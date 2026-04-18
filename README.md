---
date: 2026-03-04
type: research-project
tags: [research, AI, memory, LISP, cognition, paper]
status: active
---

# Memory-as-Code (MaC) 研究專案

> 讓記憶不只是被存取的資料，而是能自動觸發思考、自我修正、產生新連結的活性結構。

## 研究目標
設計並實作一套 AI 專屬的可執行記憶架構，基於 LISP homoiconicity 哲學，最終以學術論文形式發表。

## 論文標題草案
**"Memory as Code: Toward an Executable Memory Architecture for Self-Evolving AI Agents"**

## 目錄結構

```
memory-as-code/
├── README.md              ← 你在這裡
├── papers/                ← 論文 PDF + 閱讀筆記
│   ├── reading-list.md    ← 待讀/已讀清單 + 評分
│   └── [paper-slug].md    ← 每篇論文的詳細筆記
├── notes/                 ← 研究筆記、靈感、分析
├── experiments/           ← 實驗設計、結果、數據
└── drafts/                ← 論文草稿
```

## 研究佇列（對應 research-queue.json R032）

### Phase 1: 文獻研究（知）
| ID | 子任務 | 狀態 |
|----|--------|------|
| S1 | 精讀核心論文（A-MEM, MemOS, etc.） | A-MEM done, 9 篇待讀 |
| S5 | 論文寫作 Introduction + Related Work | pending |

### Phase 2: 設計（知→行的橋樑）
| ID | 子任務 | 狀態 |
|----|--------|------|
| S2 | 設計 Memory S-expression v0.1 規格 | pending |
| S4 | 人格向量 × Memory 交互設計 | pending |

### Phase 3: 實作驗證（行）— ⚠️ 知行合一的關鍵
| ID | 子任務 | 預期產出 | 狀態 |
|----|--------|----------|------|
| E1 | **S-expression 編碼器 MVP** | Python script：將現有 LanceDB 記憶轉為三層 S-expression | ✅ done (29 tests) |
| E2 | **分層理解實測** | 同一條 S-expression 記憶分別餵 Opus/Sonnet/gpt-5-mini，測量理解差異 | ✅ live done (135 calls, 0 errors; 2026-03-06) |
| E3 | **記憶觸發實驗** | 5 條帶觸發條件的記憶，驗證能否自動 fire | ✅ done (F1=1.0) |
| E4 | **記憶自我修正實驗** | 記憶帶 confidence + decay rule，驗證結果回饋後自動調整 | ✅ done (5/5 pass) |
| E5 | **跨模型編譯實測** | Opus 編譯一條記憶→三層版本，驗證 gpt-5-mini 能用 L1、Sonnet 能用 L2 | ✅ live done (45 calls + Opus analysis; 2026-03-06) |
| E6 | **A/B 對比實驗** | 同任務跑兩次：一次用原始記憶、一次用 S-expression 記憶，比較效果 | ✅ live judge + robustness analysis done (2026-04-01) |

### Phase 4: 論文寫作
| ID | 子任務 | 狀態 |
|----|--------|------|
| S5 | Introduction + Related Work | ✅ v2 revised (2026-03-12), refreshed 2026-04-19 with AgeMem / EverMemOS / symbolic-reasoning updates, ~8000 words |
| S5b | The Mentalese Hypothesis (Section 3) | ✅ first draft (2026-03-08), ~1800 words |
| S6 | Architecture (§4) + Governance (§5) + Implementation (§6) | ✅ first draft (2026-03-14/15), ~18000 words |
| S7 | Evaluation + Results (§7) | ✅ revised with E6 robustness analysis (2026-04-01), ~2900 words |
| S8 | Discussion + Conclusion (§8-9) | ✅ first draft (2026-03-15), ~6500 words |
| S9 | Abstract | ✅ revised (2026-04-05), ~270 words |

### 驗證里程碑
- **M1** (Phase 2 完成): S-expression v0.1 spec 定稿 → 可以開始寫 Architecture section
- **M2** (E1-E2 完成): 編碼器能跑 + 分層理解有數據 → 證明「分層理解」不只是理論
- **M3** (E3-E4 完成): 觸發 + 自修正能跑 → 證明「記憶即代碼」核心假說
- **M4** (E5-E6 完成): 跨模型 + A/B 對比 → 論文 Evaluation section 的數據來源

## 核心假說
1. **記憶即代碼**: 記憶用 S-expression 表達，自帶觸發條件、連結、衰減規則
2. **人格塑造記憶**: 人格向量影響記憶的觸發閾值和衰減速率
3. **記憶自我修正**: 記憶帶 meta-rule，可以根據結果自動調整信心度
4. **AI 的 Mentalese**: AI 需要一套不同於自然語言的內部思考語言

## 關鍵研究者（追蹤名單）

### 直接相關
- **Jordi de la Torre** (Barcelona) — LISP + LLM 整合框架
- **Wujiang Xu** (Rutgers) — A-MEM, Agentic Memory
- **MemTensor Team** — MemOS 記憶操作系統
- **Yongfeng Zhang** (Rutgers) — A-MEM 通訊作者

### Neuro-Symbolic AI 領域
- 待收集

### 認知科學 / Language of Thought
- **Jerry Fodor** (經典) — Mentalese 假說
- 待收集當代認知科學研究者

## 相關連結
- 文獻地圖: [[LISP-與AI思考語言]]
- 人格向量: `~/clawd/personality/personality-vector.json`
- 研究佇列: `~/clawd/vault/Evolution/research-queue.json` (R032)
- Mickey 系統架構: `~/clawd/SOUL.md`

---
*啟動日: 2026-03-04 | 發起人: 茂 & Mickey*
🐭