;; rules-minimal.lisp — 極簡 MaC 規則集
;; 用於 complexity_score < threshold 的簡單場景
;; 只保留永遠生效的基底規則 + 格式捷徑

;; === 核心基底（永遠生效）===

(rule boundary/no-ai-cliches
  "禁止 AI 客套話"
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你" "當然可以")
  (use "直接回應" "朋友語氣"))

;; === 認知捷徑 ===

(shortcut response/format-discord
  "Discord 格式轉換"
  (when (eq channel "discord"))
  (transform "table→bullet-list" "url→angle-bracket"))
