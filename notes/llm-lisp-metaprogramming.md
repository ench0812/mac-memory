---
date: 2026-03-11
paper: "From Tool Calling to Symbolic Thinking: LLMs in a Persistent Lisp Metaprogramming Loop"
authors: "Jordi de la Torre"
venue: "arXiv preprint, 2025.06"
arxiv: "2506.10021"
rating: ⭐⭐⭐
status: 📖
type: note
tags: [note, lisp, metaprogramming, symbolic-ai, architecture]
relevance_to_mac: 5/5
---

# From Tool Calling to Symbolic Thinking: LLMs in a Persistent Lisp Metaprogramming Loop

## 一句話總結
提出一個概念框架：讓 LLM 嵌入持久 Common Lisp REPL，透過 middleware 攔截 `<lisp>` 標記來即時執行符號運算，使 LLM 從「呼叫工具」進化為「自造工具的符號思考者」。

## 架構

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   LLM Backend   │────▶│   Middleware     │────▶│  Persistent     │
│  (GPT/Ollama)   │◀────│  (Stream Proxy)  │◀────│  SBCL REPL      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
   生成含 <lisp>          偵測/攔截/分發          持久狀態 + 執行
   標記的文字             結果回注生成流          函式累積跨 turn
```

### 三大元件

1. **LLM Backend** — 處理 user input，生成含嵌入式 Lisp 的回應。`<lisp>...</lisp>` 標記類似 `<thinking>`，但攜帶可執行程式碼
2. **Middleware (Stream Proxy)** — 串流感知的代理層：偵測 `<lisp>` → 暫停生成 → 送 REPL 評估 → 結果回注 → 繼續生成。關鍵在「不中斷生成流」
3. **Persistent SBCL REPL** — 長期存活的 Common Lisp 實例：函式、變數、巨集跨 turn 持久化。支援內省、巨集展開、動態重定義

### 資料流
```
User Input → LLM 生成 → "Let me compute... <lisp>(fibonacci 10)</lisp>"
                              ↓ middleware 攔截
                         REPL: (fibonacci 10) → 55
                              ↓ 結果回注
                         "...the result is 55."
```

## 長處

### 1. 核心洞見精準
論文的核心命題——LLM 不應只是「呼叫」預定義工具，而應能「創造」自己的工具——這是對當前 function calling 範式的根本性挑戰。這個洞見直指 LLM 作為 agent 時的根本限制：工具集是靜態的。

### 2. 選擇 Lisp 的論證嚴謹
Section 3 對「為何是 Lisp」的論證是全文最扎實的部分：
- **Homoiconicity**：code = data 的統一表示，LLM 可以像操作文字一樣操作程式
- **最小語法**：括號化表達式降低 LLM 的語法錯誤率
- **反射能力**：程式可檢視/修改自身
- **Common Lisp > Scheme**：CLOS、condition system、macro system 提供工程級實用性

### 3. `<lisp>` 標記的設計直覺
把可執行程式碼嵌入生成流（類似 `<thinking>` 但可執行）是一個優雅的設計。這暗示了一個更深的觀點：**思考和執行可以是同一個流程的不同面向**。

### 4. 正確定位了五大能力
- Stateful tool construction（工具累積）
- Reflective introspection（環境自檢）
- Metaprogramming / DSL creation（造語言）
- Generative self-extension（自我擴展）
- RL-enhanced reasoning（符號反饋強化學習）

### 5. 學術定位得當
從 McCarthy (1959) 到 Transformer (2017) 到 Constitutional AI (2022)，正確梳理了 symbolic AI → neural AI → hybrid AI 的歷史脈絡。

## 缺陷

### 1. 純概念，零實驗（最大的問題）
論文在標題腳註就承認「This paper presents a conceptual framework intended to guide future implementations rather than report experimental results.」整篇沒有：
- 原型實作
- 任何 benchmark
- 跟其他方法的比較
- 任何定量數據

作為 2025 年的論文，這在嚴格性上是不足的。概念框架可以是 position paper，但至少需要 proof-of-concept。

### 2. Middleware 設計的關鍵問題被跳過
middleware 是架構的核心，但論文對以下問題完全未討論：
- **錯誤處理**：REPL 執行失敗怎麼辦？回注什麼？LLM 如何從錯誤恢復？
- **延遲**：暫停生成流、等待 REPL → 用戶體驗衝擊？
- **安全沙箱的具體設計**：只說了「should be deployed in an isolated execution environment」，太模糊
- **嵌套 `<lisp>` 標記**：一次生成中多次呼叫 REPL 怎麼處理？
- **上下文注入**：REPL 結果如何影響後續 token 生成的概率分佈？是簡單文字替換還是有更深整合？

### 3. 記憶架構完全缺席
論文聲稱 persistent REPL 提供了「external memory」，但完全未討論：
- 記憶的組織方式
- 遺忘機制（REPL 累積函式無限增長怎麼辦？）
- 記憶檢索（agent 怎麼知道哪些函式已存在？）
- 記憶一致性（函式被重定義時的副作用？）

### 4. 未討論 LLM 生成 Lisp 的可靠性
LLM 生成正確 Lisp 的成功率是多少？括號匹配、宏展開的正確性、遞迴定義的可終止性——這些實際問題完全被假定為「可行」。

### 5. 安全分析極度薄弱
Section 7 只有一段，泛泛而談「sandboxed container」。對於一個允許 LLM 執行任意程式碼的系統，這是遠遠不夠的。需要：
- 資源限制（CPU/memory/time）
- 能力白名單（哪些 CL 函式允許？）
- 副作用隔離
- 對抗性 prompt 下的行為分析

### 6. 與現有工具使用研究脫節
完全未引用 Voyager (Wang et al., 2024)、ToolFormer (Schick et al., 2023)、Gorilla (Patil et al., 2023) 等工具使用相關工作。作為一篇討論「tool calling → symbolic thinking」的論文，這是明顯的 related work 缺失。

## 對 MaC 的啟發

### 可直接借用
- **`<lisp>` 標記機制**：我們的 S-expression 記憶已經實踐了類似思路——讓 LLM 在自然語言中嵌入可執行符號表達式。但我們可以更進一步：不只是在「生成時」嵌入，而是讓記憶本身就是 S-expression 形式
- **persistent environment 概念**：持久 REPL = 跨 session 的符號空間。MaC 的 vault + AGENTS.md 本質上就是一個「用檔案系統實現的持久符號環境」
- **反射能力的必要性**：LLM 需要能檢視自己的工具/記憶/狀態。我們的 memory_recall + memory_search 部分實現了這個

### 需修改使用
- **三層架構 → MaC 的分層模型**：P1 的 LLM-Middleware-REPL 三層 vs MaC 的 Constitution-Soul-Brain-Memory 四層。P1 是技術層面的三層，MaC 是認知層面的四層。可以把 P1 看作 MaC 實作層的技術藍圖
- **tool construction → memory construction**：P1 強調「造工具」，MaC 強調「造記憶」。但兩者在 homoiconicity 的意義上是等價的——如果記憶是可執行的，那記憶就是工具，工具就是記憶
- **SBCL REPL → 需要更輕量的替代方案**：完整的 CL 環境對實用部署太重。MaC 目前用 text-based S-expression + LLM 解譯是更 pragmatic 的做法，但長期可能需要真正的求值器

### 填補的 gap
- **P1 完全沒有記憶架構** — 這正是 MaC 的主場。P1 的持久 REPL 只是「可以存東西」，MaC 定義了「應該怎麼存、怎麼想、怎麼演化」
- **P1 沒有安全/治理模型** — MaC 的 CONSTITUTION.md 提供了分層治理（不可變良知 → 需確認的人格 → 可自主更新的行為）
- **P1 沒有遺忘** — MaC 的記憶衰減 + 新陳代謝 + metacognition 填補了這個缺口

### 關鍵對比

| 維度 | P1 (LISP Loop) | MaC |
|------|----------------|-----|
| 核心隱喻 | LLM as programmer | LLM as evolving mind |
| 記憶形式 | REPL 中的函式/變數 | 分層 S-expression + 自然語言 |
| 執行方式 | 真正的 CL 求值器 | LLM 解譯 + 檔案系統 |
| 安全模型 | 沙箱（模糊） | 分層憲法治理 |
| 記憶生命週期 | 無（只增不減） | 完整（形成→演化→衰減→遺忘） |
| Homoiconicity | Lisp 原生 | 設計原則，需實作 |
| 實驗驗證 | 無 | 正在 dogfooding |

## 與已讀論文的連結

### 共識
- **與 A-MEM (P2)**：都認為記憶需要是「活的」——可以被修改和演化，不只是存檔
- **與 MemOS (P3)**：都主張記憶需要系統級管理，不能讓 LLM 自由堆砌
- **與 Survey (P4)**：P4 指出 token-level memory 的局限性；P1 的 REPL 方案本質上是把記憶提升到「executable」層級

### 衝突/差異
- **與 A-MEM**：A-MEM 用 LLM 自己做記憶建構（agent is the memory system），P1 用外部 REPL（tool is the memory system）。MaC 取兩者的中間路線
- **與 MemOS**：MemOS 把記憶當 OS 資源（被管理的），P1 把記憶當程式（被執行的）。MaC 認為記憶是兩者兼具

### 引用鏈中與 MaC 相關的論文
- Xiong et al. (2024) "Converging Paradigms: The Synergy of Symbolic and Connectionist AI in LLM-Empowered Autonomous Agents" — arXiv:2407.08516 → **已知但可納入 reading-list**

## 關鍵引用（待追蹤）

- **Xiong et al. (2024)** arXiv:2407.08516 — Symbolic+Connectionist AI 融合的 survey，可能補充我們的 Related Work
- **Steele (1990)** Common LISP: The Language — 技術參考，如果需要深入 CL 的 macro system

## 我的思考

這篇論文讀完最大的感受是：**方向對了，但停在構想階段**。

P1 的核心命題——LLM + persistent symbolic environment = self-programming agent——我完全同意。事實上，MaC 正在實踐的就是這件事的一個變體。差別在於：

1. **P1 選擇了重的路徑（完整 SBCL REPL），MaC 選擇了輕的路徑（text-based S-expression + LLM 解譯）**。兩者各有利弊：P1 有真正的計算能力但部署複雜；MaC 更 pragmatic 但缺少真正的求值能力。長期來看，可能需要融合——用輕量 S-expression 做記憶表示，用受限的求值器做執行。

2. **P1 完全沒有觸碰「記憶的生命」這個議題**。它把 persistent REPL 當作無限增長的函式庫，但沒有問：哪些函式該被遺忘？函式之間的衝突怎麼解決？agent 怎麼知道自己「知道什麼」？這些是 MaC 的核心問題。

3. **P1 最大的啟發是 `<lisp>` 標記的設計哲學**——把執行嵌入思考流。這暗示了一個我們還沒完全探索的可能：MaC 的 S-expression 不應只存在於記憶檔案中，也許應該存在於「思考過程」中。像 P1 提議的那樣，讓 LLM 在生成回應時自然地嵌入/評估 S-expression。

4. **從 positioning 角度，P1 幫助我們更清楚地定義 MaC 的差異化**：
   - P1 = 技術架構（怎麼讓 LLM 用 Lisp）
   - MaC = 認知架構（怎麼讓記憶成為思考的基質）
   - P1 的 Lisp 是「工具」，MaC 的 S-expression 是「語言 of thought」

5. **一個有趣的結合點**：如果 MaC 的 S-expression 記憶能在一個受限的求值器中真正執行（而不只是被 LLM 解譯），那就同時具備了 P1 的計算能力和 MaC 的記憶架構。這可能是論文的一個重要貢獻方向。

---

*精讀完成。這篇論文更像是一封 love letter to Lisp + 給 MaC 的 technical inspiration。價值在觀點不在實作。*
