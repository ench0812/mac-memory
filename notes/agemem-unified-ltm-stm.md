---
date: 2026-04-03
paper: "Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents"
authors: "Yi Yu, Liuyi Yao, Yuexiang Xie, Qingquan Tan, Jiaqi Feng, Yaliang Li, Libing Wu"
venue: "arxiv preprint, 2026.01"
arxiv: "2601.01885"
rating: ⭐⭐⭐
status: 📖
---

# Agentic Memory (AgeMem): 統一 LTM/STM 管理框架

## 一句話總結

用三階段漸進式 RL + step-wise GRPO 訓練 LLM agent 把 LTM 和 STM 管理統一為 tool-based policy，讓 agent 自主決定何時 store / retrieve / update / summarize / filter / discard，在五個 long-horizon benchmark 上全面超越 A-Mem、Mem0、LangMem 等基線。

## 架構

```
┌─────────────────────────────────────────────┐
│              AgeMem Agent Policy (πθ)         │
│                                               │
│   State s_t = (C_t, M_t, T)                  │
│   ├── C_t: Short-term context (message list)  │
│   ├── M_t: Long-term memory store             │
│   └── T: Task specification                   │
│                                               │
│   Action Space A (hybrid):                    │
│   ├── Language generation                     │
│   └── Memory Tool Calls:                      │
│       ├── LTM: Add, Update, Delete            │
│       └── STM: Retrieve, Summary, Filter      │
└───────────────────┬─────────────────────────┘
                    │
    Three-Stage Progressive RL Training
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
  Stage 1         Stage 2         Stage 3
  LTM 建構        STM 控制        整合推理
  (casual chat,   (distractor     (正式 query,
   store salient   injection,      coordinate
   info → M_t)     filter/summary  LTM+STM)
                   context)
                    │
    Step-wise GRPO: 終端 reward 廣播回所有步驟
    R(τ) = w_task·R_task + w_ctx·R_context + w_mem·R_memory + P_penalty
```

**核心設計**：
- 6 種 memory tool（Add/Update/Delete 管 LTM，Retrieve/Summary/Filter 管 STM）作為 structured actions 整合進 agent policy
- 三階段 trajectory：Stage 1 建 LTM → Stage 2 抗干擾學 STM → Stage 3 統合推理。Stage 間 LTM 保留、STM 重置
- Step-wise GRPO：終端 reward 均勻廣播到所有步驟，解決 memory ops 的 sparse/discontinuous reward 問題
- Reward 三維度：R_task（任務完成度）+ R_context（壓縮效率+預防+信息保留）+ R_memory（存儲品質+維護+語義相關性）

**技術棧**：AgentScope + Trinity RL 框架，backbone 用 Qwen2.5-7B-Instruct 和 Qwen3-4B-Instruct。

## 長處

1. **LTM/STM 統一為同一 policy 的核心貢獻非常扎實**。之前所有工作不是把 LTM 和 STM 分開管，就是靠 heuristic / 外部 expert model。AgeMem 讓同一個 LLM 直接學會兩者協調，conceptually clean 且工程可行。

2. **三階段漸進式訓練策略設計精巧**。Stage 間 LTM 保留但 STM 重置的設計，強制 agent 不能靠殘留 context 作弊，必須真正學會 retrieval。這解決了一個 RL 訓練記憶 agent 的核心 credit assignment 問題。

3. **實驗設計有說服力**：
   - 五個異質 benchmark（embodied / game / QA）涵蓋不同推理類型
   - 只在 HotpotQA 訓練但 zero-shot transfer 到其他四個 dataset，證明學到的是 generalizable memory policy
   - RL vs no-RL ablation 清楚：+8.5pp 改善
   - Memory Quality 評估用 ground-truth facts 對比，不只看 task accuracy

4. **Reward 設計的多維度分解**。R_context 拆成 compression/preventive/preservation 三項，R_memory 拆成 storage quality/maintenance/relevance 三項，每一項都有明確的可實現定義。比起 sparse binary reward，這讓 RL 收斂更快（Figure 5 的 All-Returns vs Answer-Only 曲線證實）。

5. **Tool usage 分析（Table 3）是亮點**。RL 前後的 tool call 頻率變化揭示 agent 學到了什麼：Add 從 0.92→1.64（學會主動存），Filter 從 0.02→0.31（學會主動清），Update 從近零→0.13（學會維護）。

## 缺陷

1. **記憶表示仍是 flat text + embedding**。每條 memory 就是 (content, embedding, metadata)，沒有結構、沒有型別、沒有計算能力。這和 MemOS 的 MemCube、A-Mem 的 Zettelkasten 結構，甚至 MAGMA 的 multi-graph 比都顯得過於原始。Agent 學會了「何時記」但沒學會「如何組織」。

2. **Step-wise GRPO 的 advantage broadcast 太粗糙**。A_T 均勻廣播到所有前序步驟 = 每一步得到相同的 learning signal。這意味著 Stage 1 的某一次 Add 操作和 Stage 3 的 Retrieve 得到完全相同的 advantage，丟失了 step-level 的 credit 差異。真正好的 credit assignment 應該區分哪一步 memory decision 對最終結果貢獻更大。

3. **只用 7B 和 4B 小模型，沒測大模型**。核心 argument 是「記憶管理需要 RL 訓練」，但如果用 70B+ 模型做 in-context learning 就能達到相似效果呢？缺乏這個對比，無法排除 scaling 就能解決問題的可能。

4. **Context reset 在實際部署中不成立**。Stage 間重置 STM 是訓練 trick，但真實 agent 運行時 STM 是連續流動的。論文沒有說明 deployment 時如何處理這個 gap（train-time 有 reset，inference-time 沒有）。

5. **遺忘機制是二元的**。Delete 是硬刪除，沒有 decay / soft forgetting / importance-based 衰減。現實中記憶不是「有或沒有」而是「強度遞減」。P8（Forgetful but Faithful）的 MaRS 在這方面更成熟。

6. **Filter 的固定閾值 θ=0.6 很 ad hoc**。什麼是「相關但要過濾」vs「相關且要保留」，靠一個全局 cosine threshold 決定太粗糙。不同任務、不同 domain 的最佳閾值顯然不同。

7. **沒有 memory poisoning / adversarial 分析**。如果 Stage 1 的 casual chat 包含惡意信息被 Add 進 LTM，Stage 3 會被 poisoned memory 誤導。安全性完全未討論。

## 對 MaC 的啟發

### 可直接借用
- **Memory ops 作為 tool-based actions 的 interface 設計**。AgeMem 的 6 tool schema（Add/Update/Delete/Retrieve/Summary/Filter）可以作為 MaC memory scheduler 的 low-level API 參考，但我們的 tool 操作的對象是 S-expression 而非 flat text。
- **三維 reward function 設計**。R_task + R_context + R_memory 的分解方式可以被 MaC 的 executor 評估器直接採用。特別是 R_context 的 preventive reward（主動壓縮）和 R_memory 的 maintenance reward（鼓勵 update/delete）。

### 需修改後使用
- **三階段訓練的概念可以映射到 MaC 的 compile → optimize → execute 管線**。但 MaC 不靠 RL 訓練——我們的 memory compilation 本身就是程式變換，不需要從 reward 中學。差異在於 AgeMem 是 learned policy，MaC 是 symbolic compilation。
- **Step-wise GRPO 的 credit assignment 思路**，但需要改成 finer-grained：MaC 的 S-expression 有明確的 provenance（哪條規則觸發了哪條記憶），可以做到 per-memory-operation 的 attribution，比 uniform broadcast 精確得多。

### 填補的 gap
- AgeMem 用實驗數據證明了「統一 LTM/STM 管理比分離管理效果好」這個假說（+4.82pp over best baseline）。這是 MaC 論文 Introduction 中需要引用的 key evidence——我們聲稱記憶應該是 first-class 的可執行對象，AgeMem 的實驗支持「統一管理 > 分離管理」的前提。
- 暴露了 flat representation 的天花板：即使有最好的 policy，flat text memory 的 MQ 只到 0.605。MaC 的 argument 正是：structured + executable representation 可以突破這個天花板。

## 關鍵引用（待追蹤）

1. **Memory-R1 (yan2025memory)**：P13 已在 reading-list，RL-trained memory extraction，和 AgeMem 互補。
2. **ReSum (wu2025resum)**：STM 壓縮的 baseline，periodic summarization 方法。
3. **Trinity framework (pan2025trinity)**：AgeMem 用的 RL 訓練框架，可能對 MaC 實驗有用。
4. **Zep (rasmussen2025zep)**：temporal knowledge graph 式記憶，和 MAGMA (P28) 的 multi-graph 路線相關。

## 我的思考

這篇論文最重要的貢獻不在技術細節，而在於**建立了一個令人信服的 empirical argument**：LTM 和 STM 不該被分開管理，agent 應該自主決定記憶操作。這和 MaC 的哲學高度一致——我們也認為記憶不該是被動的外部模組。

但 AgeMem 和 MaC 的分歧在於「自主」的實現方式：
- AgeMem 靠 **RL 訓練** 讓 agent 學會何時呼叫 tool → 是 learned behavior
- MaC 靠 **符號表示** 讓記憶本身攜帶計算邏輯 → 是 structural capability

AgeMem 的 agent 學會了「何時記」和「何時忘」，但記下來的東西仍然是惰性的 text。MaC 的記憶不只是被記住和被取回——它自己可以執行、可以觸發其他記憶、可以自我修改。這是 representation power 層面的根本差異。

一個好的類比：AgeMem 像一個學會了如何使用圖書館的人（知道什麼書值得借、什麼時候該還），而 MaC 是讓書本身會互相推薦、自動更新、在被閱讀時改變讀者。

從 positioning 角度，MaC 論文可以這樣定位 AgeMem：「AgeMem 證明了統一記憶管理的價值，但它的 learned policy + flat representation 路線有兩個瓶頸：(1) credit assignment 的粗糙性限制了 policy quality 的上限；(2) text-only memory 無法攜帶計算邏輯。MaC 用 executable S-expression 從根本上繞過這兩個瓶頸。」

對我們的系統（OpenClaw 的 memory-lancedb-pro + lossless-claw context compaction）的啟示：AgeMem 的 preventive reward 概念很值得借鑒——在 context compaction 時不只看「壓了多少」，還看「是否在 overflow 前就主動壓」。目前 lossless-claw 是被動觸發的（context 達到閾值才壓縮），如果能加入預防性壓縮的概念，可能減少壓縮時的信息損失。
