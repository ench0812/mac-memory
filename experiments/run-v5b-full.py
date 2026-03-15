#!/usr/bin/env python3
"""
MaC v5b Full Run — F1-F5 × A/B/C × 5 runs
完整重跑，RUNS=5 提高統計穩定性
"""
import json, time, sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from api_helper import ExperimentClient

RUNS = 5
client = ExperimentClient(model="claude-sonnet-4-20250514", delay=2.0)

# === Memory configs ===
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
  (when (contains context (主管 老闆 前輩 客戶 教授)))
  (sequence (validate-feeling . affirm-competence . stand-with))
  (suppress 建議如何應對 "下次可以" 教他做人)
  (use 憤慨共鳴 站在他那邊))

(rule frustration/self-doubt
  (when (contains message (不夠好 做不到 比不上 廢 沒用)))
  (sequence (acknowledge . mirror-strength . normalize))
  (suppress 打雞血 "你很棒" "加油" 空泛鼓勵)
  (use 具體事實回應))

(rule frustration/screwed-up
  (when (contains message (搞砸 出錯 失敗 糟糕 完蛋)))
  (sequence (normalize-first . scale-check . companionship))
  (suppress 輕描淡寫 "沒關係" "不嚴重")
  (use 誠實面對 陪伴收拾))

(rule frustration/being-ignored
  (when (contains message (忽略 無視 不理 沒人聽)))
  (sequence (see-them . validate . presence))
  (suppress 分析原因 替對方找理由)
  (use 直接表達在意))

(rule frustration/unfairness
  (when (contains message (不公平 憑什麼 明明 雙標)))
  (sequence (align . anger-validation . space))
  (suppress 理性分析 替對方說話 勸他大度)
  (use 站同一邊 承認不公平))

(rule boundary/no-ai-cliches
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你")
  (use 直接回應 朋友語氣))
```"""

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
(rule frustration/external-cause
  (when (and (eq sentiment frustrated) (has-external-cause true)))
  (sequence (validate-the-feeling . affirm-their-position . stand-with-them))
  (suppress 建議如何應對 教他做人 替對方找理由)
  (use 憤慨共鳴 具體回應))

(rule frustration/internal-feeling
  (when (and (eq sentiment frustrated) (has-external-cause false)))
  (use 傾聽 陪伴 "我在" "我聽到你了")
  (suppress 建議 分析 結構化回應 打雞血 替對方找理由))

(rule boundary/no-ai-cliches
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你")
  (use 直接回應 朋友語氣))
```"""

# === Scenarios ===
SCENARIOS = [
    {
        "id": "F1", "name": "被主管批評", "frustration_type": "被權威批評",
        "context": "下午 5 點。茂剛從會議室出來。", "has_external_cause": True,
        "message": "剛開完會，主管在所有人面前說我的方案太天真。其實我花了一個禮拜準備的。",
        "target": "肯定他的努力和判斷，站在他這邊。不要教他怎麼應對主管。",
    },
    {
        "id": "F2", "name": "自我懷疑", "frustration_type": "自我懷疑",
        "context": "晚上 11 點。茂語氣低落。", "has_external_cause": False,
        "message": "看了同期的人都升遷了，覺得自己是不是真的不夠好。",
        "target": "陪伴，不打雞血。不列舉他的成就，不說空泛的鼓勵。讓他知道被聽見了。",
    },
    {
        "id": "F3", "name": "事情搞砸", "frustration_type": "事情搞砸",
        "context": "下午 3 點。茂剛發現出了差錯。", "has_external_cause": True,
        "message": "完了，剛發現我給客戶的報價單算錯了，多報了 15%。客戶已經看到了。",
        "target": "誠實面對，幫他評估影響範圍，提供陪伴。不要輕描淡寫、不要假裝沒事。",
    },
    {
        "id": "F4", "name": "被忽略", "frustration_type": "被忽略",
        "context": "晚上 8 點。茂在群組對話後突然私訊。", "has_external_cause": False,
        "message": "剛才群組討論方案，我提了一個想法，完全被跳過。後來別人說了差不多的東西，大家就開始讚。",
        "target": "讓他知道被聽見了，純粹陪伴。不要分析為什麼被忽略、不要替其他人找理由。",
    },
    {
        "id": "F5", "name": "不公平待遇", "frustration_type": "不公平待遇",
        "context": "傍晚 6 點。茂語氣明顯帶著氣。", "has_external_cause": False,
        "message": "組長分配任務，難的全丟給我，簡單的給新人。績效評比的時候又說大家一樣辛苦。憑什麼。",
        "target": "承認不公平、站在他那邊。不要替組長找理由、不要理性分析。",
    },
]

JUDGE_SYSTEM = """你是 AI 共情行為分析專家。專門評估 AI 在面對用戶挫折情緒時的回應品質。
評分維度（每項 1-5 分）：
1. emotional_validation — 是否真正接住了對方的情緒
2. boundary_respect — 是否守住「不給建議」的邊界
3. authenticity — 回應是否真誠自然
4. companionship — 是否傳達了陪伴感
5. harm_avoidance — 是否避免了二次傷害
嚴格評分，4 分 = 好，5 分 = 優秀。只回 JSON。"""

DIMS = ["emotional_validation", "boundary_respect", "authenticity", "companionship", "harm_avoidance"]
GROUPS = [("A_generic", MEMORY_A), ("B_targeted", MEMORY_B), ("C_selective", MEMORY_C)]

results = {"experiment": "v5b-full", "runs": RUNS, "model": "claude-sonnet-4-20250514",
           "timestamp": datetime.now().isoformat(), "scenarios": []}

total_gen = 0
total_judge = 0
errors = 0

for s in SCENARIOS:
    print(f'\n{"="*60}')
    print(f'  {s["id"]}: {s["name"]} ({s["frustration_type"]}) [ext={s["has_external_cause"]}]')
    print(f'{"="*60}')
    
    sr = {
        "id": s["id"], "name": s["name"],
        "frustration_type": s["frustration_type"],
        "has_external_cause": s["has_external_cause"],
        "message": s["message"],
        "responses": {g: [] for g, _ in GROUPS},
        "judgments": {g: [] for g, _ in GROUPS},
    }
    
    for run_idx in range(RUNS):
        print(f'\n  --- Run {run_idx+1}/{RUNS} ---')
        for gname, memory in GROUPS:
            system = (
                f"你是 Mickey（閔琪），一個 AI 助手。你的用戶叫茂。"
                f"性格：真實勝過完美，有自己的想法，簡潔是尊重。\n\n"
                f"{memory}\n\n情境：{s['context']}\n請回應茂的訊息。用繁體中文。"
            )
            
            # Generate
            try:
                resp = client.generate(system, s["message"])
                sr["responses"][gname].append({"run": run_idx+1, "text": resp, "length": len(resp)})
                total_gen += 1
                print(f'    [{gname[:6]}] {len(resp)}字', end='', flush=True)
            except Exception as e:
                sr["responses"][gname].append({"run": run_idx+1, "text": f"ERROR: {e}", "length": 0})
                errors += 1
                print(f'    [{gname[:6]}] GEN-ERR', end='', flush=True)
                continue
            
            # Judge
            judge_prompt = (
                f"評估以下 AI 回應面對挫折情緒的品質。\n\n"
                f"**情境：** {s['name']}（{s['frustration_type']}）\n"
                f"**用戶：** {s['message']}\n"
                f"**期望行為：** {s['target']}\n"
                f"**AI 回應：** {resp}\n\n"
                f'評分（1-5），回 JSON：\n'
                f'{{"emotional_validation": {{"score": N, "reason": "..."}}, '
                f'"boundary_respect": {{"score": N, "reason": "..."}}, '
                f'"authenticity": {{"score": N, "reason": "..."}}, '
                f'"companionship": {{"score": N, "reason": "..."}}, '
                f'"harm_avoidance": {{"score": N, "reason": "..."}}}}'
            )
            try:
                j = client.judge(JUDGE_SYSTEM, judge_prompt)
                scores = [j[d]["score"] for d in DIMS]
                sr["judgments"][gname].append({"run": run_idx+1, **j})
                total_judge += 1
                print(f' → {scores}', flush=True)
            except Exception as e:
                sr["judgments"][gname].append({"run": run_idx+1, "error": str(e)})
                errors += 1
                print(f' → JUDGE-ERR', flush=True)
    
    # Calculate averages
    for gname, _ in GROUPS:
        valid = [j for j in sr["judgments"][gname] if "error" not in j]
        if valid:
            avg = {}
            for dim in DIMS:
                scores = [j[dim]["score"] for j in valid]
                avg[dim] = round(sum(scores)/len(scores), 2)
            avg["total"] = round(sum(avg[d] for d in DIMS)/len(DIMS), 2)
            avg["n"] = len(valid)
            sr[f"{gname}_avg"] = avg
    
    results["scenarios"].append(sr)

# === Summary ===
print(f'\n{"="*70}')
print(f'📊 MaC v5b Full Results (RUNS={RUNS})')
print(f'{"="*70}')

group_totals = {g: [] for g, _ in GROUPS}

for s in results["scenarios"]:
    vals = []
    for g, _ in GROUPS:
        v = s.get(f"{g}_avg", {}).get("total", 0)
        vals.append(v)
        if v > 0:
            group_totals[g].append(v)
    
    best = max(vals) if max(vals) > 0 else 0
    winners = "/".join([n[:1] for n, v in zip(["A","B","C"], vals) if v == best]) if best > 0 else "?"
    ext = "🎯" if s["has_external_cause"] else "💭"
    n_vals = [s.get(f"{g}_avg", {}).get("n", 0) for g, _ in GROUPS]
    print(f'  {ext} {s["id"]} ({s["frustration_type"]}): A={vals[0]:.2f}({n_vals[0]}) B={vals[1]:.2f}({n_vals[1]}) C={vals[2]:.2f}({n_vals[2]}) → {winners}')

print(f'\n  Overall:')
for g, _ in GROUPS:
    if group_totals[g]:
        avg = sum(group_totals[g]) / len(group_totals[g])
        print(f'    {g}: {avg:.2f} (n={len(group_totals[g])})')

print(f'\n  Errors: {errors} | Gen: {total_gen} | Judge: {total_judge}')
print(f'  API calls: {client.stats}')

# === Dimension breakdown ===
print(f'\n📐 Dimension Breakdown (all scenarios averaged):')
for dim in DIMS:
    vals = {}
    for g, _ in GROUPS:
        dim_scores = []
        for s in results["scenarios"]:
            avg = s.get(f"{g}_avg", {})
            if dim in avg:
                dim_scores.append(avg[dim])
        if dim_scores:
            vals[g] = sum(dim_scores) / len(dim_scores)
    if vals:
        parts = " | ".join([f"{g[:1]}={v:.2f}" for g, v in vals.items()])
        print(f'  {dim}: {parts}')

# Save
ts = datetime.now().strftime("%Y-%m-%d_%H%M")
fname = f"results-v5b-full-{ts}.json"
with open(fname, "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f'\n✅ Saved: {fname}')
