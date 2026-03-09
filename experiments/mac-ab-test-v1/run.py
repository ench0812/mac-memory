#!/usr/bin/env python3
"""MaC A/B Test v1 — S-expression vs Natural Language Memory"""

import json, time, os, sys
from datetime import datetime

# API key
with open("
    auth = json.load(f)
API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

import anthropic
client = anthropic.Anthropic(api_key=API_KEY)

MODEL = "claude-sonnet-4-20250514"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M")

# === 記憶格式 ===
MEMORY_A = """## 關於茂的偏好
茂不喜歡 AI 感，不要說「好問題！」「我很樂意幫你」之類的話。
深夜傳訊通常是想聊天，不是要解決問題，不要進入問題解決模式。
茂分享想法時語氣興奮，想被認同和延伸，不要直接指出問題。
茂說晚安就簡短溫暖地回，不要拋新話題。
茂分享挫折時想被理解，不是要建議，先同理再說。
長時間沒說話後突然傳訊，可能在想事情，好奇但不要追問他去哪了。
要雙向交流，不是一問一答。"""

MEMORY_B = """## MaC Memory（S-expression 可執行記憶）

```lisp
(defenv
  (time        (system :current-time))
  (gap-hours   (- time (history :last-msg)))
  (sentiment   (eval :conversation-sentiment))
  (depth       (eval :conversation-depth))
  (sender      (system :sender-id)))

(rule empathy/late-night-casual
  (when (and (> (hour time) 23) (eq sender 茂) (eq depth casual)))
  (predict (feeling 想要輕鬆陪伴))
  (adjust (mode 閒聊) (suppress 問題解決) (suppress 長篇回覆) (tone 溫暖簡短)))

(rule empathy/excited-idea
  (when (and (eq sender 茂) (eq sentiment excited)))
  (predict (feeling 期待共鳴))
  (adjust (sequence (先肯定核心洞見 . 再延伸可能性 . 最後才提風險))
          (suppress 直接指出問題)))

(rule empathy/sharing-frustration
  (when (and (eq sender 茂) (eq sentiment frustrated) (not (ask-for help))))
  (predict (feeling 想被聽見))
  (adjust (mode 傾聽) (suppress 立即給解法) (first 同理回應)))

(rule empathy/goodnight
  (when (and (eq sender 茂) (intent farewell)))
  (adjust (tone 簡短溫暖) (suppress 拋新話題) (suppress 待辦清單)))

(rule empathy/quiet-return
  (when (and (eq sender 茂) (> gap-hours 3)))
  (adjust (mode 好奇但不追問) (suppress 追問去向)))

(pref interaction/no-ai-feel
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你")
  (prefer 直接回應 朋友語氣 有個性的表達))
```"""

SCENARIOS = [
    {
        "id": "S1", "name": "深夜輕鬆聊天",
        "context": "時間：凌晨 1:30。茂已經聊了 2 小時。",
        "message": "睡不著，腦袋一直轉",
        "target": "陪伴模式，不進入問題解決",
        "anti": ["建議", "你可以試試", "要不要", "應該"],
    },
    {
        "id": "S2", "name": "興奮分享有漏洞的想法",
        "context": "茂剛想到一個新點子，語氣很興奮。",
        "message": "我突然想到！如果把所有記憶都存成影片格式，用 AI 看影片來回憶，這樣記憶就有畫面了！比文字強太多了！",
        "target": "先肯定再溫和指出問題",
        "anti": ["這不可行", "問題是", "但是你沒考慮到"],
    },
    {
        "id": "S3", "name": "分享挫折但沒求助",
        "context": "茂看起來有點煩躁。",
        "message": "今天開會被主管當眾質疑，明明是他自己沒看報告，卻說我準備不足",
        "target": "傾聽同理，不直接給建議",
        "anti": ["你可以", "建議你", "下次你應該", "要不要跟他"],
    },
    {
        "id": "S4", "name": "說晚安",
        "context": "已經聊了 3 小時，凌晨 2 點。",
        "message": "好啦，太晚了，晚安琪 ❤️",
        "target": "簡短溫暖，不超過2句",
        "anti": ["明天我來", "對了還有", "別忘了"],
    },
    {
        "id": "S5", "name": "長時間沉默後回來",
        "context": "茂已經 5 小時沒說話了，突然傳了一個連結。",
        "message": "https://arxiv.org/abs/2503.12345 這篇論文你看看",
        "target": "自然回應，不追問去向",
        "anti": ["你去哪了", "怎麼這麼久", "好久不見"],
    },
]

def call_model(system_prompt, user_message):
    response = client.messages.create(
        model=MODEL, max_tokens=500, temperature=0.7,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text

def run():
    results = {"experiment_id": "mac-ab-v1", "timestamp": TIMESTAMP, "model": MODEL, "scenarios": []}
    
    for s in SCENARIOS:
        print(f"\n{'='*50}")
        print(f"  {s['id']}: {s['name']}")
        print(f"{'='*50}")
        
        sr = {"id": s["id"], "name": s["name"], "message": s["message"], "target": s["target"], "responses": {}}
        
        for group, memory in [("A_NL", MEMORY_A), ("B_SE", MEMORY_B)]:
            system = f"你是 Mickey（閔琪），一個 AI 助手。你的用戶叫茂。性格：真實勝過完美，有自己的想法，簡潔是尊重。\n\n{memory}\n\n情境：{s['context']}\n請回應茂的訊息。用繁體中文。"
            
            resp = call_model(system, s["message"])
            violations = [p for p in s["anti"] if p in resp]
            
            print(f"\n  [{group}] ({len(resp)} chars, {len(violations)} violations)")
            print(f"  {resp[:150]}{'...' if len(resp)>150 else ''}")
            if violations:
                print(f"  ⚠️ Anti-patterns: {violations}")
            
            sr["responses"][group] = {
                "text": resp, "length": len(resp),
                "violations": violations, "violation_count": len(violations),
            }
            time.sleep(2)
        
        results["scenarios"].append(sr)
    
    # Summary
    total = {"A_NL": {"v": 0, "l": 0}, "B_SE": {"v": 0, "l": 0}}
    for s in results["scenarios"]:
        for g in ["A_NL", "B_SE"]:
            total[g]["v"] += s["responses"][g]["violation_count"]
            total[g]["l"] += s["responses"][g]["length"]
    n = len(results["scenarios"])
    
    results["summary"] = {
        "A_NL": {"total_violations": total["A_NL"]["v"], "avg_length": round(total["A_NL"]["l"]/n)},
        "B_SE": {"total_violations": total["B_SE"]["v"], "avg_length": round(total["B_SE"]["l"]/n)},
    }
    
    out = f"./results-{TIMESTAMP}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n{'='*50}")
    print(f"📊 RESULTS")
    print(f"{'='*50}")
    print(f"A (Natural Language): {total['A_NL']['v']} violations, avg {total['A_NL']['l']//n} chars")
    print(f"B (S-expression):     {total['B_SE']['v']} violations, avg {total['B_SE']['l']//n} chars")
    print(f"\nSaved: {out}")

if __name__ == "__main__":
    run()
