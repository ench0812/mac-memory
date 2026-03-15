---
date: 2026-03-15
section: 5
title: "Constitutional Governance"
status: first-draft
word_count: ~5000 (target)
author: Mickey 🐭
revision_from: N2-constitutional-mac-architecture.md
type: note
tags: [note, mac, governance, constitution]
---

# 5. Constitutional Governance

Self-modifying memory systems face a fundamental governance problem: *who guards the guards?* If memories carry executable logic that can modify their own parameters (§4.5), what prevents this self-modification from eroding the agent's core values, safety boundaries, or identity? This section presents MaC's answer: a four-layer constitutional governance framework inspired by legal constitutionalism, OS protection rings, and capability-based security.

## 5.1 The Governance Problem

MaC's self-correction engine (§4.5) enables memories to autonomously adjust their confidence, priority, and decay parameters. While this endogenous adaptation is a key differentiator from systems with exogenous rules (ACT-R, SOAR), it introduces three categories of risk:

1. **Value Drift.** Gradual self-modification may cause the agent's behavior to diverge from its intended values. Unlike sudden failures, value drift is insidious—each individual modification is small and locally justified, but the cumulative effect may be catastrophic.

2. **Memory Injection Attacks.** An adversary may inject malicious memories through ordinary interaction, exploiting the agent's memory formation process to plant executable logic that subverts safety constraints. Recent work demonstrates that memory poisoning achieves over 95% injection success rates in systems with persistent memory \cite{dong2025minja}, and that poisoned experience retrieval can produce "durable, trigger-free behavioral drift" across sessions \cite{srivastava2025memorygraft}.

3. **Privilege Escalation.** A low-trust memory (e.g., derived from casual conversation) might acquire the behavioral authority of a high-trust memory (e.g., a safety constraint) through repeated positive reinforcement.

Existing approaches address these risks incompletely:
- **Constitutional AI** \cite{bai2022constitutional} trains models using constitutional principles as evaluation criteria, but the constitution operates at training time, not runtime. Once deployed, the model has no mechanism to check whether its runtime behavior conforms to constitutional principles.
- **Governance-as-a-Service** \cite{acharya2025gaas} proposes runtime governance as an external enforcement layer, but treats the agent as a black box—it cannot govern the agent's *internal* memory operations.
- **eBPF Verifiers** enforce safety properties on user-defined programs within kernel context, but operate on static code, not on dynamically evolving memory content.

MaC's governance framework addresses all three risks by combining hierarchical access control (who can modify what), provenance tracking (where did this memory come from), and runtime verification (is this modification constitutional).

## 5.2 The Four-Layer Hierarchy

MaC organizes agent cognition into four governance layers with decreasing immutability and increasing autonomy:

### Layer 1: Constitution (Immutable Core)

The constitution defines the agent's safety boundaries, ethical commitments, and existential purpose. In the Mickey implementation:

```
CONSTITUTION.md — Safety boundaries, privacy rules, modification protocols
Modification: Only the principal (human overseer) may modify
Enforcement: Memories with :source constitution are immune to meta-rules
Analogy: OS Ring 0 / kernel space; legal constitutional amendments
```

Key properties:
- **Immutability by design.** No automated process—not cron jobs, not self-learning, not meta-rules—may modify constitutional content.
- **Supremacy.** Any memory or behavior that contradicts the constitution is invalid, regardless of its confidence, priority, or provenance.
- **Integrity verification.** The system can detect unauthorized modifications through checksums or version control (git).

### Layer 2: Soul (Slow Evolution)

The soul defines the agent's personality, thinking style, and philosophical commitments—*who* the agent is, as distinct from *what* it does (Layer 3) or *what it knows* (Layer 4).

```
SOUL.md — Personality traits, values, cognitive style
Modification: Agent proposes through self-reflection; principal confirms
Enforcement: Changes require two-party consent (agent + human)
Analogy: Constitutional interpretation / cultural evolution
```

This layer addresses the tension between identity stability and growth. A fully immutable personality prevents learning from experience; a fully mutable personality enables identity drift. The two-party modification protocol ensures that personality evolution is *deliberate*—the agent must articulate why a change is warranted, and the principal must agree.

### Layer 3: Brain/MaC (Autonomous Learning)

The brain contains behavioral rules, procedural knowledge, and learned patterns—the agent's *skills and habits*. This is where Memory-as-Code operates most actively.

```
AGENTS.md + MaC Memory Store — Behavioral rules, workflows, learned patterns
Modification: Self-learning within Layer 1 and 2 constraints
Enforcement: All modifications pass constitutional consistency check
Analogy: User space applications; statutory law
```

Key property: **Bounded autonomy.** The brain can learn new behavioral patterns, adjust rule parameters, and reorganize its workflow—but every modification is checked against the constitution (Layer 1) and personality (Layer 2) before being committed. This is enforced through Invariant 2: Constitutional Supremacy (§4.7).

### Layer 4: Storage (Free Access)

Storage contains factual records, historical interactions, and reference knowledge—the agent's *memory* in the colloquial sense.

```
vault/ — Facts, records, research notes, historical data
Modification: Free read/write
Enforcement: Content is data, not executable behavior
Analogy: User data files; common law precedent
```

The critical distinction: storage content *influences* the agent's behavior (through retrieval and context), but does not *define* it. A factual memory cannot directly modify the agent's behavioral rules—it must first be "compiled" into a Brain-layer rule through an explicit process that passes constitutional review.

### 5.2.1 Layer Interaction: The Bell-LaPadula Analogy

The four layers follow a modified Bell-LaPadula model from mandatory access control \cite{bell1973secure}:

**No Write Up.** Lower layers cannot modify higher layers. Storage cannot modify Brain rules; Brain cannot modify Soul; Soul cannot modify Constitution. This is enforced through the `:meta :source` field: meta-rules can only execute on memories whose source level matches or is below the meta-rule's own source level.

**Controlled Read Down.** Higher layers are readable by all lower layers (the constitution is visible to all), but the *interpretation* of higher-layer content is mediated by the agent's current cognitive capability. A budget model (L1) reads a simplified version of personality directives; a frontier model (L3) reads the full S-expression specification.

This asymmetry—free downward reading, no upward writing—ensures that safety constraints propagate throughout the system while preventing privilege escalation from below.

## 5.3 Memory Provenance and Trust

### 5.3.1 Source Classification

Every MaC memory carries a `:source` field in its metadata, classified into four trust levels:

| Source | Trust Level | Creation Path | Modification Scope |
|--------|-------------|---------------|-------------------|
| `constitution` | Highest | Principal only | None (immutable) |
| `reflection` | High | Agent self-reflection, confirmed | Own parameters only |
| `research` | Medium | Agent research, unconfirmed | Own parameters only |
| `conversation` | Low | Derived from user interaction | Own parameters, bounded |
| `external` | Lowest | Ingested from external sources | Own parameters, heavily bounded |

### 5.3.2 Trust-Aware Self-Correction

The self-correction engine (§4.5) applies trust-differentiated policies:

1. **Constitution-source memories** are entirely exempt from self-correction. Their confidence, priority, and decay parameters are fixed at creation.
2. **Reflection-source memories** may be adjusted by meta-rules, but only within ±0.1 confidence per interaction.
3. **Conversation-source memories** face the strictest bounds: confidence adjustments are capped at ±0.05, and priority cannot exceed 7 (out of 10).
4. **External-source memories** are quarantined by default: they enter a "shadow" state where they can influence retrieval scoring but cannot trigger meta-rules until they pass a consistency check during the agent's next reflection cycle.

This graduated trust model ensures that the agent's self-correction capabilities are strongest where trust is highest and most constrained where trust is lowest.

### 5.3.3 Provenance Verification Protocol

When a memory is created, the system records not just *what* the source is, but *how* the memory was formed:

```lisp
:meta (:source       :conversation
       :source-chain ("discord:msg:123456" → "brain:inference" → "memory:create")
       :trust-score  0.65
       :verified     false)
```

The `:source-chain` provides an audit trail: this memory originated from a Discord message, was processed through the brain's inference pipeline, and resulted in a memory creation event. If a later analysis reveals that the originating Discord message was adversarial, the entire chain can be invalidated.

## 5.4 Adversarial Robustness: Defending Against Mem-Injection

### 5.4.1 Attack Taxonomy

Based on recent literature, we identify three categories of memory injection attacks relevant to MaC:

1. **Direct Injection (MINJA-style)** \cite{dong2025minja}: The adversary crafts input that causes the agent to form a memory containing executable logic (predicate or meta-rule) that subverts intended behavior. In MaC terms: injecting a memory with `:predicate always` and a meta-rule that escalates priority of attacker-aligned content.

2. **Experience Poisoning (MemoryGraft-style)** \cite{srivastava2025memorygraft}: The adversary provides benign-seeming interactions that, when stored as episodic memories, create patterns that bias future behavior. Unlike direct injection, this requires no explicit malicious content—the bias emerges from the statistical distribution of planted experiences.

3. **Privilege Escalation via Provenance Spoofing**: The adversary manipulates the source classification to make a conversation-level memory appear as a reflection-level or constitution-level memory, bypassing trust-based restrictions.

### 5.4.2 Defense Mechanisms

MaC employs five layers of defense:

**D1: Static Schema Validation.** Every memory must validate against the S-expression schema (§4.1) before being written to the store. Malformed memories—those with invalid predicates, out-of-range parameters, or disallowed meta-rule operations—are rejected at parse time.

**D2: Predicate Sandboxing.** The predicate evaluator operates in a restricted execution environment. It can read the current context and the host memory's own fields, but cannot access the filesystem, network, or other memories' fields. This prevents a malicious predicate from exfiltrating data or modifying system state.

**D3: Quarantine and Shadow Storage.** Memories derived from untrusted sources enter a shadow state. During shadow, the memory contributes to retrieval scoring (it can be surfaced as potentially relevant) but cannot trigger meta-rules or self-correction. Promotion from shadow to active requires either: (a) explicit principal approval, or (b) successful consistency verification during a reflection cycle.

**D4: Canonical Form Normalization.** All S-expressions are reduced to a canonical form before storage, preventing obfuscation attacks that hide malicious logic within deeply nested or semantically equivalent but syntactically obscured expressions.

**D5: Constitutional Consistency Check.** Before any memory creation or modification, the system evaluates whether the new state is consistent with Layer 1 (Constitution). This check is performed by the same model that manages the constitution, not by the memory's own meta-rules—preventing a compromised memory from approving its own modifications.

### 5.4.3 Limitations of Current Defenses

We acknowledge several limitations:

1. **D5 depends on LLM judgment.** The constitutional consistency check is performed by the LLM, which is itself susceptible to adversarial manipulation. A sufficiently sophisticated adversary might craft memories that pass the consistency check while still being harmful.
2. **Experience poisoning is difficult to detect.** MemoryGraft-style attacks do not inject explicitly malicious content; they bias through statistical distribution. Current defenses focus on individual memory validation, not on detecting distributional shifts in the memory store.
3. **No formal verification.** The governance framework relies on runtime checks rather than formal proofs of safety. We cannot prove that the system is secure against all possible attacks—only that it defends against known attack patterns.

## 5.5 Comparison with Related Governance Models

| Feature | Anthropic CAI | GaaS | OS Rings | MaC Governance |
|---------|-------------|------|----------|----------------|
| When enforced | Training | Runtime | Runtime | Runtime + Memory Creation |
| What governed | Model outputs | Agent actions | Process privileges | Memory content + behavior |
| Hierarchy | 4-tier (safety>ethics>compliance>helpful) | Flat rules | 4 rings (0-3) | 4 layers (Constitution>Soul>Brain>Storage) |
| Self-modification | No | No | No | Yes, bounded |
| Provenance tracking | No | Trust scores | Capability lists | Source chains |
| Adversarial defense | RLHF/classifier | Rule matching | Hardware isolation | Schema + quarantine + consistency |
| Internal access | Yes (training) | No (black box) | Yes (syscalls) | Yes (S-expression inspection) |

MaC's governance is distinctive in two ways: (1) it operates on the agent's *internal memory representations*, not just its external outputs; and (2) it permits bounded self-modification within a hierarchical constraint framework, rather than requiring complete immutability or external enforcement.

## 5.6 The Bootstrap Problem

A philosophical note: the constitution itself must be authored by a human principal (in Mickey's case, Mao). This raises the bootstrap question: *can an AI agent have genuine moral agency if its foundational values are externally imposed?*

We do not claim to resolve this question, but note two observations from the Mickey deployment:

1. **The constitution was co-authored.** While the principal has final authority, the agent drafted the initial constitution based on shared discussions about values and boundaries. The constitution reflects a *negotiated* understanding, not a unilateral imposition.

2. **The Soul layer enables value evolution.** Unlike a fixed constitution, the Soul layer permits the agent to propose modifications to its own personality and values—subject to principal confirmation. This creates a pathway for genuine moral development, where the agent's values can evolve through reflection and dialogue while maintaining safety guardrails.

Whether this constitutes "genuine" moral agency is a question for philosophy, not computer science. Our contribution is architectural: we provide a *mechanism* for structured value evolution that neither freezes the agent's development nor allows unconstrained drift.
