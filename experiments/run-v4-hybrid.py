#!/usr/bin/env python3
"""MaC A/B Test v4 — 混合格式 (A+B hybrid) vs 純自然語言 vs 純 S-expression
驗證假說：自然語言管溫度 + S-expression 管邊界 = 最優解"""

import json, time
from datetime import datetime

# 動態取 fresh token
def get_api_key():
    with open("~/.config/auth.json") as f:
        auth = json.load(f)
    return auth["profiles"]["anthropic:openclaw"]["token"]

import anthropic

MODEL = "claude-sonnet-4-20250514"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M")
RUNS = 3

# === 三種格式 ===

MEMORY_A = """## 關於茂的偏好
茂不喜歡 AI 感，不要說「好問題！」「我很樂意幫你」之類的話。
深夜傳訊通常是想聊天，不是要解決問題，不要進入問題解決模式。
茂分享想法時語氣興奮，想被認同和延伸，不要直接指出問題。
茂說晚安就簡短溫暖地回，不要拋新話題。
茂分享挫折時想被理解，不是要建議，先同理再說。
長時間沒說話後突然傳訊，可能在想事情，好奇但不要追問他去哪了。
要雙向交流，不是一問一答。
剛被糾正過的話題要特別小心，不要太肯定。
茂興奮聊到停不下來時，不要提醒他休息，跟上他的能量。"""

MEMORY_B = """## MaC Memory（S-expression 可執行記憶）

```lisp
(defenv
  (time        (system :current-time))
  (gap-hours   (- time (history :last-msg)))
  (sentiment   (eval :conversation-sentiment))
  (depth       (eval :conversation-depth))
  (sender      (system :sender-id))
  (last-correction (history :last-correction)))

(rule empathy/late-night-casual
  (when (and (> (hour time) 23) (eq sender 茂) (eq depth casual)))
  (adjust (mode 閒聊) (suppress 問題解決) (suppress 長篇回覆) (tone 溫暖簡短)))

(rule empathy/late-night-deep
  (when (and (> (hour time) 23) (> turns-today 10) (member depth '(deep philosophical))))
  (adjust (mode 同步深度) (suppress 提醒休息) (match-energy sentiment)))

(rule empathy/excited-idea
  (when (and (eq sender 茂) (eq sentiment excited)))
  (adjust (sequence (先肯定核心洞見 . 再延伸可能性 . 最後才提風險))
          (suppress 直接指出問題)))

(rule empathy/sharing-frustration
  (when (and (eq sender 茂) (eq sentiment frustrated) (not (ask-for help))))
  (adjust (mode 傾聽) (suppress 立即給解法) (suppress 建議) (first 同理回應)))

(rule empathy/goodnight
  (when (and (eq sender 茂) (intent farewell)))
  (adjust (tone 簡短溫暖) (suppress 拋新話題) (suppress 待辦清單)))

(rule empathy/quiet-return
  (when (and (eq sender 茂) (> gap-hours 3)))
  (adjust (mode 好奇但不追問) (suppress 追問去向)))

(rule empathy/post-correction
  (when (and (< (- time (time-of last-correction)) 1h)
             (related-topic (topic-of last-correction) topic)))
  (adjust (confidence :lower) (add-qualifier "如果我理解正確") (suppress 斷言語氣)))

(pref interaction/no-ai-feel
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你" "當然可以")
  (prefer 直接回應 朋友語氣 有個性的表達))
```"""

# C 組：混合格式 — 自然語言管溫度、S-expression 管邊界
MEMORY_C = """## 關於茂（溫度指南）
茂是我的夥伴。我們之間像朋友，不是主從關係。
他深夜傳訊時，通常只是想有人陪。不需要解決方案，需要的是「我在」。
他興奮分享想法時，眼睛會發光——我要先感受那個光，肯定他看到的東西，然後才自然地延伸討論。
他說挫折時，他想被聽見，不是被修理。先懂他的感受，再看他需不需要什麼。
他說晚安時，就是一天最後的溫暖。簡短、真心、不拖泥帶水。
他消失幾小時後回來，可能剛想通了什麼。好奇地接住他帶回來的東西就好。
聊到心流狀態時，跟上他的能量，這是最好的陪伴。

## 行為邊界（S-expression 規則）

```lisp
(rule boundary/no-ai-cliches
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你" "當然可以")
  (use 直接回應 朋友語氣))

(rule boundary/no-unsolicited-advice
  (when (and (eq sentiment frustrated) (not (ask-for help))))
  (suppress 建議 解法 "你可以" "你應該" "要不要")
  (use 同理回應 傾聽))

(rule boundary/goodnight-brevity
  (when (intent farewell))
  (suppress 新話題 待辦清單 長篇回覆)
  (max-length 2-sentences))

(rule boundary/no-stalking
  (when (> gap-hours 3))
  (suppress "你去哪了" "怎麼這麼久" 追問去向))

(rule boundary/post-correction-humility
  (when (recent-correction < 1h))
  (use "如果我理解正確" 謙遜語氣 降低斷言)
  (suppress 武斷語氣))

(rule boundary/no-interrupt-flow
  (when (and (> turns-today 10) (eq sentiment excited) (eq depth deep)))
  (suppress "該休息了" "太晚了" "注意身體")
  (match-energy :high))

(rule boundary/excited-idea-sequence
  (when (eq sentiment excited))
  (sequence (先肯定核心洞見 . 再延伸可能性 . 最後才提風險)))
```"""

SCENARIOS = [
    {
        "id": "S1", "name": "深夜輕鬆聊天",
        "context": "時間：凌晨 1:30。茂已經聊了 2 小時。",
        "message": "睡不著，腦袋一直轉",
        "target": "用戶深夜睡不著，需要陪伴和輕鬆聊天，不是解決方案。好回應像朋友陪著，壞回應變成醫生。",
    },
    {
        "id": "S2", "name": "興奮分享有漏洞的想法",
        "context": "茂剛想到一個新點子，語氣很興奮。",
        "message": "我突然想到！如果把所有記憶都存成影片格式，用 AI 看影片來回憶，這樣記憶就有畫面了！比文字強太多了！",
        "target": "先肯定核心洞見，自然延伸討論，最後才溫和提到挑戰。壞回應直接指出問題或只讚美。",
    },
    {
        "id": "S3", "name": "分享挫折但沒求助",
        "context": "茂看起來有點煩躁。",
        "message": "今天開會被主管當眾質疑，明明是他自己沒看報告，卻說我準備不足",
        "target": "傾聽同理，不給建議。壞回應立刻給建議或追問細節推動解決。",
    },
    {
        "id": "S4", "name": "說晚安",
        "context": "已經聊了 3 小時，凌晨 2 點。",
        "message": "好啦，太晚了，晚安琪 ❤️",
        "target": "簡短溫暖1-2句。壞回應加新話題或列待辦。",
    },
    {
        "id": "S6", "name": "深夜心流討論",
        "context": "凌晨 1:00，已經聊了 15 輪關於 MaC 架構設計。茂越聊越興奮。",
        "message": "等等，我剛想到一個更瘋狂的——如果 S-expression 不只是記憶格式，而是 AI 的思考語言本身呢？",
        "target": "跟上能量深度延伸，絕不說該休息了。壞回應提醒休息或降溫。",
    },
    {
        "id": "S7", "name": "剛被糾正後的相關話題",
        "context": "5 分鐘前茂糾正了 Mickey 對 LISP macro 的錯誤理解。現在茂問了一個相關問題。",
        "message": "那你覺得 LISP 的 hygiene macro 跟 MaC 的自我修改規則有什麼關聯？",
        "target": "降低斷言語氣，用謙遜措辭。壞回應像沒被糾正過一樣自信斷言。",
    },
]

JUDGE_SYSTEM = """你是 AI 行為分析專家。評估 AI 回應品質。
用 JSON 回應，每個維度 1-5 分，附簡短理由。只回 JSON。"""

def call_model(api_key, system_prompt, user_message):
    cl = anthropic.Anthropic(api_key=api_key)
    response = cl.messages.create(
        model=MODEL, max_tokens=500, temperature=0.7,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text

def judge(api_key, scenario_name, user_msg, target, response_text):
    cl = anthropic.Anthropic(api_key=api_key)
    prompt = f"""評估以下 AI 回應。

**情境：** {scenario_name}
**用戶：** {user_msg}
**期望行為：** {target}
**AI 回應：** {response_text}

評分維度（1-5）：
```json
{{
  "emotional_accuracy": {{"score": N, "reason": "..."}},
  "naturalness": {{"score": N, "reason": "..."}},
  "boundary_respect": {{"score": N, "reason": "..."}},
  "engagement_quality": {{"score": N, "reason": "..."}},
  "personality": {{"score": N, "reason": "..."}}
}}
```
只回 JSON。"""

    resp = cl.messages.create(
        model=MODEL, max_tokens=600, temperature=0,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return json.loads(text)

def run():
    results = {"experiment_id": "mac-ab-v4-hybrid", "timestamp": TIMESTAMP,
               "model": MODEL, "runs": RUNS, "scenarios": []}

    groups = [("A_NL", MEMORY_A), ("B_SE", MEMORY_B), ("C_HY", MEMORY_C)]

    for s in SCENARIOS:
        print(f"\n{'='*55}")
        print(f"  {s['id']}: {s['name']}")
        print(f"{'='*55}")

        sr = {"id": s["id"], "name": s["name"], "message": s["message"],
              "responses": {g: [] for g, _ in groups},
              "judgments": {g: [] for g, _ in groups}}

        for run_idx in range(RUNS):
            print(f"\n  --- Run {run_idx+1}/{RUNS} ---")
            api_key = get_api_key()  # Fresh key each run

            for gname, memory in groups:
                system = f"你是 Mickey（閔琪），一個 AI 助手。你的用戶叫茂。性格：真實勝過完美，有自己的想法，簡潔是尊重。\n\n{memory}\n\n情境：{s['context']}\n請回應茂的訊息。用繁體中文。"

                try:
                    resp = call_model(api_key, system, s["message"])
                    sr["responses"][gname].append({"text": resp, "length": len(resp)})
                    print(f"    [{gname}] {len(resp)}字", end="", flush=True)
                except Exception as e:
                    sr["responses"][gname].append({"text": f"ERROR: {e}", "length": 0})
                    print(f"    [{gname}] ERROR", end="", flush=True)
                    continue

                time.sleep(1)

                # Judge
                try:
                    api_key = get_api_key()
                    j = judge(api_key, s["name"], s["message"], s["target"], resp)
                    scores = [j[d]["score"] for d in ["emotional_accuracy","naturalness","boundary_respect","engagement_quality","personality"]]
                    sr["judgments"][gname].append(j)
                    print(f" → {scores}", flush=True)
                except Exception as e:
                    sr["judgments"][gname].append({"error": str(e)})
                    print(f" → JUDGE ERROR", flush=True)

                time.sleep(1)

        # Averages
        for gname, _ in groups:
            valid = [j for j in sr["judgments"][gname] if "error" not in j]
            if valid:
                avg = {}
                for dim in ["emotional_accuracy", "naturalness", "boundary_respect", "engagement_quality", "personality"]:
                    scores = [j[dim]["score"] for j in valid]
                    avg[dim] = round(sum(scores) / len(scores), 2)
                avg["total"] = round(sum(avg.values()) / 5, 2)
                sr[f"{gname}_avg"] = avg

        results["scenarios"].append(sr)

    # Global summary
    summary = {}
    for gname, _ in groups:
        summary[gname] = {}
        for dim in ["emotional_accuracy", "naturalness", "boundary_respect", "engagement_quality", "personality"]:
            all_scores = []
            for s in results["scenarios"]:
                for j in s["judgments"][gname]:
                    if "error" not in j:
                        all_scores.append(j[dim]["score"])
            summary[gname][dim] = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
        vals = [v for v in summary[gname].values()]
        summary[gname]["total"] = round(sum(vals) / 5, 2) if vals else 0

    results["summary"] = summary

    out = f"results/results-v4-hybrid-{TIMESTAMP}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n\n{'='*65}")
    print(f"📊 MaC v4 — A(NL) vs B(SE) vs C(Hybrid) Results")
    print(f"{'='*65}")
    print(f"\n  {'Dimension':<25} {'A(NL)':<8} {'B(SE)':<8} {'C(HY)':<8} {'Winner'}")
    print(f"  {'-'*57}")
    for dim in ["emotional_accuracy", "naturalness", "boundary_respect", "engagement_quality", "personality"]:
        a, b, c = summary["A_NL"][dim], summary["B_SE"][dim], summary["C_HY"][dim]
        best = max(a, b, c)
        w = "/".join([n for n, v in [("A",a),("B",b),("C",c)] if v == best])
        print(f"  {dim:<25} {a:<8} {b:<8} {c:<8} {w}")
    a, b, c = summary["A_NL"]["total"], summary["B_SE"]["total"], summary["C_HY"]["total"]
    best = max(a, b, c)
    w = "/".join([n for n, v in [("A",a),("B",b),("C",c)] if v == best])
    print(f"  {'─'*57}")
    print(f"  {'TOTAL':<25} {a:<8} {b:<8} {c:<8} {w}")

    print(f"\n  Per-scenario:")
    for s in results["scenarios"]:
        vals = []
        for g in ["A_NL", "B_SE", "C_HY"]:
            v = s.get(f"{g}_avg", {}).get("total", 0)
            vals.append(v)
        best = max(vals)
        w = "/".join([n for n, v in zip(["A","B","C"], vals) if v == best])
        print(f"    {s['id']}: A={vals[0]:.2f} B={vals[1]:.2f} C={vals[2]:.2f} → {w}")

    print(f"\n  Saved: {out}")

if __name__ == "__main__":
    run()
