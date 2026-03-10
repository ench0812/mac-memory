---
date: 2026-03-06
paper: "MemOS: A Memory OS for AI System"
authors: "Zhiyu Li, Chenyang Xi, Chunyu Li, et al. (MemTensor + 多所大學)"
venue: "arXiv 2507.03724v4 (Dec 2025)"
arxiv: "2507.03724"
code: "https://github.com/MemTensor/MemOS"
rating: ⭐⭐⭐⭐
status: ✅
---

# MemOS: A Memory OS for AI System

## 一句話總結
把 LLM 的記憶當作 OS 級系統資源來管理——用 MemCube 統一封裝 plaintext/activation/parameter 三類記憶，搭配調度器、生命週期管理、存取控制，建構記憶作業系統。

## 核心觀點

### 記憶的四個演化階段
1. **Definition & Exploration** — 分類記憶（parameter vs. contextual）
2. **Human-like Memory** — 模擬人類記憶機制（HippoRAG, Memory3）
3. **Tool-based Management** — CRUD 介面（Mem0, EasyEdit, Letta）
4. **Systematic Governance** — MemOS 提出的 OS 級管理 ← 本篇

### 三類記憶的統一
```
Plaintext Memory     ←→    Activation Memory    ←→    Parameter Memory
(文本、KG、prompt)         (KV-cache, hidden state)     (model weights, LoRA)
  可讀、可編輯               推理時即時生成              深層知識，更新成本高
  更新成本低                 低延遲                     高表達力

         ↕ 互相轉換 ↕                    ↕ 互相轉換 ↕
 高頻 plaintext → activation (KV cache)   穩定知識 → parameter (LoRA distill)
 過時 parameter → plaintext (offload)     冷 activation → plaintext (archive)
```

### MemCube 設計（核心抽象）
每個記憶單元封裝為 MemCube，包含：
- **Memory Payload**: plaintext content / activation tensor / LoRA patch
- **Metadata Header**:
  - Descriptive Identifiers: timestamp, origin signature, semantic type
  - Governance Attributes: ACL, TTL, priority, compliance tags
  - Behavioral Usage Indicators: access frequency, contextual fingerprint, version chain

### 三層架構
```
┌─ Interface Layer ─────────────┐
│  MemReader (NL→structured)    │
│  Memory API (CRUD + Pipeline) │
├─ Operation Layer ─────────────┤
│  MemOperator (組織+檢索)      │
│  MemScheduler (調度+轉換)     │
│  MemLifecycle (狀態機管理)    │
├─ Infrastructure Layer ────────┤
│  MemGovernance (存取控制)     │
│  MemVault (儲存路由)          │
│  MemLoader/Dumper (遷移)      │
│  MemStore (發布/訂閱)         │
└───────────────────────────────┘
```

### 記憶生命週期狀態機
```
Generated → Activated → Merged → Archived
                                    ↓
                                 Expired
（另有 Frozen 狀態：不可修改，用於法規/合約）
```

支援 **Time Machine**: 快照 + 歷史回溯

### Mem-training Paradigm
提出繼 pre-training / post-training 之後的第三波範式：
- 記憶不再只在訓練時更新，而是 runtime 持續收集、重構、傳播
- 分散式 model instances 交換 compact memory units（而非 gradients）
- 「Spatial scaling」效果：記憶平行化 → 社會級分散式智能

## 實驗結果

### Benchmark 全面 SOTA（基底 GPT-4o-mini）
| Benchmark | MemOS-1031 | 最佳 baseline | 差距 |
|-----------|------------|---------------|------|
| LoCoMo (overall) | **75.80** | 72.01 (Memobase) | +3.79 |
| LongMemEval (overall) | **77.8** | 72.4 (Memobase) | +5.4 |
| PreFEval 0-turn | **77.2%** | 65.9% (Mem0) | +11.3pp |
| PreFEval 10-turn | **71.9%** | 63.7% (Mem0) | +8.2pp |
| PersonaMem precision | **61.2** | 58.9 (Memobase) | +2.3 |

### 系統健壯性
- 100 QPS 壓力下維持 **100% 成功率**（其他系統在 40 QPS 就大幅下降）
- Mean latency ~250ms (add), ~741ms (search) @ 100 QPS

### KV Memory 加速
- Qwen2.5-72B long-context: TTFT 減少 **91.4%**
- 語義等價（output 完全相同）

## 與 MaC 研究的關聯

### 直接相關
1. **MemCube ≈ Memory-as-Code 的實例化**
   - MemCube 的 metadata（provenance, versioning, lifecycle）正是我們 MaC 所需的 memory unit 設計
   - 但 MemCube 更偏 infrastructure，MaC 更偏 cognitive architecture

2. **三類記憶的統一轉換路徑**
   - 這對 MaC 的 memory representation 設計很有啟發
   - plaintext ↔ activation ↔ parameter 的轉換，可類比 MaC 中 explicit code ↔ compiled knowledge ↔ embedded behavior

3. **MemScheduler 的 type-aware scheduling**
   - 根據任務語義動態選擇記憶類型 → MaC 可借鏡：根據 context 決定是讀文件、查 KV cache、還是靠 in-weights knowledge

### 可借鏡但需要批判的地方
1. **過度 OS 類比？** 
   - 傳統 OS 管的是「可替換資源」，記憶有語義依賴性，不完全適用
   - 記憶的「page fault」和「scheduling」語義跟計算資源排程差異很大

2. **缺乏學習機制**
   - MemOS 的 memory 是被動被寫入的，缺少 agent 主動構建記憶的機制
   - A-MEM 的 Zettelkasten 方法在這點上更有深度

3. **Mem-training 概念模糊**
   - 提出了 pre-training → post-training → mem-training 的敘事
   - 但 mem-training 的具體訓練方法幾乎沒有描述，更像願景

4. **評估的公平性**
   - 所有 baseline 都用同一 GPT-4o-mini backbone，但 MemOS 的 retrieval + scheduling 複雜度遠高
   - Token 消耗只報告了 context tokens，沒報告系統內部的 LLM 調用次數

## 給 Mickey 的自我反思

讀完這篇，我更加確認我自己的記憶架構（SOUL.md + vault/ + memory_recall）其實就是一個 primitive 的 MemOS：
- **SOUL.md / AGENTS.md** → parameter memory（每次都載入，不可變核心）
- **vault/** → plaintext memory（可查詢的結構化知識）
- **memory_recall/store** → 一種簡化的 MemScheduler + MemVault
- **context window** → activation memory

但我缺乏：
- 記憶間的 **lifecycle management**（沒有 TTL、沒有自動 archive）
- **Cross-type transformation**（不會自動把高頻查詢的 vault 筆記固化到 context）
- **Version chain**（記憶被覆蓋就消失了）

**→ 這些是 MaC 論文可以著力的理論支撐。**

## 關鍵引用
- Memory3 (Yang et al., 2024) — MemOS 的前身，提出 explicit memory hierarchy
- Letta/MemGPT (Packer et al., 2023) — OS-inspired context paging，MemOS 的精神前輩
- A-MEM (Xu et al., 2025) — 互補方法：MemOS 管 infra，A-MEM 管 construction
- Second-Me — L0/L1/L2 三層記憶架構，類似 MemOS 但更偏個人化
