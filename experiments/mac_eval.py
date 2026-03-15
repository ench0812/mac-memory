#!/usr/bin/env python3
"""
MaC S-Expression Evaluator — 最小可執行記憶引擎

把 MaC 的 S-expression 規則變成真正可執行的程式。
輸入：情境描述（JSON）+ 規則檔案
輸出：哪些規則被觸發、建議的行為模式、complexity score

v2 (2026-03-13): 加入 complexity_score 兩軸結構
  - 認知負荷軸 (cognitive): depth + sentiment
  - 上下文壓力軸 (pressure): task_steps + turns_today
  - 取 max 決定 complexity_score
  - dual_mid flag 觀測兩軸同時中等的 case
  - 可選 --rules-dir 根據 score 動態載入 rules-minimal/rules-full

v3 (2026-03-13): 加入 intensity metadata 層
  - 從訊息結構特徵自動推算 intensity (low/mid/high)
  - 主信號：標點密度 + 回覆間隔
  - 修正項：長度極端值 (< 5 字或 > 200 字)
  - caller 傳 message_text + message_ts + last_message_ts，引擎自算
  - intensity 注入 context 供規則使用
  - 第一週閾值為拍腦袋值，一週後用 log 數據校正

用法：
  python3 mac_eval.py --context '{"sentiment":"frustrated","gap_hours":0}' --rules rules.lisp
  python3 mac_eval.py --context '{"sentiment":"excited","turns_today":15,"depth":"deep"}' --rules rules.lisp
  python3 mac_eval.py --context '{"sentiment":"neutral","task_steps":5}' --rules-dir ./rules/ --threshold 3
  echo '{"sentiment":"frustrated"}' | python3 mac_eval.py --rules rules.lisp
"""

import json
import os
import re
import sys
import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


# ============================================================
# S-Expression Parser
# ============================================================

def tokenize(source: str) -> list[str]:
    """將 S-expression 源碼轉換為 token 列表。"""
    # 移除註釋
    source = re.sub(r';[^\n]*', '', source)
    # 加空格讓括號分離
    source = source.replace('(', ' ( ').replace(')', ' ) ')
    return source.split()


def parse(tokens: list[str]) -> list:
    """從 token 列表建構巢狀 list 結構。"""
    result = []
    while tokens:
        token = tokens.pop(0)
        if token == '(':
            result.append(parse(tokens))
        elif token == ')':
            return result
        elif token.startswith('"') and token.endswith('"'):
            result.append(token[1:-1])
        elif token.startswith("'"):
            # 引用列表 '(a b c) → 直接保留
            if tokens and tokens[0] == '(':
                tokens.pop(0)  # consume '('
                quoted = parse(tokens)
                result.append(quoted)
            else:
                result.append(token[1:] if len(token) > 1 else token)
        else:
            # 嘗試數字
            try:
                result.append(int(token))
            except ValueError:
                try:
                    result.append(float(token))
                except ValueError:
                    result.append(token)
    return result


def parse_source(source: str) -> list:
    """解析 S-expression 源碼。"""
    tokens = tokenize(source)
    return parse(tokens)


# ============================================================
# MaC Rule Engine
# ============================================================

@dataclass
class Rule:
    """一條 MaC 規則。"""
    name: str
    description: str = ""
    conditions: list = field(default_factory=list)  # (when ...) 條件
    suppress: list = field(default_factory=list)     # 禁止的行為
    use: list = field(default_factory=list)          # 建議的行為
    sequence: list = field(default_factory=list)     # 回應序列
    max_length: str = ""                              # 長度限制
    match_energy: str = ""                            # 能量匹配


@dataclass
class EvalResult:
    """規則求值結果。"""
    triggered: list = field(default_factory=list)     # 觸發的規則名稱
    suppressed: list = field(default_factory=list)    # 所有被禁止的行為
    suggested: list = field(default_factory=list)     # 所有建議的行為
    sequences: list = field(default_factory=list)     # 回應序列
    constraints: dict = field(default_factory=dict)   # 其他約束
    details: list = field(default_factory=list)       # 每條規則的詳細觸發資訊


def extract_rules(parsed: list) -> list[Rule]:
    """從解析後的 S-expression 提取規則。"""
    rules = []
    for expr in parsed:
        if not isinstance(expr, list) or len(expr) < 3:
            continue
        if expr[0] not in ('rule', 'shortcut'):
            continue

        rule = Rule(name=str(expr[1]))

        # 第三個元素是描述字串
        if len(expr) > 2 and isinstance(expr[2], str):
            rule.description = expr[2]
            body_start = 3
        else:
            body_start = 2

        # 解析 body
        for item in expr[body_start:]:
            if not isinstance(item, list) or not item:
                continue

            head = item[0]
            args = item[1:]

            if head == 'when':
                rule.conditions = args
            elif head == 'suppress':
                rule.suppress = [str(a) for a in args]
            elif head == 'use':
                rule.use = [str(a) for a in args]
            elif head == 'sequence':
                rule.sequence = [str(a) for a in args]
            elif head == 'max-length':
                rule.max_length = str(args[0]) if args else ""
            elif head == 'match-energy':
                rule.match_energy = str(args[0]) if args else ""
            elif head == 'action':
                rule.use = [str(a) for a in args]
            elif head == 'transform':
                rule.use = [str(a) for a in args]

        rules.append(rule)

    return rules


def eval_condition(cond: list, context: dict) -> bool:
    """求值一個條件表達式。

    支援的運算：
      (eq key value)        — context[key] == value
      (not (expr))          — 邏輯非
      (and expr1 expr2 ...) — 邏輯與
      (or expr1 expr2 ...)  — 邏輯或
      (> key value)         — context[key] > value
      (< key value)         — context[key] < value
      (member key list)     — context[key] in list
      (ask-for what)        — context 中有 ask_for == what
      (recent-correction < time) — context[recent_correction_minutes] < time
    """
    if not isinstance(cond, list) or not cond:
        return True  # 空條件 = 永遠觸發

    op = str(cond[0])

    if op == 'and':
        return all(eval_condition(c, context) for c in cond[1:])
    elif op == 'or':
        return any(eval_condition(c, context) for c in cond[1:])
    elif op == 'not':
        return not eval_condition(cond[1], context) if len(cond) > 1 else False
    elif op == 'eq':
        key = str(cond[1])
        expected = str(cond[2]) if len(cond) > 2 else ""
        return str(context.get(key, "")) == expected
    elif op == '>':
        key = str(cond[1])
        threshold = cond[2] if len(cond) > 2 else 0
        try:
            return float(context.get(key, 0)) > float(threshold)
        except (ValueError, TypeError):
            return False
    elif op == '<':
        key = str(cond[1])
        threshold = cond[2] if len(cond) > 2 else 0
        try:
            return float(context.get(key, 0)) < float(threshold)
        except (ValueError, TypeError):
            return False
    elif op == 'member':
        key = str(cond[1])
        allowed = cond[2] if isinstance(cond[2], list) else [cond[2]]
        return str(context.get(key, "")) in [str(a) for a in allowed]
    elif op == 'ask-for':
        what = str(cond[1]) if len(cond) > 1 else ""
        return context.get("ask_for") == what
    elif op == 'recent-correction':
        # (recent-correction < 1h) → context[recent_correction_minutes] < 60
        if len(cond) >= 3 and str(cond[1]) == '<':
            threshold_str = str(cond[2])
            if threshold_str.endswith('h'):
                threshold_min = float(threshold_str[:-1]) * 60
            elif threshold_str.endswith('m'):
                threshold_min = float(threshold_str[:-1])
            else:
                threshold_min = float(threshold_str)
            return float(context.get("recent_correction_minutes", 9999)) < threshold_min
        return False
    elif op == 'intent':
        return context.get("intent") == str(cond[1]) if len(cond) > 1 else False

    # 未知運算 → 不觸發
    return False


def evaluate(rules: list[Rule], context: dict) -> EvalResult:
    """對所有規則求值，返回觸發結果。"""
    result = EvalResult()

    for rule in rules:
        # 如果沒有條件，規則永遠生效（作為 default）
        if not rule.conditions:
            triggered = True
        else:
            # conditions 是 (when ...) 裡面的內容
            # 如果只有一個條件且是 list，直接求值
            if len(rule.conditions) == 1 and isinstance(rule.conditions[0], list):
                triggered = eval_condition(rule.conditions[0], context)
            elif len(rule.conditions) == 1:
                # 單一條件可能是 (eq x y) 被攤平了
                triggered = eval_condition(rule.conditions, context)
            else:
                # 多個條件，隱含 AND
                triggered = eval_condition(['and'] + rule.conditions, context)

        if triggered:
            detail = {
                "rule": rule.name,
                "description": rule.description,
            }
            result.triggered.append(rule.name)

            if rule.suppress:
                result.suppressed.extend(rule.suppress)
                detail["suppress"] = rule.suppress
            if rule.use:
                result.suggested.extend(rule.use)
                detail["use"] = rule.use
            if rule.sequence:
                result.sequences.append({"rule": rule.name, "steps": rule.sequence})
                detail["sequence"] = rule.sequence
            if rule.max_length:
                result.constraints["max_length"] = rule.max_length
            if rule.match_energy:
                result.constraints["match_energy"] = rule.match_energy

            result.details.append(detail)

    return result


# ============================================================
# Complexity Score — 兩軸 max 結構
# ============================================================
# 認知負荷 (cognitive): depth + sentiment 的「質」
# 上下文壓力 (pressure): task_steps + turns_today 的「量」
# 第一週：所有因子權重 = 1，純記錄原始信號

# Depth 映射（權重 1）
DEPTH_SCORES = {
    "shallow": 0,
    "casual": 0,
    "moderate": 1,
    "analytical": 2,
    "deep": 3,
    "philosophical": 3,
}

# Sentiment 映射（權重 1，非 neutral 就 +1）
SENTIMENT_SCORES = {
    "neutral": 0,
    "curious": 1,
    "excited": 1,
    "frustrated": 1,
    "sad": 1,
}


def compute_complexity(context: dict) -> dict:
    """計算 complexity score，返回兩軸分數 + max + dual_mid flag。

    兩軸：
      cognitive = depth_score + sentiment_score
      pressure  = task_step_score + turns_score

    complexity_score = max(cognitive, pressure)
    dual_mid = 兩軸都 >= threshold * 0.6（觀測用，第一週不影響行為）

    第一週權重全 1，純記錄原始信號。
    """
    # --- 認知負荷軸 ---
    depth = str(context.get("depth", "shallow")).lower()
    sentiment = str(context.get("sentiment", "neutral")).lower()

    depth_score = DEPTH_SCORES.get(depth, 0)
    sentiment_score = SENTIMENT_SCORES.get(sentiment, 0)
    cognitive = depth_score + sentiment_score  # max possible: 4

    # --- 上下文壓力軸 ---
    task_steps = int(context.get("task_steps", 0))
    turns_today = int(context.get("turns_today", 0))

    # 權重 1，直接用 clamp 到合理範圍
    task_score = min(task_steps, 4)   # cap at 4
    turns_score = 1 if turns_today > 10 else 0  # binary: 是否高輪次
    pressure = task_score + turns_score  # max possible: 5

    # --- 取 max ---
    complexity_score = max(cognitive, pressure)

    # --- dual_mid flag（觀測用）---
    # 預設閾值 5，0.6 × 5 = 3
    mid_threshold = 3
    dual_mid = cognitive >= mid_threshold and pressure >= mid_threshold

    return {
        "complexity_score": complexity_score,
        "cognitive": cognitive,
        "pressure": pressure,
        "dual_mid": dual_mid,
        "breakdown": {
            "depth_score": depth_score,
            "sentiment_score": sentiment_score,
            "task_score": task_score,
            "turns_score": turns_score,
        },
    }


def log_complexity(context: dict, complexity: dict, rules_file: str,
                   log_dir: str = None, source: str = "unknown",
                   outcome: str = "pending", note: str = "",
                   intensity: dict = None):
    """寫一行 JSONL log，用於一週後校準閾值。
    
    Args:
        source: heartbeat|dialogue|chat — 觸發來源
        outcome: pending|ok|off|overcorrect — 預設 pending，每日回顧回填
        note: 人工備註（回填時補充）
        intensity: compute_intensity() 的回傳值
    """
    if log_dir is None:
        log_dir = str(Path(__file__).parent / "logs")
    os.makedirs(log_dir, exist_ok=True)

    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz)
    log_file = os.path.join(log_dir, f"complexity-{now.strftime('%Y-%m-%d')}.jsonl")

    entry = {
        "ts": now.isoformat(),
        "source": source,
        "context": context,
        "complexity": complexity,
        "rules_file": rules_file,
        "outcome": outcome,
        "note": note,
    }
    if intensity is not None:
        entry["intensity"] = intensity

    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ============================================================
# Intensity Metadata — 純結構信號，不依賴 caller 主觀判斷
# ============================================================
# 主信號：標點密度 + 回覆間隔
# 修正項：長度極端值（U 型：極短/極長 = +1）
# 總分 0 = low, 1 = mid, 2-3 = high
# 第一週閾值：拍腦袋值，一週後用實際分佈校正

# 情緒標點集合
INTENSITY_PUNCTUATION = set('!?！？…⋯')


def compute_intensity(context: dict) -> dict | None:
    """從訊息 metadata 推算 intensity，回傳分數 + 分級 + 各信號細節。

    若沒有 message_text（如 heartbeat），回傳 None。
    Heartbeat 不產生訊息，intensity 不適用。

    context 可選欄位：
      message_text: str — 原始訊息文本（必要，無則 return None）
      message_ts: float/str — 本則訊息 timestamp (ISO or epoch)
      last_message_ts: float/str — 上一則訊息 timestamp
    
    三信號：
      1. punctuation_density: 情緒標點數 / 總字數，> 0.2 = +1
      2. reply_interval_sec: 回覆間隔秒數，< 10 = +1
      3. length_modifier: 字數 < 5 或 > 200 = +1（U 型修正）
    """
    text = context.get("message_text")
    if not text:
        return None
    
    # --- 信號 1: 標點密度 ---
    char_count = len(text) if text else 0
    if char_count > 0:
        punct_count = sum(1 for c in text if c in INTENSITY_PUNCTUATION)
        punctuation_density = punct_count / char_count
    else:
        punct_count = 0
        punctuation_density = 0.0
    punct_signal = 1 if punctuation_density > 0.2 else 0

    # --- 信號 2: 回覆間隔 ---
    interval_sec = _compute_interval(context)
    interval_signal = 1 if (interval_sec is not None and interval_sec < 10) else 0

    # --- 信號 3: 長度修正（U 型）---
    length_modifier = 1 if (char_count > 0 and (char_count < 5 or char_count > 200)) else 0

    # --- 總分 → 分級 ---
    total = punct_signal + interval_signal + length_modifier
    if total >= 2:
        level = "high"
    elif total == 1:
        level = "mid"
    else:
        level = "low"

    return {
        "intensity": level,
        "intensity_score": total,
        "signals": {
            "punctuation_density": round(punctuation_density, 3),
            "punct_count": punct_count,
            "char_count": char_count,
            "punct_signal": punct_signal,
            "reply_interval_sec": interval_sec,
            "interval_signal": interval_signal,
            "length_modifier": length_modifier,
        },
    }


def _compute_interval(context: dict) -> float | None:
    """計算回覆間隔（秒），支援 ISO 字串和 epoch float。"""
    msg_ts = context.get("message_ts")
    last_ts = context.get("last_message_ts")
    
    if msg_ts is None or last_ts is None:
        return None
    
    try:
        t1 = _parse_ts(msg_ts)
        t2 = _parse_ts(last_ts)
        diff = abs((t1 - t2).total_seconds())
        return round(diff, 1)
    except (ValueError, TypeError, OSError):
        return None


def _parse_ts(ts) -> datetime:
    """將 timestamp 轉為 datetime，支援 ISO 和 epoch。"""
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    if isinstance(ts, str):
        # 嘗試 ISO 格式
        try:
            return datetime.fromisoformat(ts)
        except ValueError:
            pass
        # 嘗試 epoch 字串
        return datetime.fromtimestamp(float(ts), tz=timezone.utc)
    raise ValueError(f"無法解析 timestamp: {ts}")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="MaC S-Expression Evaluator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--rules", help="S-expression 規則檔案路徑（固定）")
    group.add_argument("--rules-dir", help="規則目錄（含 rules-minimal.lisp + rules-full.lisp，根據 complexity 動態選擇）")
    parser.add_argument("--threshold", type=int, default=3,
                        help="complexity 閾值：< threshold 載 minimal，>= 載 full（預設 3）")
    parser.add_argument("--context", default=None, help="情境 JSON 字串")
    parser.add_argument("--context-file", default=None, help="情境 JSON 檔案")
    parser.add_argument("--source", default=None, choices=["heartbeat", "dialogue", "chat"],
                        help="觸發來源（寫入 log 的 source 欄位）")
    parser.add_argument("--verbose", "-v", action="store_true", help="顯示詳細資訊")
    parser.add_argument("--no-log", action="store_true", help="不寫 complexity log")
    args = parser.parse_args()

    # 讀取情境
    if args.context:
        context = json.loads(args.context)
    elif args.context_file:
        with open(args.context_file) as f:
            context = json.load(f)
    elif not sys.stdin.isatty():
        context = json.load(sys.stdin)
    else:
        context = {}

    # 計算 intensity（從訊息 metadata 自動推算；無 message_text 則 None）
    intensity = compute_intensity(context)
    # 有 intensity 時才注入 context 讓規則可以吃
    if intensity is not None and "intensity" not in context:
        context["intensity"] = intensity["intensity"]

    # 計算 complexity score
    complexity = compute_complexity(context)

    # 決定規則檔案
    if args.rules_dir:
        rules_dir = Path(args.rules_dir)
        if complexity["complexity_score"] < args.threshold:
            rules_path = rules_dir / "rules-minimal.lisp"
        else:
            rules_path = rules_dir / "rules-full.lisp"
        # fallback: 如果選中的檔案不存在，用另一個
        if not rules_path.exists():
            fallback = rules_dir / "rules.lisp"
            if fallback.exists():
                rules_path = fallback
            else:
                print(f"❌ 找不到規則檔案: {rules_path}", file=sys.stderr)
                return 1
        rules_file = str(rules_path)
    else:
        rules_file = args.rules

    # 讀取規則
    with open(rules_file) as f:
        rules_source = f.read()

    parsed = parse_source(rules_source)
    rules = extract_rules(parsed)

    if args.verbose:
        print(f"📋 載入 {len(rules)} 條規則 ({rules_file})")
        print(f"📎 情境: {json.dumps(context, ensure_ascii=False)}")
        print(f"📊 complexity: {complexity['complexity_score']} "
              f"(cognitive={complexity['cognitive']}, pressure={complexity['pressure']}, "
              f"dual_mid={complexity['dual_mid']})")
        if intensity is not None:
            print(f"🔥 intensity: {intensity['intensity']} "
                  f"(score={intensity['intensity_score']}, "
                  f"punct={intensity['signals']['punct_signal']}, "
                  f"interval={intensity['signals']['interval_signal']}, "
                  f"length={intensity['signals']['length_modifier']})")
        else:
            print(f"🔥 intensity: null (no message_text)")
        print()

    # 求值
    result = evaluate(rules, context)

    # 寫 log（除非 --no-log）
    if not args.no_log:
        log_source = args.source or context.get("source", "unknown")
        log_complexity(context, complexity, rules_file, source=log_source,
                       intensity=intensity)

    # 輸出
    output = {
        "triggered_rules": result.triggered,
        "suppressed_behaviors": list(set(result.suppressed)),
        "suggested_behaviors": list(set(result.suggested)),
        "sequences": result.sequences,
        "constraints": result.constraints,
        "complexity": complexity,
        "intensity": intensity,
        "rules_file": os.path.basename(rules_file),
    }

    if args.verbose:
        output["details"] = result.details

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
