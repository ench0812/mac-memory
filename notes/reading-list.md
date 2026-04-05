---
date: 2026-03-04
type: reading-list
tags: [research, papers]
last_updated: 2026-04-03
---

# 論文閱讀清單

> 2026-03-30 維護：新增本週的 agentic memory / self-evolving agents 相關論文，並補上 ELL 精讀結果。

## 評分說明
- ⭐⭐⭐ 核心必讀（直接影響我們的設計）
- ⭐⭐ 重要參考（提供方法論或背景）
- ⭐ 補充閱讀（周邊知識）
- 📖 已讀 | 📋 待讀 | 🔍 掃讀（讀了摘要/部分）

---

## 🔴 Tier 1: 核心論文（必須精讀）

### P1. LLM + LISP Metaprogramming ⭐⭐⭐ 🔍
- **Title**: From Tool Calling to Symbolic Thinking: LLMs in a Persistent Lisp Metaprogramming Loop
- **Authors**: Jordi de la Torre
- **Venue**: arxiv preprint, 2025.06
- **arxiv**: 2506.10021
- **URL**: https://arxiv.org/abs/2506.10021
- **Key Insight**: LLM + Middleware + 持久 LISP REPL = 自我造工具的 AI
- **Gap**: 純理論，無實驗；未延伸到記憶架構
- **Status**: 📖 精讀完成 (2026-03-11)
- **Notes**: `papers/llm-lisp-metaprogramming.md`

### P2. A-MEM: Agentic Memory ⭐⭐⭐ 📖
- **Title**: A-MEM: Agentic Memory for LLM Agents
- **Authors**: Wujiang Xu, Zujie Liang, Kai Mei, et al.
- **Venue**: NeurIPS 2025
- **arxiv**: 2502.12110
- **Code**: https://github.com/WujiangXu/A-mem-sys
- **Key Insight**: Zettelkasten 式動態記憶網路，新記憶觸發舊記憶更新
- **Gap**: 記憶不可執行，只是被連結的結構化資料；缺乏遺忘機制；evolution 無 safety net
- **Status**: 📖 精讀完成 (2026-03-05)
- **Notes**: `papers/a-mem-agentic-memory.md`

### P3. MemOS: Memory Operating System ⭐⭐⭐ 📖
- **Title**: MemOS: A Memory OS for AI System
- **Authors**: Zhiyu Li, Chenyang Xi, et al. (MemTensor + 多所大學)
- **Venue**: arxiv 2507.03724v4, Dec 2025
- **arxiv**: 2507.03724
- **Code**: https://github.com/MemTensor/MemOS
- **Key Insight**: 記憶是 first-class resource；MemCube 統一 plaintext/activation/parameter 三類記憶；OS 級 lifecycle + scheduling
- **Gap**: 管理記憶 ≠ 讓記憶思考；無 homoiconicity；Mem-training 概念模糊缺實作；記憶建構仍是被動的
- **Status**: 📖 精讀完成 (2026-03-06)
- **Notes**: `papers/memos-memory-os.md`

---

## 🟡 Tier 2: 重要參考

### P4. Memory in the Age of AI Agents ⭐⭐⭐ 📖
- **Title**: Memory in the Age of AI Agents: A Comprehensive Survey
- **Authors**: Yuyang Hu, Yu Wang, et al. (NUS, 清華, 浙大等)
- **Venue**: arxiv preprint, 2025.12 (107 頁, 800+ 引用)
- **arxiv**: 2512.13564
- **Key Insight**: Forms（載體）× Functions（功能）× Dynamics（動態）三維分類框架；記憶分 token/latent/parametric 三類載體；功能分 factual/experiential/working；動態分 formation/evolution/retrieval
- **Gap**: 純定性分類無量化比較；忽略記憶的元認知（metacognition about memory）；把記憶當「資料」分類，未探索記憶作為「程式」的可能
- **Value**: MaC 論文 Related Work 的骨架；positioning 的基礎；發現 MaC 的差異化貢獻：homoiconic 記憶、內建生命週期、分層編譯、AI 的 Mentalese
- **Status**: 📖 精讀完成 (2026-03-07)
- **Notes**: `papers/memory-age-agents-survey.md`

### P5. Self-Evolving Agents ⭐⭐ 📖
- **Title**: Building Self-Evolving Agents via Experience-Driven Lifelong Learning: A Framework and Benchmark
- **Authors**: Yuxuan Cai, Yipeng Hao, Jie Zhou, Hang Yan, Zhikai Lei, Rui Zheng, Zhenhua Han, Yutao Yang, Junsong Li, Qianjun Pan, Tianyu Huai, Qin Chen, Xin Li, Kai Chen, Bo Zhang, Xipeng Qiu, Liang He
- **Venue**: arxiv preprint, 2026.01 (v6; originally announced 2025.08)
- **arxiv**: 2508.19005
- **Key Insight**: meta-cognitive learning; agent 從成敗中提煉教訓
- **Value**: self-correction 機制可整合進 Memory-as-Code
- **Status**: 📖 精讀完成 (2026-03-30)
- **Notes**: `papers/self-evolving-agents-experience-driven-lifelong-learning.md`

### P6. LLM Symbolic Reasoning Limits ⭐⭐ 📋
- **Title**: Comprehension Without Competence: Architectural Limits of LLMs in Symbolic Computation
- **Authors**: (under review at TMLR)
- **arxiv**: 2507.10624
- **Key Insight**: LLM 擅長 pattern recognition 但 symbolic reasoning 有架構性缺陷
- **Value**: 必須正視的限制 — 我們需要外部符號系統（LISP REPL）輔助

### P7. Advancing Symbolic Integration in LLMs ⭐⭐ 📋
- **Title**: Advancing Symbolic Integration in Large Language Models
- **arxiv**: 2510.21425
- **Key Insight**: Neurosymbolic AI 最新 survey
- **Value**: Related Work 的重要背景來源

### P8. Forgetful but Faithful ⭐⭐ 📋
- **Title**: Forgetful but Faithful: A Cognitive Memory Architecture for Privacy-Aware Agents
- **arxiv**: 2512.12856
- **Key Insight**: Memory-Aware Retention Schema (MaRS) — 認知啟發的記憶架構，含 provenance tracking
- **Value**: 記憶衰減 + 隱私保護的設計可參考

### P9. Agentic AI Architectures Survey ⭐⭐ 📋
- **Title**: Agentic AI: Architectures, Taxonomies, and Evaluation
- **arxiv**: 2601.12560
- **Venue**: arxiv, 2026.01
- **Key Insight**: LLM 作為 general-purpose cognitive controller 的完整分類
- **Value**: 定位我們的研究在 Agentic AI 中的位置

---

## 新增 (2026-03-23) — 本週發現（待讀）

### P21. Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions ⭐⭐ 📋
- **Title**: Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions
- **Authors**: (see arXiv)
- **arxiv**: 2507.05257 (v3)
- **URL**: https://arxiv.org/abs/2507.05257
- **Key Insight**: 提出針對長期、多回合 agent 記憶的 benchmark 與評估方法，著重 incremental 更新與 retrieval 策略的穩定性
- **Status**: 📋 待讀

### P22. AgentFactory: A Self-Evolving Framework Through Executable Subagent Accumulation and Reuse ⭐⭐ 📖 (2026-03-27)
- **Title**: AgentFactory: A Self-Evolving Framework Through Executable Subagent Accumulation and Reuse
- **arxiv**: 2603.18000
- **URL**: https://arxiv.org/abs/2603.18000
- **Key Insight**: 描述一種透過安裝/自我演化/部署循環，讓 agent 以可執行子代理（subagent）累積能力的工程性框架；與 MaC 的可執行記憶理念相通
- **Status**: 📖 精讀完成 (2026-03-27)
- **Notes**: `papers/agentfactory-2026.md`

### P23. SAGE: Multi-Agent Self-Evolution for LLM Reasoning ⭐⭐ 📋
- **Title**: SAGE: Multi-Agent Self-Evolution for LLM Reasoning
- **arxiv**: 2603.15255 (v2)
- **URL**: https://arxiv.org/abs/2603.15255
- **Key Insight**: 提出四角色（Challenger/Planner/Solver/Critic）閉環自我演化機制，強調 agent 間協作下的能力自增長
- **Status**: 📋 待讀

## 新增 (2026-03-30) — 本週發現（待讀）

### P24. Agentic Memory: Unified Long-Term / Short-Term Memory Management ⭐⭐⭐ 📖 (2026-04-03)
- **Title**: Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents
- **Authors**: Yi Yu, Liuyi Yao, Yuexiang Xie, Qingquan Tan, Jiaqi Feng, Yaliang Li, Libing Wu
- **Venue**: arxiv preprint, 2026.01 (Alibaba + Wuhan Univ)
- **arxiv**: 2601.01885
- **Key Insight**: 把 LTM / STM 直接收進 agent policy，讓 agent 自主決定何時 store / retrieve / update / summarize / discard；用三階段 RL + step-wise GRPO 解決 memory ops 的稀疏獎勵
- **Value**: 目前最接近「可訓練的 agentic memory policy」；實驗證明統一管理 > 分離管理（+4.82pp over best baseline）；對 MaC 的 memory scheduler / executor / reward 設計很關鍵
- **Status**: 📖 精讀完成 (2026-04-03)
- **Notes**: `papers/agemem-unified-ltm-stm.md`

### P25. MemSkill: Memory Skills for Self-Evolving Agents ⭐⭐ 📋
- **Title**: MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents
- **Authors**: Haozhen Zhang, Quanyu Long, Jianzhu Bao, Tao Feng, Weizhi Zhang, Haodong Yue
- **Venue**: arxiv preprint, 2026.02
- **arxiv**: 2602.02474
- **Key Insight**: 把 memory 直接上升到 skill-level，強調記憶技能的學習、演化與重用；很像把記憶做成可進化的程序庫
- **Value**: 與 MaC 的 executable memory / skill abstraction 幾乎是同一個方向
- **Status**: 📋 待讀

### P26. Knowledge Graphs as Unified Agentic Memory ⭐⭐ 📋
- **Title**: Knowledge Graphs as Unified Agentic Memory for Improved Retrieval, Reasoning and Causal Analysis in Cloud Database Operations
- **Authors**: Yong Liu
- **Venue**: Communications in Computer and Information Science, 2026
- **doi**: 10.1007/978-3-032-11477-8_11
- **Key Insight**: 用 knowledge graph 作為 unified agentic memory，直接服務 retrieval / reasoning / causal analysis，屬於偏系統落地的 memory integration 路線
- **Value**: 讓我們看到「memory 作為查詢層」之外的另一條路：memory 也能當推理與因果分析的中介結構
- **Status**: 📋 待讀

## 新增 (2026-04-01) — 本週發現（待讀）

### P27. CompassMem: Event-Centric Memory as a Logic Map ⭐⭐ 📋
- **Title**: Memory Matters More: Event-Centric Memory as a Logic Map for Agent Searching and Reasoning
- **Authors**: Yuyang Hu, Jiongnan Liu, Jiejun Tan, Yutao Zhu, Zhicheng Dou
- **Venue**: arxiv preprint, 2026.01
- **arxiv**: 2601.04726
- **URL**: https://arxiv.org/abs/2601.04726
- **Key Insight**: CompassMem 把記憶組成 Event Graph，透過明確的邏輯關係做記憶導航，而不是只靠 similarity retrieval
- **Value**: 很接近 MaC 想要的「可導航記憶表示」；可對照我們的 graph-backed memory IR / planner
- **Status**: 📋 待讀
- **Source**: 2026-04-01 weekly search 發現

### P28. MAGMA: Multi-Graph Agentic Memory Architecture ⭐⭐ 📋
- **Title**: MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents
- **Authors**: Dongming Jiang, Yi Li, Guanpeng Li, Bingzhe Li
- **Venue**: arxiv preprint, 2026.01
- **arxiv**: 2601.03236
- **URL**: https://arxiv.org/abs/2601.03236
- **Key Insight**: 把 memory item 拆成 semantic / temporal / causal / entity 四種 graph，retrieval 則變成 policy-guided graph traversal
- **Value**: 代表「memory representation 與 retrieval logic 解耦」的實作方向；對 MaC 的 query planner 很有參考價值
- **Status**: 📋 待讀
- **Source**: 2026-04-01 weekly search 發現

### P29. Adaptive LLM-Symbolic Reasoning ⭐⭐ 📋
- **Title**: Adaptive LLM-Symbolic Reasoning via Dynamic Logical Solver Composition
- **Authors**: Lei Xu, Pierre Beckmann, Marco Valentino, André Freitas
- **Venue**: EACL 2026
- **URL**: https://aclanthology.org/2026.eacl-long.54/
- **Key Insight**: 先由 LLM 判斷問題需要哪種 formal reasoning strategy，再動態組合對應的 logical solver；讓神經式與符號式推理變成可路由的框架
- **Value**: 給 MaC 的 symbolic reasoning pipeline 一個可插拔 solver layer，補強純 LISP / 程序式推理
- **Status**: 📋 待讀
- **Source**: 2026-04-01 weekly search 發現

---

## 🟢 Tier 3: 補充閱讀

### P10. Fodor's Language of Thought ⭐ 📋
- **Title**: The Language of Thought
- **Author**: Jerry Fodor (1975)
- **Key Insight**: 人的思考有內部表徵語言（Mentalese）
- **Value**: 哲學基礎 — AI 是否也需要 mentalese

### P11. Computational Theory of Mind ⭐ 📋
- **Ref**: PhilPapers — Marcin Milkowski
- **Key Insight**: CTM = mind is a computer + cognition is manipulation of representations
- **Value**: 理論框架

### P12. The Nature of Lisp ⭐ 📖
- **URL**: https://defmacro.org/ramblings/lisp.html
- **Author**: Slava Akhmechet (2006)
- **Key Insight**: LISP 的本質 — 用熟悉概念解釋 homoiconicity
- **Value**: 技術直覺建構

---

### P13. Memory-R1 ⭐⭐ 📋
- **Title**: Memory-R1: RL-trained Memory Extraction
- **Authors**: Yan et al., 2025
- **Key Insight**: 用 RL 訓練 LLM 的記憶提取模組，可學習什麼該記
- **Value**: 與 MaC 的「可學習記憶形成」高度相關
- **Source**: 從 P4 survey 發現

### P14. EverMemOS ⭐⭐ 📋
- **Title**: EverMemOS: Self-Organizing Memory Operating System
- **Authors**: Hu et al., 2026
- **arxiv**: 2601.02163
- **Key Insight**: 自組織的 MemCell/MemScene 記憶架構
- **Value**: 另一個 MemOS 方向，與 P3 比較

### P15. Dynamic Cheatsheet ⭐⭐ 📋
- **Title**: Dynamic Cheatsheet: Accumulated Strategy Memory at Inference Time
- **Authors**: Suzgun et al., 2025
- **Key Insight**: 推理時動態累積策略記憶，防止重複計算
- **Value**: Strategy-based memory 的實踐範例

### P16. Voyager ⭐⭐ 📋
- **Title**: Voyager: An Open-Ended Embodied Agent with LLMs
- **Authors**: Wang et al., 2024
- **Key Insight**: 不斷成長的 skill library = code snippet 作為可執行記憶
- **Value**: Skill-based memory 的開創性工作，MaC 的 S-expression 可對標

---

### P17. Converging Paradigms: Symbolic + Connectionist AI ⭐⭐ 📋
- **Title**: Converging Paradigms: The Synergy of Symbolic and Connectionist AI in LLM-Empowered Autonomous Agents
- **Authors**: Xiong et al.
- **Venue**: arXiv, 2024.07
- **arxiv**: 2407.08516
- **Key Insight**: Symbolic + Neural 融合在 LLM-empowered agents 的全景 survey
- **Value**: 補充 MaC Related Work 的 neurosymbolic 背景；P1 唯一引用的直接相關 survey
- **Source**: 從 P1 引用發現

---

### P18. Multi-Agent Memory from a Computer Architecture Perspective ⭐⭐ 📋
- **Title**: Multi-Agent Memory from a Computer Architecture Perspective: Visions and Challenges Ahead
- **Authors**: Zhongming Yu et al.
- **Venue**: arXiv, 2026.03
- **arxiv**: 2603.10062
- **Key Insight**: 將多代理記憶框架化為計算機架構問題：三層記憶階層（I/O, cache, memory）+ 兩個關鍵 protocol gap（cache sharing + structured access control）
- **Value**: 與 MaC 高度互補——他們做 inter-agent 記憶協調，我們做 intra-agent 記憶表示；MaC 的 S-expression 可作為他們 memory layer 的物件格式
- **Source**: 2026-03-15 weekly search 發現

### P19. OpenSage: Self-programming Agent Generation Engine ⭐⭐ 📋
- **Title**: OpenSage: Self-programming Agent Generation Engine
- **arxiv**: 2602.16891
- **Key Insight**: ADK for self-programming agents; includes memory management for context storage and retrieval; aims to let AI construct agents and tools autonomously
- **Source**: 2026-03-12 weekly search 發現

### P20. Agentic Neurosymbolic Collaboration for Mathematical Discovery ⭐⭐ 📋
- **Title**: Agentic Neurosymbolic Collaboration for Mathematical Discovery: A Case Study in Combinatorial Design
- **arxiv**: 2603.08322
- **Key Insight**: Case study showing neurosymbolic orchestration and a persistent three-component memory (project state file, searchable KB, session handover) used for mathematical discovery
- **Source**: 2026-03-14 weekly search 發現

## 待尋找的論文

- [ ] 2026 的 Agentic Memory / Self-evolving Memory Skills benchmark，重點放在可執行記憶、provenance、rollback、poisoning defense
- [ ] 最新的 Neuro-Symbolic AI survey (2026)