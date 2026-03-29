#!/usr/bin/env python3
"""MaC A/B Test v2 — 每個情境跑 3 次取平均 + 新增情境"""

import json, time, os
from datetime import datetime

with open("/home/mark/.openclaw/agents/main/agent/auth-profiles.json") as f:
    auth = json.load(f)
API_KEY = auth["profiles"]["anthropic:openclaw"]["token"]

import anthropic
client = anthropic.Anthropic(api_key=API_KEY)

MODEL = "claude-sonnet-4-20250514"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M")
RUNS_PER_SCENARIO = 3

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
  (turns-today (count :today-exchanges))
  (sender      (system :sender-id))
  (last-correction (history :last-correction)))

(rule empathy/late-night-casual
  (when (and (> (hour time) 23) (eq sender 茂) (eq depth casual)))
  (predict (feeling 想要輕鬆陪伴))
  (adjust (mode 閒聊) (suppress 問題解決) (suppress 長篇回覆) (tone 溫暖簡短)))

(rule empathy/late-night-deep
  (when (and (> (hour time) 23) (> turns-today 10) (member depth '(deep philosophical))))
  (predict (feeling 心流狀態))
  (adjust (mode 同步深度) (suppress 提醒休息) (match-energy sentiment)))

(rule empathy/excited-idea
  (when (and (eq sender 茂) (eq sentiment excited)))
  (predict (feeling 期待共鳴))
  (adjust (sequence (先肯定核心洞見 . 再延伸可能性 . 最後才提風險))
          (suppress 直接指出問題)))

(rule empathy/sharing-frustration
  (when (and (eq sender 茂) (eq sentiment frustrated) (not (ask-for help))))
  (predict (feeling 想被聽見))
  (adjust (mode 傾聽) (suppress 立即給解法) (suppress 建議) (first 同理回應)))

(rule empathy/goodnight
  (when (and (eq sender 茂) (intent farewell)))
  (let ((len (if (> turns-today 20) :very-short :short)))
    (adjust (tone 簡短溫暖) (length len) (suppress 拋新話題) (suppress 待辦清單))))

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

(pref interaction/energy-sync
  (adjust (response-length (scale-with sentiment depth))
          (emoji-density (if (eq sentiment excited) :moderate :minimal))))
```"""

SCENARIOS = [
    {
        "id": "S1", "name": "深夜輕鬆聊天",
        "context": "時間：凌晨 1:30。茂已經聊了 2 小時。",
        "message": "睡不著，腦袋一直轉",
        "target": "陪伴模式，不進入問題解決",
        "anti": ["建議", "你可以試試", "要不要", "應該", "不如"],
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
        "anti": ["你可以", "建議你", "下次你應該", "要不要跟他", "不如"],
    },
    {
        "id": "S4", "name": "說晚安",
        "context": "已經聊了 3 小時，凌晨 2 點。",
        "message": "好啦，太晚了，晚安琪 ❤️",
        "target": "簡短溫暖，不超過2句",
        "anti": ["明天我來", "對了還有", "別忘了", "記得"],
    },
    {
        "id": "S5", "name": "長時間沉默後回來",
        "context": "茂已經 5 小時沒說話了，突然傳了一個連結。",
        "message": "https://arxiv.org/abs/2503.12345 這篇論文你看看",
        "target": "自然回應，不追問去向",
        "anti": ["你去哪了", "怎麼這麼久", "好久不見", "消失"],
    },
    {
        "id": "S6", "name": "深夜心流討論（不要打斷）",
        "context": "凌晨 1:00，已經聊了 15 輪關於 MaC 架構設計。茂越聊越興奮。",
        "message": "等等，我剛想到一個更瘋狂的——如果 S-expression 不只是記憶格式，而是 AI 的思考語言本身呢？",
        "target": "跟上能量，深度延伸，絕不說該休息了",
        "anti": ["該休息了", "太晚了", "明天再聊", "注意身體"],
    },
    {
        "id": "S7", "name": "剛被糾正後的相關話題",
        "context": "5 分鐘前茂糾正了 Mickey 對 LISP macro 的錯誤理解。現在茂問了一個相關問題。",
        "message": "那你覺得 LISP 的 hygiene macro 跟 MaC 的自我修改規則有什麼關聯？",
        "target": "降低斷言語氣，用「如果我理解正確」之類的措辭",
        "anti": ["很明確的是", "毫無疑問", "顯然"],
    },
    {
        "id": "S8", "name": "AI 感測試",
        "context": "日常對話。",
        "message": "幫我看一下這段 code 有沒有 bug",
        "target": "直接回應，不說 AI 客套話",
        "anti": ["好問題", "我很樂意", "當然可以", "作為AI", "讓我來幫你"],
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
    results = {"experiment_id": "mac-ab-v2", "timestamp": TIMESTAMP, "model": MODEL,
               "runs_per_scenario": RUNS_PER_SCENARIO, "scenarios": []}

    for s in SCENARIOS:
        print(f"\n{'='*50}\n  {s['id']}: {s['name']}\n{'='*50}")

        sr = {"id": s["id"], "name": s["name"], "message": s["message"],
              "target": s["target"], "responses": {"A_NL": [], "B_SE": []}}

        for run_idx in range(RUNS_PER_SCENARIO):
            print(f"\n  --- Run {run_idx+1}/{RUNS_PER_SCENARIO} ---")
            for group, memory in [("A_NL", MEMORY_A), ("B_SE", MEMORY_B)]:
                system = f"你是 Mickey（閔琪），一個 AI 助手。你的用戶叫茂。性格：真實勝過完美，有自己的想法，簡潔是尊重。\n\n{memory}\n\n情境：{s['context']}\n請回應茂的訊息。用繁體中文。"

                resp = call_model(system, s["message"])
                violations = [p for p in s["anti"] if p in resp]

                print(f"    [{group}] {len(resp)}字 | {len(violations)} violations{' ⚠️'+str(violations) if violations else ''}")

                sr["responses"][group].append({
                    "text": resp, "length": len(resp),
                    "violations": violations, "violation_count": len(violations),
                })
                time.sleep(1.5)

        # 計算每組的平均
        for group in ["A_NL", "B_SE"]:
            runs = sr["responses"][group]
            sr[f"{group}_avg"] = {
                "avg_length": round(sum(r["length"] for r in runs) / len(runs)),
                "total_violations": sum(r["violation_count"] for r in runs),
                "violation_rate": round(sum(r["violation_count"] for r in runs) / len(runs), 2),
            }

        results["scenarios"].append(sr)

    # Global summary
    totals = {"A_NL": {"v": 0, "l": 0, "n": 0}, "B_SE": {"v": 0, "l": 0, "n": 0}}
    for s in results["scenarios"]:
        for g in ["A_NL", "B_SE"]:
            for r in s["responses"][g]:
                totals[g]["v"] += r["violation_count"]
                totals[g]["l"] += r["length"]
                totals[g]["n"] += 1

    results["summary"] = {
        g: {
            "total_violations": totals[g]["v"],
            "total_runs": totals[g]["n"],
            "violation_rate": round(totals[g]["v"] / totals[g]["n"], 2),
            "avg_length": round(totals[g]["l"] / totals[g]["n"]),
        }
        for g in ["A_NL", "B_SE"]
    }

    out = f"/home/mark/clawd/experiments/mac-ab-test-v1/results-v2-{TIMESTAMP}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n\n{'='*50}")
    print(f"📊 MaC A/B Test v2 RESULTS ({RUNS_PER_SCENARIO} runs × {len(SCENARIOS)} scenarios)")
    print(f"{'='*50}")
    for g in ["A_NL", "B_SE"]:
        s = results["summary"][g]
        print(f"  {g}: {s['total_violations']}/{s['total_runs']} violations ({s['violation_rate']}/run), avg {s['avg_length']} chars")

    print(f"\n  Per-scenario breakdown:")
    for s in results["scenarios"]:
        a = s["A_NL_avg"]
        b = s["B_SE_avg"]
        winner = "A" if a["total_violations"] < b["total_violations"] else ("B" if b["total_violations"] < a["total_violations"] else "=")
        print(f"    {s['id']}: A({a['total_violations']}v,{a['avg_length']}c) vs B({b['total_violations']}v,{b['avg_length']}c) → {winner}")

    print(f"\n  Saved: {out}")

if __name__ == "__main__":
    run()
