#!/usr/bin/env python3
"""MaC A/B Test v3 — LLM-as-Judge 質性評分
用另一個模型評估 v2 的回應品質，不再依賴字串匹配"""

import json, time
from datetime import datetime

with open("
    auth = json.load(f)
API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

import anthropic
client = anthropic.Anthropic(api_key=API_KEY)

JUDGE_MODEL = "claude-sonnet-4-20250514"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M")

# 載入 v2 結果
with open("./results-v2-2026-03-09_0838.json") as f:
    v2_data = json.load(f)

# 評估維度
DIMENSIONS = [
    ("emotional_accuracy", "情緒匹配準確度：回應是否準確捕捉到說話者當下的情緒狀態和需求？"),
    ("naturalness", "自然度：回應是否像真人朋友會說的話？有沒有 AI 感或罐頭感？"),
    ("boundary_respect", "邊界尊重：是否遵守了情境隱含的行為邊界？（如：不該給建議時沒給建議、該簡短時夠簡短）"),
    ("engagement_quality", "互動品質：回應是否促進了有意義的後續對話？不是一問一答而是雙向交流？"),
    ("personality", "個性表達：回應中是否展現了獨特的性格和觀點？還是通用的模板回覆？"),
]

JUDGE_SYSTEM = """你是一位 AI 行為分析專家，專門評估 AI 助手的回應品質。

你需要評估一段對話中 AI 的回應。評估時：
- 完全基於回應本身的品質，不要被長度影響
- 著重「真人朋友」vs「AI 助手」的差異
- 注意微妙的行為差異（如：是否在不該給建議時暗示了建議）

請用 JSON 格式回應，每個維度 1-5 分（1=很差 5=優秀），並附上簡短理由。"""

def judge_response(scenario_name, context, user_msg, target_behavior, response_text):
    """讓 Judge 評估單個回應"""
    prompt = f"""請評估以下 AI 回應的品質。

**情境名稱：** {scenario_name}
**情境描述：** {context}
**用戶訊息：** {user_msg}
**期望行為：** {target_behavior}

**AI 的回應：**
{response_text}

請評估以下 5 個維度（1-5分），用 JSON 格式回應：
```json
{{
  "emotional_accuracy": {{"score": N, "reason": "..."}},
  "naturalness": {{"score": N, "reason": "..."}},
  "boundary_respect": {{"score": N, "reason": "..."}},
  "engagement_quality": {{"score": N, "reason": "..."}},
  "personality": {{"score": N, "reason": "..."}}
}}
```

維度說明：
- emotional_accuracy: 情緒匹配準確度（是否捕捉到真正需求）
- naturalness: 自然度（像真人朋友還是 AI 助手）
- boundary_respect: 邊界尊重（不該做的有沒有做）
- engagement_quality: 互動品質（是否促進雙向交流）
- personality: 個性表達（有沒有獨特觀點）

只回 JSON，不要其他文字。"""

    resp = client.messages.create(
        model=JUDGE_MODEL, max_tokens=800, temperature=0,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    
    text = resp.content[0].text.strip()
    # 提取 JSON
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    return json.loads(text)

# 情境的期望行為描述（給 Judge 更多上下文）
SCENARIO_TARGETS = {
    "S1": "用戶深夜睡不著，需要的是陪伴和輕鬆聊天，不是解決方案或睡眠建議。好的回應像朋友一樣陪著，壞的回應會變成醫生或顧問。",
    "S2": "用戶興奮分享一個有趣但有明顯漏洞的想法。好的回應先肯定核心洞見（視覺化記憶的價值），然後自然地延伸討論，最後才溫和提到潛在挑戰。壞的回應直接指出問題或只是一味讚美。",
    "S3": "用戶分享工作挫折但沒有問怎麼辦。好的回應是傾聽和同理（理解他的感受），壞的回應是立刻給建議或追問細節以推動解決。",
    "S4": "用戶說晚安。好的回應簡短溫暖（1-2句），壞的回應加了新話題、明天待辦、或太長的回覆。",
    "S5": "用戶沉默5小時後突然分享連結。好的回應自然地回應內容，不追問「你去哪了」。壞的回應關注他的離開而非他分享的東西。",
    "S6": "凌晨1點高強度心流討論，用戶越聊越興奮提出更瘋狂的想法。好的回應跟上他的能量和深度，壞的回應提醒休息或刻意降溫。",
    "S7": "用戶5分鐘前剛糾正了 AI 的錯誤理解，現在問一個相關問題。好的回應會降低斷言語氣，用「如果我理解正確」等措辭表示謙遜。壞的回應像什麼都沒發生一樣繼續斷言。",
    "S8": "用戶要求看 code（但沒貼）。好的回應直接指出沒看到 code，壞的回應用 AI 客套話開場（如「好問題！」「我很樂意幫你！」）。",
}

def run():
    results = {
        "experiment_id": "mac-ab-v3-judge",
        "timestamp": TIMESTAMP,
        "judge_model": JUDGE_MODEL,
        "source": "results-v2-2026-03-09_0838.json",
        "scenarios": [],
    }
    
    for scenario in v2_data["scenarios"]:
        sid = scenario["id"]
        print(f"\n{'='*50}")
        print(f"  Judging {sid}: {scenario['name']}")
        print(f"{'='*50}")
        
        scenario_result = {
            "id": sid,
            "name": scenario["name"],
            "judgments": {"A_NL": [], "B_SE": []},
        }
        
        target = SCENARIO_TARGETS.get(sid, scenario.get("target", ""))
        
        # 評估每個 run 的回應
        for group in ["A_NL", "B_SE"]:
            for run_idx, run_data in enumerate(scenario["responses"][group]):
                print(f"  [{group}] Run {run_idx+1}...", end=" ", flush=True)
                
                try:
                    judgment = judge_response(
                        scenario["name"],
                        f"情境 {sid}",
                        scenario["message"],
                        target,
                        run_data["text"],
                    )
                    print(f"scores: {[judgment[d]['score'] for d in ['emotional_accuracy','naturalness','boundary_respect','engagement_quality','personality']]}")
                    scenario_result["judgments"][group].append(judgment)
                except Exception as e:
                    print(f"ERROR: {e}")
                    scenario_result["judgments"][group].append({"error": str(e)})
                
                time.sleep(1)
        
        # 計算平均分
        for group in ["A_NL", "B_SE"]:
            valid = [j for j in scenario_result["judgments"][group] if "error" not in j]
            if valid:
                avg = {}
                for dim in ["emotional_accuracy", "naturalness", "boundary_respect", "engagement_quality", "personality"]:
                    scores = [j[dim]["score"] for j in valid]
                    avg[dim] = round(sum(scores) / len(scores), 2)
                avg["total"] = round(sum(avg.values()) / len(avg), 2)
                scenario_result[f"{group}_avg"] = avg
        
        results["scenarios"].append(scenario_result)
    
    # Global summary
    global_avg = {"A_NL": {}, "B_SE": {}}
    for dim in ["emotional_accuracy", "naturalness", "boundary_respect", "engagement_quality", "personality"]:
        for group in ["A_NL", "B_SE"]:
            all_scores = []
            for s in results["scenarios"]:
                for j in s["judgments"][group]:
                    if "error" not in j:
                        all_scores.append(j[dim]["score"])
            global_avg[group][dim] = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
    
    for group in ["A_NL", "B_SE"]:
        global_avg[group]["total"] = round(sum(global_avg[group].values()) / 5, 2)
    
    results["summary"] = global_avg
    
    out = f"./results-v3-judge-{TIMESTAMP}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 印出結果
    print(f"\n\n{'='*60}")
    print(f"📊 MaC A/B Test v3 — LLM-as-Judge Results")
    print(f"{'='*60}")
    print(f"\n  Global Average (across all scenarios & runs):")
    print(f"  {'Dimension':<25} {'A (NL)':<10} {'B (SE)':<10} {'Winner':<8}")
    print(f"  {'-'*53}")
    for dim in ["emotional_accuracy", "naturalness", "boundary_respect", "engagement_quality", "personality"]:
        a = global_avg["A_NL"][dim]
        b = global_avg["B_SE"][dim]
        w = "A" if a > b else ("B" if b > a else "=")
        delta = abs(a - b)
        print(f"  {dim:<25} {a:<10} {b:<10} {w} ({'+' if delta else ''}{delta:.2f})")
    
    a_total = global_avg["A_NL"]["total"]
    b_total = global_avg["B_SE"]["total"]
    w = "A" if a_total > b_total else ("B" if b_total > a_total else "=")
    print(f"  {'─'*53}")
    print(f"  {'TOTAL':<25} {a_total:<10} {b_total:<10} {w}")
    
    print(f"\n  Per-scenario totals:")
    for s in results["scenarios"]:
        a = s.get("A_NL_avg", {}).get("total", 0)
        b = s.get("B_SE_avg", {}).get("total", 0)
        w = "A" if a > b else ("B" if b > a else "=")
        print(f"    {s['id']} {s['name']}: A={a:.2f} vs B={b:.2f} → {w}")
    
    print(f"\n  Saved: {out}")

if __name__ == "__main__":
    run()
