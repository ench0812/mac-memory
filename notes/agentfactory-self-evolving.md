---
date: 2026-03-24
paper: AgentFactory: A Self-Evolving Framework Through Executable Subagent Accumulation and Reuse
authors: Zhang Zhang, Shuqi Lu, Hongjin Qian, Di He, Zheng Liu
venue: arXiv
arxiv: 2603.18000
rating: ⭐⭐
status: 📖
type: note
tags: [note]
---

# AgentFactory: A Self-Evolving Framework Through Executable Subagent Accumulation and Reuse

## 一句話總結
AgentFactory 將成功解法保存為可執行的 Python 子代理（subagent），並透過執行回饋自動改進與導出，實現能力的累積與跨系統復用。

## 架構
- Meta-Agent（協調者）：任務分解、選配工具、評估並觸發子代理的建立/修改。
- Skill System：三層技能（Meta/Tool/Subagent），Subagent 為可演化的 Python 腳本。
- Workspace Manager：隔離執行環境，測試後將成熟子代理提升至永久庫。
資料流：請求→Meta-Agent 分解→選 skill / 生成 subagent→執行→回饋分析→modify_subagent→驗證→persist/部署。

## 長處
1. 把「經驗」從文本轉為可執行 artefact，提高復用確定性與效率。
2. 明確的三階段管線（Install→Self‑Evolve→Deploy），可直接導出到其他 Python 生態。
3. 注重執行回饋閉環，示例中有自動修復與增強的實證。

## 缺陷
1. 安全風險與權限控制薄弱，runtime code 執行需更嚴格 sandbox 與 provenance 機制。
2. 對複雜語義泛化的依賴仍強，modify 依賴 LLM 的可靠性與測試集覆蓋。
3. 評估以 token 數/代理重用為主，缺少對可用性、可維護性與長期腐化的量化分析。

## 對 MaC 的啟發
- 可直接借用：以可執行 S-expression / Python 模組化記憶（執行即語義）作為 MaC 的記憶單元思想。
- 需修改使用：加入嚴格 provenance、不可變 source 與 sandboxed 執行層，並把子代理表示為 homoiconic S-expression 以利內省與編輯。
- 填補的 gap：提供了從經驗→可執行記憶的工程化路徑，對 MaC 的執行性設計具體可參照性。

## 關鍵引用（待追蹤）
- Novikov et al. (AlphaEvolve, 2025) — code-based evolution 的案例
- Shinn et al. (Reflexion, 2023) — 與文本經驗 baseline 的比較

## 我的思考
AgentFactory 在工程性與可移植性上很有價值；把「記憶」當成可執行模組與我們 MaC 的 homoiconic 設計高度相容，但必須補強安全/可審計、以及讓記憶的語義表示更易於形式化檢驗。