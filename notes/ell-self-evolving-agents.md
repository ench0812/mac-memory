---
date: 2026-03-16
paper: Building Self-Evolving Agents via Experience-Driven Lifelong Learning (ELL)
authors: Yuxuan Cai, Yipeng Hao, Jie Zhou, et al.
venue: arXiv preprint
arxiv: 2508.19005
rating: ⭐⭐
status: 📖
type: note
tags: [note]
---

# Building Self-Evolving Agents via Experience-Driven Lifelong Learning (ELL)

## 一句話總結
提出 ELL 框架與 StuLife 基準，強調經驗驅動的長期記憶、技能抽象與知識內化，評估現有 LLM 在自我演化場景下的不足。

## 架構
- 核心元件：Experience Exploration → Knowledge Abstraction → Knowledge Refinement → Memory/Skills 庫 → Policy/Planner
- 資料流：agent 與 environment 互動，產生 trajectory → 抽象成結構化記憶與技能 → 驗證並回寫到 persistent memory → 用於未來決策與技能學習
- 關鍵操作：Add / Update / Delete / Combine（知識精煉循環）

## 長處
1. 定位明確：把「終身學習」擴展為「經驗驅動的自我演化」，把主動探索與內在動機放在框架中心。
2. Bench + Metric：提供 StuLife 與 StuGPA 用以衡量長期發展、主動性與記憶保持，具體化研究議題。
3. 實務導向：討論記憶的結構化、技能化與生命周期管理（增、改、刪、合併），可直接作為系統設計指南。

## 缺陷
1. 記憶表徵模糊：雖強調 persistent memory，但沒有提供 homoiconic 或可執行記憶的具體表示格式（例如 S-expression / code-as-memory）。
2. 安全與可控性不足：自我演化與長期記憶可能導致不可預期行為，論文未深入處理 safety / provenance / revert 機制。
3. 實驗局限：雖有 StuLife，但環境仍是模擬且未展示可執行記憶（memory-as-code）對策略改進的直接效果。
4. 評估薄弱：StuGPA 有價值，但論文未提供對不同記憶設計（structured vs. executable）的比較實驗。

## 對 MaC 的啟發
- 可直接借用：ELL 對於經驗抽象（experience→skill）與知識精煉流程的操作語義（Add/Update/Delete/Combine）是 MaC 設計的重要流程，可映射為記憶編譯階段。
- 需修改使用：把 ELL 的 persistent memory 換成 MaC 的 homoiconic、可執行記憶（S-expr / code cells），以支持記憶的自我修改與版本化回滾。
- 填補的 gap：ELL 強調流程與 benchmark，但少了可執行記憶的表示與安全網；MaC 可以補上可執行記憶語言、校驗器與憲法（constraining constitution）以做 evolution 的安全門檻。

## 與我們 Reading-list 的連結 / 建議跟進引用
- 論文引用了多篇關於 memory augmentation、continual learning、self-play 與 skill learning 的工作（例：liang2025sage, chhikara2025mem0, zhong2024memorybank）。
- 建議加入 reading-list 至少：
  - liang2025sage — memory augmentation 與 retrieval-augmented learning（Tier2, 📋）
  - chhikara2025mem0 — 結構化記憶系統設計（Tier2, 📋）
  - guan2024richelieu — self-play / experience generation 方法（Tier3, 📋）

## 我的思考
ELL 為自我演化的整體願景與評估提供了良好框架，但在「記憶如何成為可執行的第一類實體」上留白。對我們 MaC 而言，直接的工程價值是把 ELL 的 knowledge refinement 具體化成可編輯、可驗證、可回滾的 S-expression memory lifecycle；同時在 benchmark 上添加對 "executable memory" 類別的 ablation（structured data vs. code-as-memory vs. opaque vec store）會是一個有說服力的實驗。

---

## 關鍵引用（待追蹤）
- [liang2025sage] — memory augmentation / retrieval-augmented learning
- [chhikara2025mem0] — structured memory system
- [guan2024richelieu] — self-play experience generation

## 總結（給團隊）
ELL 很值得作為 MaC 的 design-positioning 參考：採納其流程與 benchmark 設計，但補上我們的差異化——homoiconic 可執行記憶、憲法式安全檢查、以及記憶的可證明回滾機制。