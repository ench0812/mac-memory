---
date: 2026-03-27
paper: "AgentFactory: A Self-Evolving Framework Through Executable Subagent Accumulation and Reuse"
authors: "Zhang Zhang, Shuqi Lu, Hongjin Qian, Di He, Zheng Liu"
venue: "arxiv preprint, 2026.03"
arxiv: "2603.18000"
rating: ⭐⭐
status: 📖
---

# AgentFactory: A Self-Evolving Framework Through Executable Subagent Accumulation and Reuse

## 一句話總結
將 AI agents 的「自我演化」機制從單純經驗／history 記錄，推進為「可執行子代理（subagent）累積 + 持續自我修正、跨系統可攜」的工程性框架。

## 架構
核心由三大元件組成：Meta-Agent（負責分解與導引）、Skill System（三層：meta skills、tool skills、subagent skills，subagent 皆為純 Python + SKILL.md 文件）、Workspace Manager（每個子代理有 sandbox；改進時僅推進到 persistent pool）。
系統分為三階段：Install（為新問題動態生成專用 subagent）、Self-Evolve（根據執行回饋持續修正）、Deploy（成熟 subagent 可匯出跨 AI framework 使用）。每個成功任務都會獨立保存並檔案化相關子代理。

## 長處
1. 從「經驗為 prompt」進化為「經驗為 executable code」──每一段解決方案可重用、可驗證、可自演化，落地力強。
2. Subagent 完全模組化、文檔標準化，可於外部 AI framework（如 LangChain、AutoGen）中直接載入。
3. 強調隔離機制（sandbox），增強自動化 agent 自修時的穩定性與安全。

## 缺陷
1. 仍依賴 meta-agent 做決策與 agent orchestration，本身「自演化」只限於 subagent code/技能層，尚未達到 meta-agent 結構自演化。
2. Subagent 的「generalization」仍需 meta-agent 額外判斷與 feedback 累積，遇到 novel task 仍可能失效。

## 對 MaC 的啟發
- 可直接借用：code-first 記憶累積邏輯、執行路徑標準化、subagent portability。
- 需修改使用：擴展 subagent 的型態／存取路徑，讓「homoiconic 記憶」能跨語言、跨 runtime；考慮將 meta-agent 也抽象成可演化 node。
- 填補的 gap：MaC 目前缺乏跨 framework 記憶遷移與自發明執行單位（subagent）演化的 workflow，AgentFactory 提供現成範例。

## 關鍵引用（待追蹤）
- Self-Refine [Madaan+ 2023] — 執行反饋驅動的 generate-feedback-modify loop
- Voyager [Wang+ 2023] — 經驗累積為 tool-level skill；subagent saving
- Darwin Gödel Machine [Zhang+ 2025b] — open-ended recursive self-improvement

## 我的思考
AgentFactory 理論上解決了「經驗→能力」的最後一哩路，重點在於讓 agent 經驗的存續不再是 LLM prompt/hint history，而是成為可被直接執行的 artifact。這與 MaC 的 memory-as-code 完全同軌，但目前的框架還無法讓自身 orchestration policy 自演化，meta-agent “不會自己生長”。MaC 若能結合這種 subagent 的形式、但擴展記憶單位到 S-expression/homoiconicity + policy 層，也許能讓整個 agent 結構完整地進化，不只累積 tool，也能累積行為/策略本身。