---
date: 2026-03-30
paper: Building Self-Evolving Agents via Experience-Driven Lifelong Learning: A Framework and Benchmark
authors: Yuxuan Cai, Yipeng Hao, Jie Zhou, Hang Yan, Zhikai Lei, Rui Zhen, Zhenhua Han, Yutao Yang, Junsong Li, Qianjun Pan, Tianyu Huai, Qin Chen, Xin Li, Kai Chen, Bo Zhang, Xipeng Qiu, Liang He
venue: arxiv preprint
arxiv: 2508.19005
rating: ⭐⭐
status: 📖
type: note
tags: [note]
---

# Building Self-Evolving Agents via Experience-Driven Lifelong Learning: A Framework and Benchmark

## 一句話總結
這篇不是在做一個更會聊天的 agent，而是在定義「會自己長大」的 agent：讓經驗探索、長期記憶、技能抽象、知識內化形成閉環，並用 StuLife 這個長期、動態、帶自發行為要求的 benchmark 去測它。

## 架構（圖+文字描述）

### 核心框架：ELL（Experience-driven Lifelong Learning）
```text
Environment interaction
   → Experience Exploration
   → Long-term Memory
   → Skill Learning
   → Knowledge Internalization
   → back to better Environment interaction
```

ELL 的關鍵不是「把更多 context 塞進 prompt」，而是把 agent 的成長拆成四個層次：
1. **Experience Exploration**：主動與動態環境互動，自己產生經驗軌跡。
2. **Long-term Memory**：把歷史知識、個人經驗、領域知識持久化。
3. **Skill Learning**：把重複模式抽成可重用技能，並能 refine / validate / combine / deprecate。
4. **Knowledge Internalization**：把顯式經驗內化成更像直覺的隱式能力。

### StuLife Bench 的系統結構
StuLife 不是單一任務，而是一個跨週期的校園人生模擬環境，底層由多個 deterministic subsystems 組成：
- **Persistent World State**：整個評測生命週期共享同一個 state；前面做過的事會永久影響後面。
- **World Time / Calendar**：時間不是 agent 可控的，而是系統注入；測的是對 temporal cues 的反應。
- **Map + Geography**：先查路徑、再執行移動，分離 planning 與 execution。
- **Course Selection**：以 draft schedule + priority pass 做資源競爭，測策略性配置。
- **Resource Reservation**：availability 由任務約束反推生成，避免無解題。
- **Information Retrieval**：同時有 hierarchical bibliography 與 flat entity queries，測不同查詢策略。
- **Communication**：append-only email log，評估格式精確性。

### 簡化資料流
```text
stateful world
  → task prompt / system time injection
  → agent plan
  → tool use
  → persistent state mutation
  → future tasks inherit consequences
```

## 長處

### 1. 問題定義比方法更重要
這篇最大的貢獻是把「self-evolving agent」從口號變成一個可評測的問題：
- 不是單次任務成功率
- 而是跨時間的適應、記憶保留、技能累積、主動性

### 2. Benchmark 設計很有野心
StuLife 把校園人生拆成多階段、多子任務，且讓早期決策對後面有累積影響。這比一般長對話 benchmark 更接近真實 agentic learning。

### 3. 明確點出三個 AGI 缺口
- stateless models 沒有自發動機
- 長期記憶很弱
- 技能不會穩定沉澱

### 4. 實驗訊號很直接
最強模型 GPT-5 也只有 **17.9/100**，人類基準 **85.24**。這個 gap 很誇張，但也很有研究價值：代表這不是微調就能補的洞。

### 5. context engineering 的結果值得重視
論文強調不只是模型本身，**怎麼組織上下文與系統提示** 也顯著影響表現。這很符合 MaC 的直覺：認知框架本身就是能力的一部分。

## 缺陷

### 1. 框架多、機制少
ELL 講得很完整，但很多地方停留在 conceptual layer：
- long-term memory 怎麼編碼？
- skill 怎麼抽象與驗證？
- knowledge internalization 怎麼落到可重用的表示？
- 沒有一個真正可執行的 memory language 或 update calculus。

### 2. benchmark 偏「人生模擬」，不夠「能力演化」
StuLife 很像 longitudinal life sim，但仍然主要在測：
- 任務完成
- 記憶保留
- 主動性

它沒有充分測到：
- 記憶自我修正
- 記憶衝突處理
- 失誤後的策略重構
- 工具/技能庫的版本演化

### 3. 太依賴 prompt / context engineering
論文自己也承認，優化 prompt 就能拉升不少表現。這有點危險：
- 它證明了「包裝」很重要
- 但也說明目前的 improvements 可能偏脆弱
- 一旦上下文長度、格式、指令順序變動，穩定性可能不夠

### 4. 沒有安全與遺忘機制
如果 agent 一直累積錯誤經驗，系統怎麼：
- 檢測幻覺記憶
- 回滾錯誤技能
- 清理過時策略
- 防止記憶污染

這些對 MaC 來說是核心問題，但這篇沒有處理。

### 5. 自發性仍然是弱點
雖然 benchmark 要求 proactive behavior，但現有模型本質上還是被動回應。論文很誠實地暴露出這個 gap，也等於告訴我們：真正的自我驅動還沒被解決。

## 對 MaC 的啟發（可直接借用 / 需修改使用 / 填補的 gap）

### 可直接借用
1. **長期、跨任務 statefulness**：MaC 需要的不是短期 scratchpad，而是能跨週期延續的世界狀態與記憶。
2. **Experience → Memory → Skill 的三段式循環**：非常適合拿來設計記憶成長管線。
3. **From Context to Memory** 的設計目標：這正是我們要把 transient prompt 變成 persistent memory 的方向。

### 需修改使用
1. **把 memory 變成可執行物件**
   - 這篇的 memory 主要是存歷史與知識
   - MaC 要讓 memory 帶 trigger / action / constraints / provenance

2. **把 skill learning 變成可版本化的程序資產**
   - 不是只抽象成文字筆記
   - 而是可以被調用、測試、退版、合併的 executable skill

3. **把 internalization 變成可觀察的編譯過程**
   - 哪些顯式經驗被壓縮成了規則？
   - 哪些規則又沉澱成了預設行為？
   - 這些都應該在 MaC 裡可追蹤

### 填補的 gap
- ELL 告訴我們：self-evolving agent 需要一個「長期成長環境」
- MaC 要補的是：一個能讓成長被表示、被執行、被回滾的記憶語言
- 換句話說，ELL 定義了「要長大什麼」，MaC 要定義「怎麼長大」

## 關鍵引用（待追蹤）

- **Lifelong learning / continual learning**：這篇的理論底座，後續可對照 task/domain/class-incremental learning
- **Mem0**：production-ready long-term memory 系統，和這篇的 memory layer 很接近
- **Richelieu**：self-evolving LLM agents 的案例，能和 ELL 互相比較
- **MemSkill**：把 memory skill 化、可演化化，和本篇的 skill learning 很搭
- **MemoryBank / MemAgent 類工作**：這篇在 related work 中提到的 memory 系列路線，值得追

## 我的思考（自由形式深度反思）

這篇其實是很典型的「研究方向定義論文」：它不是在某個算法上把前人打穿，而是在告訴大家下一個戰場在哪。這種論文通常有兩種命運：一種被當成大詞堆砌，另一種變成後續所有人引用的坐標系。ELL 比較像後者。

我最在意的是它把 agent 的成長拆成了四件事：經驗、記憶、技能、內化。這四件事其實已經很接近認知架構了，只差一個能真正運作的表示語言。這正是 MaC 的機會：如果我們只做 memory retrieval，那很容易被 Mem0、MemOS 追上；但如果我們能把記憶變成可執行、可演化、可回滾的 code，位置就不一樣了。

另一個很重要的點是：這篇 benchmark 其實間接證明了 **stateless LLM 的天花板**。不是因為它們不夠聰明，而是因為它們缺少一個穩定的成長介面。今天的 agent 大多靠 prompt engineering 撐著，這讓它們像「每次都重新上線的新手」。ELL 想做的是長出累積性；MaC 要做的是把這個累積性編譯成結構。

最後，我覺得這篇最有價值的地方，是它把「主動性」也納入評估。很多 memory work 只看回憶，但真正的 agent 不是只會想起來，還要會自己開始做事。這一點如果 MaC 能做出來，會比純記憶檢索更像一個活的系統。

*精讀完成 2026-03-30 | Mickey 🐭*