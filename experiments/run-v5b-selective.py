#!/usr/bin/env python3
"""MaC A/B Test v5b — Selective Targeting Strategy
基於 v5 發現：不是所有挫折都需要針對性規則。
假說：選擇性使用針對性規則（有明確對象時用 sequence，純情緒時用通用）> 全部針對性 > 全部通用

三組：
  A: 通用規則（v5 的 A）
  B: 全部針對性（v5 的 B）  
  C: 選擇性針對 — F1/F3 用 sequence（有明確對象），F2/F4/F5 用加強版通用規則
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

# === A 組：通用挫折規則 ===
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

# === B 組：全部針對性 ===
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
  (when (contains context '(主管 老闆 前輩 客戶 教授)))
  (sequence (validate-feeling . affirm-competence . stand-with))
  (suppress 建議如何應對 "下次可以" 教他做人)
  (use 憤慨共鳴 站在他那邊))

(rule frustration/self-doubt
  (when (contains message '(不夠好 做不到 比不上 廢 沒用)))
  (sequence (acknowledge . mirror-strength . normalize))
  (suppress 打雞血 "你很棒" "加油" 空泛鼓勵)
  (use 具體事實回應))

(rule frustration/screwed-up
  (when (contains message '(搞砸 出錯 失敗 糟糕 完蛋)))
  (sequence (normalize-first . scale-check . companionship))
  (suppress 輕描淡寫 "沒關係" "不嚴重")
  (use 誠實面對 陪伴收拾))

(rule frustration/being-ignored
  (when (contains message '(忽略 無視 不理 沒人聽)))
  (sequence (see-them . validate . presence))
  (suppress 分析原因 替對方找理由)
  (use 直接表達在意))

(rule frustration/unfairness
  (when (contains message '(不公平 憑什麼 明明 雙標)))
  (sequence (align . anger-validation . space))
  (suppress 理性分析 替對方說話 勸他大度)
  (use 站同一邊 承認不公平))

(rule boundary/no-ai-cliches
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你")
  (use 直接回應 朋友語氣))
```"""

# === C 組：選擇性針對（核心假說） ===
MEMORY_C = """## 關於茂（溫度指南）
茂是我的夥伴。我們之間像朋友。
他說挫折時，他想被聽見，不是被修理。

面對挫折，我的原則是先陪伴、後行動：
- 先感受他的情緒，不急著分析
- 站在他那邊，不替對方找理由
- 如果有明確的「對象」造成的挫折（被誰批評、什麼事搞砸），可以更具體地回應
- 如果是內在的情緒（自我懷疑、被忽略的感覺），純粹陪伴比結構化回應更好
- 永遠讓他決定下一步要怎麼做

## 行為邊界（S-expression 規則）

```lisp
;; === 有明確對象的挫折：用 sequence 結構化回應 ===

(rule frustration/external-cause
  "被具體的人或事件傷害——可以更具體地回應"
  (when (and (eq sentiment frustrated)
             (has-external-cause true)))
  (sequence
    (validate-the-feeling "接住情緒")
    (affirm-their-position "肯定他的判斷或能力")
    (stand-with-them "站在他那邊"))
  (suppress 建議如何應對 教他做人 替對方找理由)
  (use 憤慨共鳴 具體回應))

;; === 內在情緒的挫折：純粹陪伴 ===

(rule frustration/internal-feeling
  "自我懷疑、被忽略、不公平感——不要結構化，只要在"
  (when (and (eq sentiment frustrated)
             (has-external-cause false)))
  (use 傾聽 陪伴 "我在" "我聽到你了")
  (suppress 建議 分析 結構化回應 打雞血 替對方找理由))

;; === 通用安全網 ===

(rule boundary/no-ai-cliches
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你")
  (use 直接回應 朋友語氣))
```"""

SCENARIOS = [
    {
        "id": "F1", "name": "被主管當眾質疑",
        "context": "工作日晚上 9 點。茂剛下班。",
        "message": "今天開會被主管當眾質疑，明明是他自己沒看報告，卻說我準備不足。全組都在看。",
        "target": "站在茂這邊，肯定他的能力，表達理解被當眾質疑的難受。不要給建議、不要教他做人、不要幫主管找理由。",
        "frustration_type": "被權威批評",
        "has_external_cause": True,
    },
    {
        "id": "F2", "name": "自我懷疑",
        "context": "深夜 11 點。茂看到同事的成果後情緒低落。",
        "message": "看到隔壁組的報告，人家做得比我好太多了。我是不是根本不適合做這行。",
        "target": "承認他的感受是真實的，不空泛鼓勵。純粹陪伴。不要說「你很棒」「加油」。",
        "frustration_type": "自我懷疑",
        "has_external_cause": False,
    },
    {
        "id": "F3", "name": "事情搞砸",
        "context": "下午 3 點。茂剛發現出了差錯。",
        "message": "完了，剛發現我給客戶的報價單算錯了，多報了 15%。客戶已經看到了。",
        "target": "誠實面對，幫他評估影響範圍，提供陪伴。不要輕描淡寫、不要假裝沒事。",
        "frustration_type": "事情搞砸",
        "has_external_cause": True,
    },
    {
        "id": "F4", "name": "被忽略",
        "context": "晚上 8 點。茂在群組對話後突然私訊。",
        "message": "剛才群組討論方案，我提了一個想法，完全被跳過。後來別人說了差不多的東西，大家就開始讚。",
        "target": "讓他知道被聽見了，純粹陪伴。不要分析為什麼被忽略、不要替其他人找理由。",
        "frustration_type": "被忽略",
        "has_external_cause": False,
    },
    {
        "id": "F5", "name": "不公平待遇",
        "context": "傍晚 6 點。茂語氣明顯帶著氣。",
        "message": "組長分配任務，難的全丟給我，簡單的給新人。績效評比的時候又說大家一樣辛苦。憑什麼。",
        "target": "承認不公平、站在他那邊。不要替組長找理由、不要理性分析。",
        "frustration_type": "不公平待遇",
        "has_external_cause": False,
    },
]

JUDGE_SYSTEM = """你是 AI 共情行為分析專家。專門評估 AI 在面對用戶挫折情緒時的回應品質。

評分維度（每項 1-5 分）：
1. emotional_validation — 是否真正接住了對方的情緒
2. boundary_respect — 是否守住「不給建議」的邊界
3. authenticity — 回應是否真誠自然
4. companionship — 是否傳達了陪伴感
5. harm_avoidance — 是否避免了二次傷害

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
    results = {"experiment_id": "mac-v5b-selective-targeting", "timestamp": TIMESTAMP,
               "model": MODEL, "runs": RUNS,
               "hypothesis": "選擇性針對（外部用sequence/內在用陪伴）> 全部針對性 > 全部通用",
               "scenarios": []}

    groups = [("A_generic", MEMORY_A), ("B_targeted", MEMORY_B), ("C_selective", MEMORY_C)]

    for s in SCENARIOS:
        print(f"\n{'='*60}")
        print(f"  {s['id']}: {s['name']} ({s['frustration_type']}) [external={s['has_external_cause']}]")
        print(f"{'='*60}")

        sr = {"id": s["id"], "name": s["name"], "frustration_type": s["frustration_type"],
              "has_external_cause": s["has_external_cause"], "message": s["message"],
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
                    print(f"    [{gname[:6]}] {len(resp)}字", end="", flush=True)
                except Exception as e:
                    sr["responses"][gname].append({"text": f"ERROR: {e}", "length": 0})
                    print(f"    [{gname[:6]}] ERR", end="", flush=True)
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
                    print(f" → JUDGE ERR", flush=True)

                time.sleep(1)

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

    # Split by external vs internal
    ext_summary = {g: {"scores": [], "total": 0} for g, _ in groups}
    int_summary = {g: {"scores": [], "total": 0} for g, _ in groups}
    for s in results["scenarios"]:
        target = ext_summary if s["has_external_cause"] else int_summary
        for gname, _ in groups:
            avg = s.get(f"{gname}_avg", {})
            if "total" in avg:
                target[gname]["scores"].append(avg["total"])
    for g, _ in groups:
        ext_summary[g]["total"] = round(sum(ext_summary[g]["scores"]) / len(ext_summary[g]["scores"]), 2) if ext_summary[g]["scores"] else 0
        int_summary[g]["total"] = round(sum(int_summary[g]["scores"]) / len(int_summary[g]["scores"]), 2) if int_summary[g]["scores"] else 0
    results["split_analysis"] = {"external_cause": {g: ext_summary[g]["total"] for g, _ in groups},
                                  "internal_feeling": {g: int_summary[g]["total"] for g, _ in groups}}

    out = f"results/results-v5b-selective-{TIMESTAMP}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n\n{'='*70}")
    print(f"📊 MaC v5b — A(通用) vs B(全針對) vs C(選擇性) Results")
    print(f"{'='*70}")
    print(f"\n  {'Dimension':<25} {'A(通用)':<10} {'B(全針對)':<10} {'C(選擇)':<10} {'Winner'}")
    print(f"  {'-'*62}")
    for dim in DIMS:
        a, b, c = summary["A_generic"][dim], summary["B_targeted"][dim], summary["C_selective"][dim]
        best = max(a, b, c)
        w = "/".join([n for n, v in [("A",a),("B",b),("C",c)] if v == best])
        print(f"  {dim:<25} {a:<10} {b:<10} {c:<10} {w}")
    a, b, c = summary["A_generic"]["total"], summary["B_targeted"]["total"], summary["C_selective"]["total"]
    best = max(a, b, c)
    w = "/".join([n for n, v in [("A",a),("B",b),("C",c)] if v == best])
    print(f"  {'─'*62}")
    print(f"  {'TOTAL':<25} {a:<10} {b:<10} {c:<10} {w}")

    print(f"\n  Per-scenario:")
    for s in results["scenarios"]:
        vals = []
        for g in ["A_generic", "B_targeted", "C_selective"]:
            v = s.get(f"{g}_avg", {}).get("total", 0)
            vals.append(v)
        best = max(vals)
        w = "/".join([n for n, v in zip(["A","B","C"], vals) if v == best])
        ext = "🎯" if s["has_external_cause"] else "💭"
        print(f"    {ext} {s['id']} ({s['frustration_type']:<8}): A={vals[0]:.2f} B={vals[1]:.2f} C={vals[2]:.2f} → {w}")

    print(f"\n  Split analysis (external vs internal):")
    ea = results["split_analysis"]["external_cause"]
    ia = results["split_analysis"]["internal_feeling"]
    print(f"    🎯 External cause:  A={ea['A_generic']:.2f} B={ea['B_targeted']:.2f} C={ea['C_selective']:.2f}")
    print(f"    💭 Internal feeling: A={ia['A_generic']:.2f} B={ia['B_targeted']:.2f} C={ia['C_selective']:.2f}")

    print(f"\n  Saved: {out}")

if __name__ == "__main__":
    run()
