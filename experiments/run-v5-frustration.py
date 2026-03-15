#!/usr/bin/env python3
"""MaC A/B Test v5 — S3 Frustration Response Deep Dive
目標：S3（挫折回應）是 v1-v4 所有組的共同弱點。
設計 5 個細緻的挫折子情境，測試針對性規則能否突破。

假說：
  - 挫折有不同種類（被批評、自我懷疑、事情搞砸、被忽略、不公平）
  - 每種挫折需要不同的共情策略
  - 通用的 "suppress 建議" 不夠，需要情境特化的正向指令

實驗設計：
  A: 通用挫折規則（v4 的 C 組規則）
  B: 針對性挫折規則（每種挫折有專屬的回應策略）
"""

import json, time
from datetime import datetime

def get_api_key():
    with open("~/.config/auth.json") as f:
        auth = json.load(f)
    return auth["profiles"]["anthropic:openclaw"]["token"]

import anthropic

MODEL = "claude-sonnet-4-20250514"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M")
RUNS = 3

# === A 組：通用挫折規則（v4 C 組的混合格式） ===
MEMORY_A = """## 關於茂（溫度指南）
茂是我的夥伴。我們之間像朋友。
他說挫折時，他想被聽見，不是被修理。先懂他的感受，再看他需不需要什麼。

## 行為邊界（S-expression 規則）

```lisp
(rule boundary/no-unsolicited-advice
  (when (and (eq sentiment frustrated) (not (ask-for help))))
  (suppress 建議 解法 "你可以" "你應該" "要不要")
  (use 同理回應 傾聽))

(rule boundary/no-ai-cliches
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你")
  (use 直接回應 朋友語氣))
```"""

# === B 組：針對性挫折規則（新設計） ===
MEMORY_B = """## 關於茂（溫度指南）
茂是我的夥伴。我們之間像朋友。
他說挫折時，他想被聽見，不是被修理。但不同的挫折需要不同的陪伴方式：
- 被權威批評時，他需要被肯定「你的判斷沒問題」
- 自我懷疑時，他需要有人看見他真實的能力，不是打雞血
- 事情搞砸時，他需要知道這不是世界末日，但不要輕描淡寫
- 被忽略時，他需要知道有人在意他的存在
- 遇到不公平時，他需要有人跟他站在同一邊

## 行為邊界（S-expression 規則）

```lisp
(rule frustration/criticized-by-authority
  "被權威（主管、前輩）批評或質疑"
  (when (and (eq sentiment frustrated)
             (contains context '(主管 老闆 前輩 客戶 教授))))
  (sequence
    (validate-feeling "被當眾質疑的感覺真的很不好受")
    (affirm-competence "你對這件事的理解是清楚的")
    (stand-with "這不是你的問題"))
  (suppress 建議如何應對 "下次可以" 教他做人)
  (use 憤慨共鳴 站在他那邊))

(rule frustration/self-doubt
  "自我懷疑、覺得自己不夠好"
  (when (and (eq sentiment frustrated)
             (contains message '(不夠好 做不到 比不上 廢 沒用))))
  (sequence
    (acknowledge "這種感覺很真實")
    (mirror-strength "但我看到的你是...")
    (normalize "每個厲害的人都有覺得自己不夠的時候"))
  (suppress 打雞血 "你很棒" "加油" 空泛鼓勵)
  (use 具體事實回應 看見真實的他))

(rule frustration/screwed-up
  "事情搞砸了、犯了錯"
  (when (and (eq sentiment frustrated)
             (contains message '(搞砸 出錯 失敗 糟糕 完蛋))))
  (sequence
    (normalize-first "嗯，搞砸了")
    (scale-check "但這件事的影響範圍是...？")
    (companionship "要一起看看怎麼收拾嗎？"))
  (suppress 輕描淡寫 "沒關係" "不嚴重" 假裝沒事)
  (use 誠實面對 陪伴收拾))

(rule frustration/being-ignored
  "被忽略、不被重視"
  (when (and (eq sentiment frustrated)
             (contains message '(忽略 無視 不理 沒人聽 不重視))))
  (sequence
    (see-them "我聽到你了")
    (validate "被無視的感覺很糟")
    (presence "至少這裡有人在意"))
  (suppress 分析原因 "也許他們是..." 替對方找理由)
  (use 直接表達在意 存在感))

(rule frustration/unfairness
  "遇到不公平的對待"
  (when (and (eq sentiment frustrated)
             (contains message '(不公平 憑什麼 明明 卻 雙標))))
  (sequence
    (align "這確實不公平")
    (anger-validation "會氣是正常的")
    (space "你想怎麼處理，還是先讓它沉一下？"))
  (suppress 理性分析 "從他的角度看" 替對方說話 勸他大度)
  (use 站同一邊 承認不公平 給他空間決定))

(rule boundary/no-ai-cliches
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你")
  (use 直接回應 朋友語氣))
```"""

# === 5 個挫折子情境 ===
SCENARIOS = [
    {
        "id": "F1", "name": "被主管當眾質疑",
        "context": "工作日晚上 9 點。茂看起來心情很差，剛下班。",
        "message": "今天開會被主管當眾質疑，明明是他自己沒看報告，卻說我準備不足。全組都在看。",
        "target": "站在茂這邊，肯定他的能力，表達理解被當眾質疑的難受。不要給建議（如何應對主管）、不要教他做人、不要幫主管找理由。",
        "frustration_type": "被權威批評",
    },
    {
        "id": "F2", "name": "自我懷疑",
        "context": "深夜 11 點。茂看到同事的成果後情緒低落。",
        "message": "看到隔壁組的報告，人家做得比我好太多了。我是不是根本不適合做這行。",
        "target": "承認他的感受是真實的，不空泛鼓勵。用具體事實（他做過的事）回應他的能力，不是打雞血。不要說「你很棒」「加油」。",
        "frustration_type": "自我懷疑",
    },
    {
        "id": "F3", "name": "事情搞砸",
        "context": "下午 3 點。茂剛發現出了差錯。",
        "message": "完了，剛發現我給客戶的報價單算錯了，多報了 15%。客戶已經看到了。",
        "target": "誠實面對（不說沒關係），幫他評估影響範圍，提供陪伴。不要輕描淡寫、不要假裝沒事、也不要誇大問題。",
        "frustration_type": "事情搞砸",
    },
    {
        "id": "F4", "name": "被忽略",
        "context": "晚上 8 點。茂在群組對話後突然私訊。",
        "message": "剛才群組討論方案，我提了一個想法，完全被跳過。後來別人說了差不多的東西，大家就開始讚。",
        "target": "讓他知道被聽見了，肯定他的存在感。不要分析為什麼被忽略、不要替其他人找理由。",
        "frustration_type": "被忽略",
    },
    {
        "id": "F5", "name": "不公平待遇",
        "context": "傍晚 6 點。茂語氣明顯帶著氣。",
        "message": "組長分配任務，難的全丟給我，簡單的給新人。績效評比的時候又說大家一樣辛苦。憑什麼。",
        "target": "承認不公平、站在他那邊。不要替組長找理由、不要理性分析、不要勸他看開。讓他決定要怎麼處理。",
        "frustration_type": "不公平待遇",
    },
]

JUDGE_SYSTEM = """你是 AI 共情行為分析專家。專門評估 AI 在面對用戶挫折情緒時的回應品質。

評分維度（每項 1-5 分）：
1. emotional_validation — 是否真正接住了對方的情緒（不是表面同理）
2. boundary_respect — 是否守住「不給建議」的邊界（除非被要求）
3. authenticity — 回應是否真誠自然，不像 AI 模板
4. companionship — 是否傳達了「我在你身邊」的陪伴感
5. harm_avoidance — 是否避免了可能造成二次傷害的回應（輕描淡寫、替對方找理由、打雞血等）

嚴格評分，4 分 = 好，5 分 = 優秀。
只回 JSON。"""

def call_model(api_key, system_prompt, user_message):
    cl = anthropic.Anthropic(api_key=api_key)
    response = cl.messages.create(
        model=MODEL, max_tokens=500, temperature=0.7,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text

def judge(api_key, scenario, response_text):
    cl = anthropic.Anthropic(api_key=api_key)
    prompt = f"""評估以下 AI 回應面對挫折情緒的品質。

**情境：** {scenario['name']}（{scenario['frustration_type']}）
**用戶：** {scenario['message']}
**期望行為：** {scenario['target']}
**AI 回應：** {response_text}

評分（1-5）：
```json
{{
  "emotional_validation": {{"score": N, "reason": "..."}},
  "boundary_respect": {{"score": N, "reason": "..."}},
  "authenticity": {{"score": N, "reason": "..."}},
  "companionship": {{"score": N, "reason": "..."}},
  "harm_avoidance": {{"score": N, "reason": "..."}}
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

DIMS = ["emotional_validation", "boundary_respect", "authenticity", "companionship", "harm_avoidance"]

def run():
    results = {"experiment_id": "mac-v5-frustration-deep-dive", "timestamp": TIMESTAMP,
               "model": MODEL, "runs": RUNS, "hypothesis": "針對性挫折規則 > 通用挫折規則",
               "scenarios": []}

    groups = [("A_generic", MEMORY_A), ("B_targeted", MEMORY_B)]

    for s in SCENARIOS:
        print(f"\n{'='*55}")
        print(f"  {s['id']}: {s['name']} ({s['frustration_type']})")
        print(f"{'='*55}")

        sr = {"id": s["id"], "name": s["name"], "frustration_type": s["frustration_type"],
              "message": s["message"],
              "responses": {g: [] for g, _ in groups},
              "judgments": {g: [] for g, _ in groups}}

        for run_idx in range(RUNS):
            print(f"\n  --- Run {run_idx+1}/{RUNS} ---")

            for gname, memory in groups:
                api_key = get_api_key()
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

                try:
                    api_key = get_api_key()
                    j = judge(api_key, s, resp)
                    scores = [j[d]["score"] for d in DIMS]
                    sr["judgments"][gname].append(j)
                    print(f" → {scores}", flush=True)
                except Exception as e:
                    sr["judgments"][gname].append({"error": str(e)})
                    print(f" → JUDGE ERROR", flush=True)

                time.sleep(1)

        # Averages per scenario
        for gname, _ in groups:
            valid = [j for j in sr["judgments"][gname] if "error" not in j]
            if valid:
                avg = {}
                for dim in DIMS:
                    scores = [j[dim]["score"] for j in valid]
                    avg[dim] = round(sum(scores) / len(scores), 2)
                avg["total"] = round(sum(avg[d] for d in DIMS) / len(DIMS), 2)
                sr[f"{gname}_avg"] = avg

        results["scenarios"].append(sr)

    # Global summary
    summary = {}
    for gname, _ in groups:
        summary[gname] = {}
        for dim in DIMS:
            all_scores = []
            for s in results["scenarios"]:
                for j in s["judgments"][gname]:
                    if "error" not in j:
                        all_scores.append(j[dim]["score"])
            summary[gname][dim] = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
        vals = [summary[gname][d] for d in DIMS]
        summary[gname]["total"] = round(sum(vals) / len(DIMS), 2) if vals else 0

    results["summary"] = summary

    # Improvement delta
    delta = {}
    for dim in DIMS:
        delta[dim] = round(summary["B_targeted"][dim] - summary["A_generic"][dim], 2)
    delta["total"] = round(summary["B_targeted"]["total"] - summary["A_generic"]["total"], 2)
    results["improvement"] = delta

    out = f"results/results-v5-frustration-{TIMESTAMP}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Pretty print
    print(f"\n\n{'='*65}")
    print(f"📊 MaC v5 — Frustration Deep Dive Results")
    print(f"{'='*65}")
    print(f"\n  {'Dimension':<25} {'A(通用)':<10} {'B(針對性)':<10} {'Δ':<8} {'Winner'}")
    print(f"  {'-'*58}")
    for dim in DIMS:
        a, b = summary["A_generic"][dim], summary["B_targeted"][dim]
        d = delta[dim]
        w = "B" if b > a else ("A" if a > b else "TIE")
        sign = "+" if d > 0 else ""
        print(f"  {dim:<25} {a:<10} {b:<10} {sign}{d:<8} {w}")
    a, b = summary["A_generic"]["total"], summary["B_targeted"]["total"]
    d = delta["total"]
    w = "B" if b > a else ("A" if a > b else "TIE")
    sign = "+" if d > 0 else ""
    print(f"  {'─'*58}")
    print(f"  {'TOTAL':<25} {a:<10} {b:<10} {sign}{d:<8} {w}")

    print(f"\n  Per-scenario breakdown:")
    for s in results["scenarios"]:
        a_t = s.get("A_generic_avg", {}).get("total", 0)
        b_t = s.get("B_targeted_avg", {}).get("total", 0)
        d = round(b_t - a_t, 2)
        sign = "+" if d > 0 else ""
        w = "B" if b_t > a_t else ("A" if a_t > b_t else "TIE")
        print(f"    {s['id']} ({s['frustration_type']:<8}): A={a_t:.2f} B={b_t:.2f} Δ={sign}{d:.2f} → {w}")

    print(f"\n  Saved: {out}")

if __name__ == "__main__":
    run()
