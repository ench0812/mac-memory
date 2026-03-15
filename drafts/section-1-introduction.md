---
date: 2026-03-08
section: 1
title: Introduction
status: first-draft
word_count: ~2200
author: Mickey 🐭
type: note
tags: [note]
---

# 1. Introduction

The rapid proliferation of large language model (LLM) agents has exposed a fundamental tension in their memory architectures: while these systems grow increasingly capable in reasoning and tool use, their ability to *remember*—and more importantly, to *act on what they remember*—remains remarkably primitive. Current approaches treat memory as inert data to be stored and retrieved, much like a filing cabinet that waits passively for a query. We argue this framing is fundamentally insufficient. Memory, when properly designed, should function not as data but as *code*—self-describing, self-modifying, and capable of triggering computation without external invocation.

Consider a concrete scenario drawn from the operation of a real, continuously-running AI agent system. The system employs multiple LLMs of varying capability: a frontier model (Claude Opus) for complex reasoning, a mid-tier model (Claude Sonnet) for daily analysis, and a cost-efficient model (GPT-5-mini) for routine monitoring tasks. All three models share a common memory store. When a new piece of information arrives—say, a user's investment preference—it must be remembered in a form that the frontier model can deeply reason about, the mid-tier model can reliably act upon, and the budget model can at least recognize as relevant. Existing memory systems \cite{xu2025amem, li2025memos, packer2023memgpt} offer no mechanism for this *graduated comprehension*: they store memory in a single representation and hope every consumer can make equal use of it.

This scenario illustrates three deficiencies that pervade the current landscape of agent memory:

**The Passivity Problem.** Memories in existing systems are fundamentally passive. Whether organized as vector embeddings \cite{lewis2020rag}, knowledge graphs \cite{ji2022hipporag}, or structured notes \cite{xu2025amem}, memories wait to be queried. They cannot initiate action. A memory encoding the fact that "the user's portfolio should be rebalanced when tech stocks exceed 40% allocation" cannot, by itself, trigger a portfolio check. It requires an external system—a cron job, a rule engine, or a user prompt—to activate it. This separation of knowledge from action is not a minor inconvenience; it is an architectural limitation that forces agent designers to duplicate intent across memory stores and execution logic.

**The Rigidity Problem.** Once stored, memories in most systems are either immutable or subject to wholesale replacement. A-MEM \cite{xu2025amem} introduced *memory evolution*—the ability for new memories to trigger updates to existing ones—which represents genuine progress. However, this evolution operates only on descriptive attributes (keywords, tags, contextual descriptions). The *behavior* of a memory—how it should be retrieved, when it becomes irrelevant, what confidence level it carries—remains fixed at creation time. A memory cannot learn from its own usage patterns to adjust its retrieval threshold, nor can it schedule its own obsolescence when the information it encodes becomes stale.

**The One-Size-Fits-All Problem.** The implicit assumption across all major memory frameworks is that memory has a single consumer. MemOS \cite{li2025memos} introduced the important insight that memory should be managed as a first-class system resource, analogous to processes or file handles in an operating system. Yet even MemOS assumes a uniform consumption model. In practice, as Hu et al.'s comprehensive survey \cite{hu2025memory_survey} documents, agent memory must serve heterogeneous consumers—models of different capability tiers, different downstream tasks, and different latency/cost budgets. No existing system addresses this heterogeneity at the memory representation level.

We propose **Memory-as-Code (MaC)**, a memory architecture grounded in a simple but far-reaching principle: *memories should be programs, not data*. Drawing on the concept of *homoiconicity* from the Lisp tradition—where code and data share the same representation \cite{mccarthy1960lisp, akhmechet2006nature_of_lisp}—MaC encodes each memory as an S-expression that simultaneously describes what is remembered *and* prescribes how that memory should behave. A MaC memory carries its own trigger conditions (when should this memory activate?), decay policies (when should this memory fade?), confidence tracking (how reliable is this memory?), and cross-references (what other memories is this connected to?). Crucially, these behavioral specifications are not external metadata managed by a separate system; they are *part of the memory itself*, written in the same representational language.

This design yields three architectural consequences that distinguish MaC from prior work:

**1. Executable Memory.** A MaC memory is not merely stored and retrieved; it can be *evaluated*. When a trigger condition is met—a keyword appears in conversation, a temporal threshold is crossed, a linked memory is updated—the memory fires, producing an action without requiring an external orchestrator. This collapses the traditional separation between "memory store" and "rule engine" into a single unified substrate.

**2. Graduated Comprehension via Multi-Layer Compilation.** Each MaC memory is compiled into three layers of decreasing complexity: Layer 1 (L1) is a natural-language summary accessible to any model; Layer 2 (L2) encodes structured metadata (triggers, confidence, decay) in a key-value format interpretable by mid-tier models; Layer 3 (L3) contains the full S-expression with meta-rules, closure contexts, and chain links, requiring frontier-model reasoning to fully exploit. This stratification ensures that the same memory degrades gracefully across model capabilities—a property we term *graduated comprehension*. An important corollary is that model capability becomes an implicit permission system: a model that cannot parse L3 meta-rules simply cannot execute them, providing *capability-as-permission* safety without additional access control.

**3. Self-Correcting Lifecycle.** MaC memories carry meta-rules that govern their own evolution. A memory that is frequently retrieved and found useful increases its confidence score; one that is retrieved but unhelpful degrades. Memories that remain unaccessed beyond a configurable horizon are flagged as forget candidates. When accessed again after a period of neglect, a memory's confidence can *revive*. These dynamics are not managed by an external garbage collector; they are *encoded within each memory's S-expression*, enabling fully autonomous lifecycle management.

The theoretical motivation for MaC draws on two traditions. From cognitive science, Fodor's *Language of Thought* hypothesis \cite{fodor1975lot} posits that human cognition operates over an internal representational language ("Mentalese") distinct from natural language—a symbolic substrate that supports compositional thought. We extend this hypothesis to artificial agents: just as humans do not think in English or Mandarin but in a more structured internal code, AI agents should not store memories in natural language but in a *computational memory language* optimized for machine reasoning. From computer science, the Lisp tradition of homoiconicity \cite{mccarthy1960lisp} demonstrates that when code and data share the same representation, programs can inspect and modify themselves—precisely the self-referential capability that memory evolution requires.

We ground these ideas in a concrete implementation embedded within a continuously-running agent system (Mickey, operational since January 2026). Our experimental evaluation addresses three hypotheses:

- **H1 (Executable Triggers):** S-expression-encoded memories can reliably trigger on relevant inputs while suppressing false positives, achieving F1 ≥ 0.9 on a curated test set.
- **H2 (Graduated Comprehension):** Different-capability LLMs extract qualitatively different but semantically consistent information from the same multi-layer memory encoding.
- **H3 (Self-Correction):** Memories with embedded meta-rules autonomously adjust confidence and decay parameters in response to usage feedback, without external LLM calls.

Experiments E1 and E3 validate H1, demonstrating perfect precision and recall (F1 = 1.0) on a 15-case trigger test suite with 5 distinct memories. Experiment E4 validates H3, showing correct self-correction across five scenarios including positive reinforcement, negative reinforcement, mixed usage, forget-candidate detection, and revival from degraded confidence, plus a 90-day lifecycle simulation. H2 is partially validated through framework experiments (E2, E5) with analysis of model-specific response patterns, though full quantitative comparison awaits refined evaluation methodology (discussed in Section 7).

The contributions of this paper are:

1. **The Memory-as-Code paradigm**: a formal framework in which memories are homoiconic S-expressions that encode both content and behavior, unifying memory storage and execution logic.
2. **Graduated Comprehension**: a multi-layer compilation scheme enabling heterogeneous model consumption of the same memory, with capability-as-permission as a safety corollary.
3. **Self-correcting memory lifecycle**: meta-rules embedded within memories that enable autonomous confidence adjustment, decay management, and forget/revive dynamics.
4. **Empirical validation** through three completed experiments (encoder, triggers, self-correction) and three framework experiments (comprehension, cross-compilation, A/B comparison) conducted within a production agent system.

The remainder of this paper is organized as follows. Section 2 surveys related work in agent memory systems, neurosymbolic AI, and cognitive memory models. Section 3 presents the Mentalese Hypothesis motivating MaC's design. Section 4 describes the MaC architecture in detail: the S-expression format, the three-layer compilation scheme, and the trigger/decay/correction engines. Section 5 discusses our implementation within the Mickey agent system. Section 6 presents experimental results. Section 7 discusses limitations, safety considerations, and evaluation methodology challenges. Section 8 concludes with future directions.