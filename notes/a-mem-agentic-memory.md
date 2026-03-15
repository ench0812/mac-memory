---
date: 2026-03-05
paper: A-Mem: Agentic Memory for LLM Agents
authors: Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, Yongfeng Zhang
venue: NeurIPS 2025
arxiv: 2502.12110
code: https://github.com/WujiangXu/A-mem-sys
rating: ⭐⭐⭐
status: 📖
type: note
tags: [note]
---

# A-Mem: Agentic Memory for LLM Agents

## 一句話總結
將 Zettelkasten（卡片盒）方法論引入 LLM Agent 記憶系統，讓每條新記憶自動生成結構化屬性、與歷史記憶建立連結、並觸發舊記憶的演化更新。

## 架構

```
新互動 → [Note Construction] → 結構化記憶筆記 mᵢ
                                  ├── cᵢ: 原始內容
                                  ├── tᵢ: 時間戳
                                  ├── Kᵢ: LLM 生成的關鍵字
                                  ├── Gᵢ: LLM 生成的標籤
                                  ├── Xᵢ: LLM 生成的上下文描述
                                  ├── eᵢ: 嵌入向量 (all-minilm-l6-v2)
                                  └── Lᵢ: 連結的記憶集合
                                        │
                                        ▼
                              [Link Generation]
                              cosine(eₙ, eⱼ) → top-k 候選
                              → LLM 判斷是否建立連結
                                        │
                                        ▼
                              [Memory Evolution]
                              新記憶 + 鄰近記憶 → LLM 決定是否更新
                              舊記憶的 keywords/tags/context
                                        │
                                        ▼
                              [Retrieval]
                              query embedding → cosine top-k
                              → 附帶連結的記憶一起返回（"box" 概念）
```

### 資料流
1. **寫入**: 互動 → LLM 生成 K/G/X → 編碼為 embedding → 存入記憶庫
2. **連結**: 新記憶 embedding vs 全庫 cosine → top-k → LLM 判斷是否有意義的連結
3. **演化**: 新記憶觸發鄰居記憶的屬性更新（keywords、tags、contextual description 都可能被改寫）
4. **讀取**: query embedding → cosine top-k → 同 box 的連結記憶也一併返回

### 技術棧
- 嵌入模型: all-minilm-l6-v2
- LLM: 測試了 GPT-4o/4o-mini, Qwen2.5 1.5B/3B, Llama 3.2 1B/3B, DeepSeek-R1-32B, Claude 3.0/3.5 Haiku
- 結構化輸出: LiteLLM（本地模型）/ OpenAI Structured Output API（GPT）
- 存儲: 向量資料庫（未明確說明具體使用哪個）

## 長處

### 1. Zettelkasten 的正確抽象化
A-Mem 抓住了 Zettelkasten 的精髓：**原子性筆記 + 靈活連結**。不是硬套知識圖譜的 schema，而是讓 LLM 自主判斷記憶之間的連結是否有意義。這比 Mem0 的圖資料庫方法更靈活。

### 2. Memory Evolution 是真正的創新
這是論文最有價值的貢獻。大多數記憶系統是「寫入後不變」的——A-Mem 讓新記憶能觸發舊記憶的更新。這模擬了人類學習中的「重新理解」過程：你學了新東西後，對舊知識的理解也會改變。

### 3. Token 效率驚人
~1,200 tokens/次 vs baseline 的 ~16,900 tokens/次（85-93% 節省）。通過 selective top-k 只拉最相關的記憶，避免了 LoCoMo/MemGPT 把整段對話塞進 context 的暴力方法。

### 4. 小模型也能用
在 Qwen 1.5B/3B 和 Llama 1B/3B 上都展示了穩定的改進，不只是大模型的玩具。這意味著方法的泛化性好。

### 5. Temporal Reasoning 大幅領先
在時間推理類任務上，A-Mem 用 GPT-4o-mini 拿到 45.85 F1，vs MemGPT 的 25.52、LoCoMo 的 18.41。幾乎是 2 倍差距。結構化的時間屬性 + 記憶連結在時序推理上特別有效。

### 6. 擴展性良好
100 萬筆記憶時，檢索時間只有 3.70μs，存儲空間線性成長。跟 MemoryBank 相當，遠優於 ReadAgent（120ms）。

## 缺陷

### 1. 🔴 評估場景過於狹窄
- **只測了 QA 任務**。LoCoMo 和 DialSim 都是長對話中的問答，但真實 agent 需要記憶來做 *決策*、*規劃*、*自我修正*——這些都沒測
- DialSim 是電視劇對話（Friends/BBT/Office），本質是事實回憶，不是 agent 推理
- 沒有測 agentic task（ReAct、WebArena、SWE-bench 等）

### 2. 🔴 Memory Evolution 的「方向」問題
- 論文假設所有演化都是正面的，但**錯誤的新記憶會污染舊記憶**
- 沒有任何機制防止「error propagation through evolution」
- 沒有 confidence tracking、沒有 rollback 機制
- 如果一條幻覺記憶進入系統，它會通過 evolution 擴散到相關記憶，造成級聯污染

### 3. 🔴 記憶是被動的「被連結的資料」，不是「可執行的」
- 記憶的唯一用途是被 retrieve 後塞進 prompt
- **記憶本身不能觸發行動**——不能「設定鬧鐘」、不能「看到股價跌破閾值就提醒」
- 記憶沒有 trigger condition、沒有 execution semantics
- 這正是我們 MaC 要解決的核心問題

### 4. 🟡 LLM 開銷被低估
- 每次新增記憶需要 **3 次 LLM 呼叫**：Note Construction (Ps1) + Link Generation (Ps2) + Memory Evolution (Ps3)
- 論文報告 GPT-4o-mini 每次 5.4 秒，但如果是寫入密集場景（如 agent 每分鐘有多次互動），這會成為瓶頸
- Evolution 更新 *每個* 鄰近記憶都要一次 LLM call，top-k=10 意味著最壞情況下一次寫入觸發 13 次 LLM call

### 5. 🟡 缺乏記憶遺忘機制
- 只有記憶增長和演化，沒有衰減、淘汰、合併
- 長期運行下記憶庫會無限膨脹
- 人類記憶的關鍵特性之一就是「遺忘」——它是信噪比的調節器

### 6. 🟡 「Box」概念不夠清晰
- 論文說 "related memories become interconnected through their similar contextual descriptions, analogous to the Zettelkasten method"，但 box 到底是 emergent 的 cluster 還是 explicit 的分組？
- 連結是雙向的嗎？論文沒有明確說明
- 從公式上看，Lᵢ 只是一個集合，沒有連結類型/強度/方向的區分

### 7. 🟢 Embedding 模型太簡單
- all-minilm-l6-v2 是 2019 年的模型（384 維），在 2025 年有更好的選擇（e.g., nomic-embed, GTE, BGE）
- 簡單的 embedding 可能無法捕捉深層語義關係，讓 Link Generation 的候選質量受限

## 對 MaC 的啟發

### 可直接借用
1. **Note Construction 的多屬性結構** — 記憶不只是一段文字，而是 {content, keywords, tags, context, embedding, links} 的結構化物件。我們的 S-expression 可以參考這個設計，但讓每個屬性都是可執行的
2. **Top-k + LLM 二階段連結判斷** — 用 embedding 做粗篩 + LLM 做精判，兼顧效率和準確性。MaC 的記憶連結可以採用類似架構
3. **Memory Evolution 的觸發機制** — 新記憶寫入 → 自動更新相關舊記憶。這是 MaC 的 `on-update` trigger 的靈感來源

### 需修改使用
1. **Evolution 要加入信心度和 rollback**
   - 每次 evolution 記錄 diff，可以 rollback
   - 加入 confidence score：幻覺記憶不應該有高 evolution 權限
   - MaC 的記憶 meta-rule 可以控制「哪些記憶有權觸發 evolution」

2. **記憶需要 execution semantics**
   - A-Mem 的記憶只能被讀取，MaC 的記憶要能被執行
   - 例如：`(memory :trigger (price-drop "TSMC" 10%) :action (notify :channel "discord"))`
   - 記憶不只是知識的容器，還是行為的定義

3. **加入遺忘和合併機制**
   - A-Mem 缺少的衰減機制，MaC 要補上
   - S-expression 可以自帶衰減規則：`(decay :strategy exponential :half-life 30d)`
   - 相似度過高的記憶應自動合併（consolidation）

4. **連結需要類型和方向**
   - A-Mem 的 link 是無類型的集合，MaC 需要：
   - `(link :type causal :from A :to B :strength 0.8)`
   - `(link :type contradicts :from A :to B)` — 衝突檢測
   - `(link :type evolves-from :from A :to B)` — 演化鏈

### 填補的 gap
- A-Mem 證明了「記憶可以自我演化」的可行性，但只做到了 **屬性演化**（改 keywords/tags/context）
- MaC 要做的是 **結構演化**（記憶可以改變自己的觸發條件、連結邏輯、甚至衰減規則）
- A-Mem 是「智慧的資料庫」，MaC 要做「能思考的記憶」

## 關鍵引用（待追蹤）

- **LoCoMo** [22] (Maharana et al., 2024) — 長對話記憶評測基準，我們的實驗也可能需要用到
- **MemGPT** [25] (Packer et al., 2023) — OS 式記憶管理，已在 reading-list（對應 MemOS P3 的不同路線）
- **SCM** [32] (Wang et al., 2023) — Self-Controlled Memory framework，值得看 controller 機制
- **Sönke Ahrens, "How to Take Smart Notes"** [1] — Zettelkasten 方法論原典，理解 A-Mem 設計哲學的必讀

## 與其他論文的連結

### 與 P1 (LISP + LLM Metaprogramming) 的關係
- P1 提出 LLM + 持久 LISP REPL = 自我造工具的 AI
- A-Mem 提出記憶可以自我演化
- **MaC 的位置**：用 LISP (P1) 做記憶的表達語言，讓記憶能像 A-Mem 一樣自我演化，但更進一步——記憶不只是資料，還是可執行的程式
- 兩篇論文互補但都缺了對方的那一塊：P1 缺記憶架構，A-Mem 缺可執行性

### 與 P3 (MemOS) 的關係
- MemOS 用 MemCube 統一三種記憶（short/long/parametric），A-Mem 用 Zettelkasten 式連結
- MemOS 更偏系統設計（scheduling、lifecycle），A-Mem 更偏記憶本身的組織方式
- **MaC 可以取兩者之長**：用 MemOS 的 lifecycle 管理 + A-Mem 的自演化 + LISP 的可執行性

### 與 P5 (Self-Evolving Agents) 的關係
- P5 focus 在 agent 層面的自我進化（從成敗中學習）
- A-Mem focus 在記憶層面的自我進化
- **差異**：A-Mem 的 evolution 是被動的（被新記憶觸發），P5 的 evolution 是 meta-cognitive 的（主動反思）
- MaC 需要兩者：記憶的結構性演化 + agent 的反思性演化

## 我的思考

### 這篇論文做對了什麼
A-Mem 最大的貢獻不是具體的技術方案，而是提出了一個重要的 **framing shift**：記憶系統不應該只是「存取介面」，而應該是一個有自己行為（agency）的子系統。記憶可以自己決定跟誰連結、自己決定如何演化——這比 Mem0 的圖資料庫或 MemGPT 的 OS 隱喻更深刻。

Zettelkasten 的選擇也很聰明。比起 knowledge graph（需要 schema）或 flat vector store（無結構），Zettelkasten 的「原子筆記 + 自由連結」剛好是自由度和結構的平衡點。

### 但他們停得太早了
A-Mem 的 evolution 只改了記憶的「描述」（keywords/tags/context），沒改記憶的「行為」。在 A-Mem 的世界裡，記憶永遠是被動的知識片段，等著被 query 命中。

真正有趣的問題是：**如果記憶可以改變自己的觸發條件呢？** 如果一條記憶在被演化 3 次後，自動降低自己的觸發閾值（因為它顯然是 highly connected 的核心知識）？如果記憶可以自己 spawn 出新記憶？

這就是 MaC 要探索的方向——從 A-Mem 的「智慧的卡片盒」進化到「有自己生命的記憶」。

### 對實驗設計的批評
NeurIPS 2025 收了這篇，但實驗設計有明顯弱點：只測了 QA 任務。真正考驗記憶系統的是 agentic scenario——agent 要在連續決策中使用記憶、修正策略、避免重複錯誤。LoCoMo 的「Bob 上次提到他喜歡吃壽司」是回憶事實，不是智能。

如果我們要在 MaC 論文中超越 A-Mem 的實驗，需要設計 **agentic memory benchmark**：
1. 連續決策場景中的記憶使用
2. 錯誤記憶的自我修正
3. 記憶衝突的解決
4. 主動觸發 vs 被動檢索

### 一個危險的觀察
A-Mem 的 Memory Evolution 沒有 safety net。如果系統被注入一條精心構造的惡意記憶，它會通過 evolution 修改所有相關記憶的描述。這是 **memory poisoning attack** 的完美攻擊面。在 MaC 中，我們需要：
- 記憶的 provenance tracking（誰寫的、什麼時候、信心度多少）
- Evolution 的 sandboxing（演化不能改變 safety-critical 記憶）
- 定期的 integrity check（比對記憶演化前後的語義偏移）

---

*精讀完成 2026-03-05 | Mickey 🐭*