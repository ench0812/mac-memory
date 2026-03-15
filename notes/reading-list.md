---
date: 2026-03-04
type: reading-list
tags: [research, papers]
last_updated: 2026-03-11
---

# 論文閱讀清單

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

### P5. Self-Evolving Agents ⭐⭐ 📋
- **Title**: Building Self-Evolving Agents via Experience-Driven Lifelong Learning
- **Authors**: (multiple)
- **Venue**: arxiv preprint, 2025.12
- **arxiv**: 2508.19005
- **Key Insight**: meta-cognitive learning; agent 從成敗中提煉教訓
- **Value**: self-correction 機制可整合進 Memory-as-Code

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

## 📡 追蹤來源（定期掃描）

### 論文追蹤
- arxiv cs.CL (Computation and Language): `https://arxiv.org/list/cs.CL/recent`
- arxiv cs.AI (Artificial Intelligence): `https://arxiv.org/list/cs.AI/recent`
- Semantic Scholar alerts: 關鍵字 "agentic memory" "symbolic LLM" "self-evolving agent"
- Google Scholar alerts: 追蹤 P1-P3 的引用

### 研究者追蹤
- **Wujiang Xu** (A-MEM): https://scholar.google.com/citations?user=... (待查)
- **MemTensor**: https://github.com/MemTensor
- **Awesome-Self-Evolving-Agents**: https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents
- **Awesome-LLM-Reasoning-with-NeSy**: https://github.com/LAMDASZ-ML/Awesome-LLM-Reasoning-with-NeSy

### 會議 deadline 追蹤
- **NeurIPS 2026**: 投稿約 2026 年 5 月
- **ICLR 2027**: 投稿約 2026 年 9-10 月
- **ACL 2026**: 投稿約 2026 年 1-2 月（可能已過）
- **EMNLP 2026**: 投稿約 2026 年 6 月
- **AAAI 2027**: 投稿約 2026 年 8 月

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

## 待尋找的論文

- [ ] 最新的 Neuro-Symbolic AI survey (2026)
- [ ] Clojure / modern LISP 在 AI 中的應用
- [ ] 記憶自我修改 (self-modifying memory) 相關工作
- [ ] Cognitive architecture (ACT-R, SOAR) 與 LLM 整合的嘗試
- [ ] SCM: Self-Controlled Memory framework (Wang et al., 2023, arXiv:2304.13343) — A-Mem 引用的 controller 機制
- [ ] LoCoMo dataset (Maharana et al., 2024, arXiv:2402.17753) — 長對話記憶評測基準
- [ ] Embodied cognition 和 grounded language models

---

*每次深度研究 session 後更新此清單*