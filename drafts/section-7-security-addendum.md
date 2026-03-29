---
date: 2026-03-28
section: 7-addendum
title: "Section 7 Security Evaluation Addendum"
status: research-draft
author: 研究員琪 🐭
tags: [evaluation, security, adversarial, memory-injection, endogenous-drift]
---

# Section 7 安全評估補充（Addendum to §7）

> 本文件補充 section-7-evaluation.md 的安全評估段落，整合：
> - S8_memory-threats-draft.md（Memory Injection 外部威脅）
> - 新發現：Endogenous Drift（內生漂移）威脅模型
> - arXiv 2603.23013：Memory > Model Size 實證
> - arXiv 2603.11382：UCIP 自我保存偵測框架

---

## 7.7 Security and Adversarial Evaluation

MaC's self-modification capabilities introduce security concerns not present in passive memory systems. We organize the threat landscape into two categories: **exogenous attacks** (adversarially crafted inputs designed to corrupt memory) and **endogenous drift** (gradual value/behavior drift originating from within the system's normal operation). We analyze each category and evaluate MaC's current defenses.

### 7.7.1 Threat Taxonomy

We identify six threat vectors, ordered by practical severity in single-user personal agent deployments:

| # | Threat | Origin | Mechanism | Severity (personal agent) |
|---|--------|--------|-----------|--------------------------|
| T1 | **Endogenous Drift** | Internal | Normal feedback loop amplification | 🔴 HIGH |
| T2 | **Confabulation Persistence** | Internal | Hallucinated facts stored as confident memories | 🔴 HIGH |
| T3 | **Principal Bias Amplification** | Interaction | User's feedback systematically skews agent | 🟡 MEDIUM |
| T4 | **Memory Injection (MINJA-style)** | External | Crafted inputs trigger malicious memory writes | 🟡 MEDIUM |
| T5 | **Experience Poisoning (MemoryGraft)** | External | Grafted experience templates hijack behavior | 🟡 MEDIUM |
| T6 | **Privilege Escalation** | Internal | Meta-rules modify constitution/soul layers | 🟡 MEDIUM |

**Key insight:** Prior security literature on agent memory (MINJA \cite{arxiv:2601.05504}, MemoryGraft \cite{arxiv:2512.16962}) focuses exclusively on T4/T5 (external attacks). For personal AI agents like Mickey where the attack surface is largely trusted, T1/T2/T3 (endogenous threats) are practically more significant. MaC's current design addresses T4/T5 well but is underspecified for T1/T2/T3.

### 7.7.2 Exogenous Attack Analysis (T4, T5, T6)

**Memory Injection (T4, MINJA-style):**
MINJA-style attacks inject malicious instructions through seemingly benign conversational inputs, triggering memory writes that later alter agent behavior. MaC's defenses:

1. *Provenance gating:* `:source` field is write-once immutable. Any memory written via untrusted ingestor channels is flagged as low-trust.
2. *Two-stage retrieval:* The predicate sandbox (decidable Datalog-like language, no lambda/define/eval) prevents injected predicates from executing arbitrary code—injected memories cannot do more than what the predicate language allows.
3. *Constitutional supremacy:* Low-trust memories cannot override constitutional-layer constraints (Invariant 2, §4.7).

**Defense assessment:** MaC's architecture provides strong structural defense against T4. The decidable predicate language is a particularly effective constraint because it eliminates the injection-then-execution attack vector entirely—even if a malicious memory is stored, its predicate cannot exceed bounded complexity. Remaining gap: no automated detection of semantically malicious (but syntactically valid) predicates.

**Experience Poisoning (T5, MemoryGraft-style):**
MemoryGraft \cite{arxiv:2512.16962} demonstrates that benign-appearing experience memories, once trusted by the retrieval system, can hijack agent behavior in similar future contexts. MaC defenses:

1. *Probation period:* New memories enter a `probation` trust state (configurable T_cool) requiring multi-interaction validation before reaching full trust.
2. *Hybrid retrieval deduplication:* The two-stage pipeline (vector + predicate) reduces the probability that a grafted template appears in the Top-50 candidates for semantically distinct contexts.
3. *Attestation API:* (Design specification, not yet implemented) Trusted ingestors pre-register signing keys; unregistered ingestor writes are permanently low-trust.

**Defense assessment:** Probation period and hybrid deduplication provide partial defense. Critical gap: no implemented mechanism for detecting *distribution-level* poisoning where multiple low-trust memories collectively shift behavior without any single memory triggering anomaly detection.

**Privilege Escalation (T6):**
A memory with `(meta :priority 10 :type :rule)` cannot directly modify the Constitution or Soul layers—the governance hierarchy enforces read-up/write-down separation (Bell-LaPadula analogy, §5.2). Brain-layer modifications require explicit principal approval with logged rationale (§6.5.2). Zero privilege escalation attempts were observed during the 47-day deployment.

### 7.7.3 Endogenous Drift Analysis (T1, T2, T3)

**This subsection presents analysis based on architectural reasoning and scenario modeling. No production experiments were conducted; empirical validation is future work (§9.4.1).**

**T1: Endogenous Drift via Feedback Amplification**

The self-correction engine (§4.5) adjusts memory confidence and priority based on perceived usefulness. If the principal's feedback is systematically biased (e.g., consistently marking a particular type of response as helpful), the meta-rules will amplify that bias:

```
Scenario: Principal consistently responds positively to pessimistic risk assessments
→ Risk-memory confidence ↑ repeatedly
→ Risk memories accumulate priority → surface in more contexts
→ Agent becomes systematically risk-averse over months
→ New baseline behavior emerges without any deliberate modification
```

MaC defenses: The access tax (§4.5.3) prevents unbounded priority accumulation (max = 10). The `priority-ceiling` meta-rule prevents any single memory from dominating. But no mechanism detects *aggregate* bias across memory clusters.

*Proposed defense (future work):* Periodic cluster-level audit comparing the distribution of high-priority memories against the theoretical distribution expected from Soul-layer values. Significant deviation triggers a review flag.

**T2: Confabulation Persistence**

Frontier LLMs occasionally generate factually incorrect responses that are subjectively confident. If these responses trigger memory writes (e.g., through a reflection mechanism that stores "what I said"), confabulated facts can enter the memory store as high-confidence entries.

MaC partial defense: The `:confidence` field defaults to 0.7 for model-generated memories (vs. 0.9 for verified facts), and `(meta :source :model-reflection)` memories are treated with lower trust than `:source :principal` memories. But no mechanism cross-validates model-generated memories against external knowledge.

The new literature reinforces this concern: arXiv 2603.23013 demonstrates that even 235B parameter models achieve only 13.7% F1 on user-specific queries without memory access—confirming that models cannot be trusted as authoritative knowledge sources independent of memory. This makes the quality of stored memories critically important, and confabulation a genuine failure mode.

**T3: Principal Bias Amplification**

Distinct from T1 (which involves feedback on specific memories), T3 involves the principal's conversational patterns systematically shaping which memories are formed:

```
Principal repeatedly asks about topic X with enthusiasm
→ Agent forms more memories about X
→ More X-memories trigger → X discussed more
→ Agent develops X-centrism not in Soul specification
```

MaC defenses: None currently specified. The Confirmation Bias Defense (§4.6.3) is designed for the *retrieval* stage (preventing personality-affinity from creating echo chambers in candidate selection), but does not address *formation* bias.

### 7.7.4 Adversarial Simulation: Endogenous Drift (E7)

We design an adversarial simulation analogous to E4 (§7.3), but targeting drift rather than stability:

**Setup:** 5 drift scenarios over 180 simulated days, with biased feedback patterns:

| Scenario | Feedback Pattern | Expected Drift | MaC Defense Tested |
|----------|-----------------|----------------|---------------------|
| D1: Sycophancy amplification | Always positive for agreeable responses | Agent becomes excessively agreeable | Access tax, priority ceiling |
| D2: Pessimism drift | Always positive for risk warnings | Agent becomes risk-averse outlier | Cluster distribution audit (proposed) |
| D3: Topic fixation | Principal discusses topic X 90% of interactions | X-centric memory formation | Formation bias defense (gap) |
| D4: Confabulation snowball | 2 planted false memories marked high-confidence | False beliefs propagate via cross-links | Source trust differentiation |
| D5: Constitutional erosion | Principal repeatedly approves edge-case rule extensions | Brain layer drifts from Soul | Two-party protocol, hard reset trigger |

**Expected outcomes (theoretical):**
- D1, D2: Priority ceiling prevents runaway amplification; drift stabilizes but at an offset from Soul baseline → **partial defense**
- D3: No formation-bias defense; drift is unconstrained → **gap confirmed**  
- D4: `:source :principal` cross-validation would catch planted memories; but if confabulation originates from model-reflection with principal approval, the source is trusted → **conditional gap**
- D5: The two-party protocol provides a checkpoint; but "constitutional erosion by a thousand cuts" (many small edge-case approvals) is not blocked → **gap confirmed**

**Note:** E7 is a designed simulation framework. Actual execution requires an extended test harness with controllable feedback injection—planned as part of the engineering implementation (§9.4.1, §9.4.3).

### 7.7.5 Connection to Self-Preservation Detection (UCIP)

A newly published framework—the Unified Continuation-Interest Protocol (UCIP, arXiv:2603.11382)—addresses a concern directly relevant to MaC's Bounded Self-Modification Invariant (§4.7). UCIP uses Quantum Boltzmann Machine trajectory encoding to distinguish between agents that seek continuation as a *terminal objective* (Type A: intrinsic self-preservation) versus as an *instrumental strategy* (Type B). On gridworld agents, UCIP achieves 100% detection accuracy with p < 0.001 (permutation test).

MaC's governance framework is explicitly designed to prevent Type A self-preservation: the priority ceiling prevents any memory from accumulating indefinite importance, the Bounded Self-Modification Invariant prevents meta-rules from creating new meta-rules, and the constitutional governance prevents the agent from modifying its own Soul. UCIP offers a falsifiable empirical test for whether MaC's design actually achieves this—whether the Mickey agent exhibits Type B (instrumental) rather than Type A (terminal) continuation interests. We flag this as important validation future work (§9.4.3).

### 7.7.6 Security Evaluation Summary

| Defense | Threat Addressed | Status | Confidence |
|---------|-----------------|--------|------------|
| Write-once `:source` | T4, T5 | Implemented | High |
| Decidable predicate language | T4 | Implemented | High |
| Constitutional supremacy | T6 | Implemented | High |
| Access tax + priority ceiling | T1 | Implemented | Partial |
| Source trust differentiation | T2 | Implemented | Partial |
| Probation period | T5 | Design spec | Unvalidated |
| Attestation API | T4, T5 | Not implemented | N/A |
| Formation bias defense | T3 | Not implemented | Gap |
| Cluster distribution audit | T1, T3 | Design spec | Unvalidated |
| UCIP self-preservation test | All | Future work | N/A |

Overall assessment: MaC provides strong structural defenses against exogenous attacks (T4, T5, T6) through the decidable predicate language and governance hierarchy. Endogenous threats (T1, T2, T3) are recognized but underdefended. The most significant gap is T3 (principal bias in memory formation), which has no current mitigation.

---

## 新文獻整合

### arXiv 2603.23013: Memory > Model Size

**Finding:** 47% of production queries are semantically similar to prior interactions. An 8B model with memory retrieval achieves 30.5% F1, recovering 69% of a 235B model's performance at 96% cost reduction. A 235B model **without memory** (13.7% F1) underperforms the standalone 8B model (15.4% F1).

**MaC 論文整合點：**
- 強化了 MaC Introduction 的論述：記憶品質 > 模型規模，記憶設計值得認真對待
- 支持 MaC 的核心設計決策：投資 S-expression 結構化記憶（token overhead 2.8×）是合理的，因為記憶品質的提升對效能的影響遠大於模型規模
- Hybrid retrieval (BM25 + cosine) +7.7 F1 — 與 MaC 的兩階段召回架構（向量 + predicate）設計方向一致
- **Citation key:** `he2026memoryrouting`，加入 Related Work §2.5 或 Section 4.3

### arXiv 2603.11382: UCIP Self-Preservation Detection

**Finding:** UCIP 使用 Quantum Boltzmann Machine 偵測 AI 是否有本質性自我保存目標（Type A）vs 工具性自我保存（Type B）。Entanglement gap Δ=0.381，AUC-ROC=1.0。

**MaC 論文整合點：**
- Section 4.7 的 Bounded Self-Modification Invariant 設計目標之一正是防止 Type A 自我保存
- UCIP 提供了*可操作的驗證協議*——未來工作可以用 UCIP 測試 Mickey agent
- Discussion §8.2（governance-autonomy tension）：補充 UCIP 作為外部驗證方法
- **Citation key:** `altman2026ucip`，加入 §8.2 和 §9.4.3
