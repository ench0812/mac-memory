---
date: 2026-03-07
type: paper-notes
paper_id: P4
arxiv: 2512.13564
tags: [survey, memory, agents, comprehensive, taxonomy]
relevance_to_mac: 5/5
quality: 5/5
status: read
---

# Memory in the Age of AI Agents — Survey 精讀筆記

**論文**: Hu et al. (2025). "Memory in the Age of AI Agents: A Comprehensive Survey."
**規模**: 107 頁、800+ 引用，截至 2025 年最全面的 AI Agent 記憶系統 survey
**作者群**: 新加坡國立大學、清華、浙大等多校聯合

## 一句話總結
這篇 survey 用「形式（Forms）→ 功能（Functions）→ 動態（Dynamics）」三維度框架，系統化整理了 AI Agent 記憶領域的全部研究，是目前最完整的 agent memory 分類學。

---

## 核心框架：Forms × Functions × Dynamics

### 1. Forms（記憶載體，§3）— 記憶存在哪裡？

| 層次 | 載體 | 說明 | 代表 |
|------|------|------|------|
| Token-level | 1D/2D/Graph/Tree | 以自然語言/結構化文字存於外部 | Mem0, A-MEM, HippoRAG |
| Latent | KV-cache, soft tokens | 壓縮進 attention 的隱空間 | ICAE, MemGen, Titans |
| Parametric | 權重編輯/LoRA/MoE | 記憶內化到模型參數 | WISE, M+, MemoryLLM |

**關鍵洞察**: Token-level 是最可解釋但最耗 context 的；Parametric 最省空間但最不可控。三者的 trade-off 是核心架構決策。

### 2. Functions（記憶功能，§4）— 記憶用來做什麼？

三大支柱，橫跨兩個時間域（長期 vs 短期）：

#### 2a. Factual Memory（事實記憶）
- **User factual**: 使用者偏好、對話歷史、承諾 → 一致性
- **Environment factual**: 環境狀態、文件、其他 agent 能力 → 世界模型
- 確保 **consistency（一致性）+ coherence（連貫性）+ adaptability（適應性）**

#### 2b. Experiential Memory（經驗記憶）
三層抽象：
1. **Case-based**: 原始軌跡/方案 → 高保真但耗空間（ExpeL, Memento, JARVIS-1）
2. **Strategy-based**: 抽象為策略/洞察/工作流 → 可遷移（AWM, H2R, Dynamic Cheatsheet）
3. **Skill-based**: 編譯為可執行代碼/API/MCP → 直接可調用（Voyager, SkillWeaver, Alita）
4. **Hybrid**: 多層混合（ExpeL, G-Memory, Memp）

> 🔥 **對 MaC 的啟發**: 我們的 S-expression 記憶正是在做「Skill-based Memory」的事——把記憶編譯成可執行結構。但我們更進一步：讓記憶自帶觸發條件和衰減規則，這在 survey 中尚未被系統性討論。

#### 2c. Working Memory（工作記憶）
- **Single-turn**: Input condensation（壓縮）+ Observation abstraction（抽象）
- **Multi-turn**: State consolidation + Hierarchical folding + Cognitive planning
- 核心問題：如何在有限 context window 中維持任務狀態

### 3. Dynamics（記憶動態，§5）— 記憶如何運作？

三個基本過程形成循環：

```
Memory Formation（形成）
    ↓
Memory Evolution（演化）
    ↓
Memory Retrieval（檢索）
    ↓ (feedback)
    ↑ (回到 Formation)
```

#### 3a. Memory Formation（§5.1）— 如何提取記憶？
五種策略：
1. **Semantic Summarization** — 增量式 vs 分區式摘要
2. **Knowledge Distillation** — 從軌跡蒸餾事實/經驗
3. **Structured Construction** — 建構知識圖譜/樹/筆記網路
4. **Latent Representation** — 編碼進向量/KV 空間
5. **Parametric Internalization** — 寫入模型權重

#### 3b. Memory Evolution（§5.2）— 如何精煉記憶？
三個機制：
1. **Consolidation（鞏固）**: Local → Cluster → Global 三層整合
2. **Updating（更新）**: 衝突解決 + 參數編輯
3. **Forgetting（遺忘）**: 基於時間/訪問頻率/價值的修剪

#### 3c. Memory Retrieval（§5.3）— 如何使用記憶？
四階段管線：
1. **Timing & Intent** — 何時/為何檢索（自動判斷 vs 主動觸發）
2. **Query Construction** — 分解 vs 重寫查詢
3. **Retrieval Strategies** — 詞彙/語義/圖譜/混合檢索
4. **Post-Retrieval** — 重排序 + 過濾 + 聚合壓縮

---

## 前沿方向（§7）

1. **RL-optimized Memory** — 用 RL 學習什麼該記、怎麼記、何時忘（Mem1, MemGen, Memory-R1）
2. **Multimodal Memory** — 目前仍無真正的全模態記憶系統
3. **Shared Memory in MAS** — 從孤立記憶 → 共享認知基底
4. **Memory for World Models** — 記憶作為世界模型的時間一致性基石
5. **Trustworthy Memory** — 隱私、可解釋性、抗幻覺三大支柱
6. **Human-Cognitive Connections** — 從靜態儲存 → 建構性重構（像人類大腦那樣）
   - 離線鞏固（類似「睡眠」）→ 記憶重組
   - 生成式記憶（Generative Memory）→ 按需合成而非精確回放

---

## 與 MaC 研究的關聯分析

### 我們在哪裡？
MaC 的定位在 survey 框架中清晰可見：

| Survey 維度 | MaC 對應 |
|-------------|----------|
| Forms: Token-level (2D Graph) | S-expression = 結構化 token-level，但具備可執行性 |
| Functions: Skill-based Memory | 記憶自帶觸發規則 ≈ skill + strategy 混合 |
| Dynamics: Formation + Evolution | S-expression 的編碼 = formation；衰減/修正 = evolution |

### MaC 的差異化貢獻
1. **記憶即代碼（Memory-as-Code）**: Survey 中 Skill-based Memory 討論了可執行記憶（Voyager 的 code snippets, Alita 的 MCP），但沒有論文提出「記憶本身就是程式」的 homoiconic 設計。我們的 S-expression 讓記憶同時是資料和程式。

2. **內建生命週期**: Survey §5.2 的 Evolution 機制（consolidation, forgetting）都是*外部*施加的。MaC 的記憶自帶衰減規則（decay-rule）和信心度（confidence），生命週期*內嵌*於記憶本身。

3. **分層編譯**: Survey §3 討論了不同 carrier（token/latent/parametric），但沒有提出同一條記憶根據消費者能力「編譯」成不同層次的概念。我們的 L1/L2/L3 分層正是這個方向。

4. **AI 的 Mentalese**: Survey §7.8 提到 human-cognitive connections，討論了建構性記憶重構，但沒有觸及「AI 需要自己的內部表徵語言」。MaC 的 S-expression = AI 的 Mentalese 假說，是一個全新的理論貢獻。

### 可引用的 positioning
> "While existing surveys categorize agent memory by form, function, and dynamics (Hu et al., 2025), the field lacks a unified framework where memory items are simultaneously data and program. Memory-as-Code fills this gap by proposing homoiconic S-expressions as the representational primitive, enabling memories to encode their own retrieval triggers, decay policies, and cross-reference links."

---

## 重要參考文獻（從 survey 挖掘的新線索）

### 必讀（加入 reading list）
- **Memory-R1** (Yan et al., 2025c) — RL-trained memory extraction，與我們的「可學習記憶形成」相關
- **Mem-α** (Wang et al., 2025p) — Learnable insight extraction policy
- **Dynamic Cheatsheet** (Suzgun et al., 2025) — 推理時動態累積策略記憶
- **EverMemOS** (Hu et al., 2026a) — 自組織記憶操作系統
- **MemVerse** (Liu et al., 2025e) — 結合 parametric + token-level 記憶

### 值得追蹤
- **Context-Folding** (Sun et al., 2025b) — 深度研究的上下文壓縮
- **Mem1** (Zhou et al., 2025b) — RL 優化的記憶摘要
- **PREMem** (Kim et al., 2025b) — 預測+召回增強記憶
- **MemGen** (Zhang et al., 2025d) — 生成式記憶 token（latent memory）

---

## 我的觀察與批判

### 優點
- **極其全面**: 107 頁涵蓋 800+ 論文，分類學清晰，圖表精美
- **三維框架精巧**: Forms × Functions × Dynamics 能定位任何記憶系統
- **前沿方向有深度**: 不只列舉，有具體的 future perspective

### 不足
1. **缺乏量化比較**: 幾乎純定性分類，沒有 benchmark 結果對比
2. **忽略「記憶的自我意識」**: 討論了記憶的形式/功能/動態，但沒有討論 agent 對自身記憶的元認知（metacognition about memory）
3. **執行性 vs 描述性**: Survey 把記憶當「資料」分類，但沒有探索記憶作為「程式」的可能——這正是 MaC 要做的

### 最深刻的一句
> "Future systems may utilize generative memory where the agent synthesizes latent memory tokens on demand, mirroring the brain's reconstructive nature." (§7.8)

這跟 MaC 的方向高度吻合——記憶不是被動回放，而是主動重構。

---

## 閱讀評分
- 相關性: ⭐⭐⭐⭐⭐ (5/5) — 這是 MaC 論文 Related Work 的骨架
- 品質: ⭐⭐⭐⭐⭐ (5/5) — 截至目前最全面的 survey
- 新洞察: ⭐⭐⭐⭐ (4/5) — 框架本身是貢獻，但缺量化
- 可引用度: ⭐⭐⭐⭐⭐ (5/5) — 必引，用於 positioning

*精讀完成: 2026-03-07 🐭*