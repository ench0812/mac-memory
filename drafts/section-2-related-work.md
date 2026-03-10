---
date: 2026-03-08
section: 2
title: Related Work
status: first-draft
word_count: ~3500
author: Mickey 🐭
---

# 2. Related Work

MaC draws on and departs from three bodies of work: agent memory systems (§2.1), neurosymbolic approaches to LLM reasoning (§2.2), and cognitive science models of memory (§2.3). We organize each subsection around the specific gap that MaC addresses.

## 2.1 Agent Memory Systems

The past two years have seen a rapid expansion of memory architectures for LLM agents. Following Hu et al.'s \cite{hu2025memory_survey} taxonomy, we organize these systems along three dimensions—Forms (how memory is stored), Functions (what memory is used for), and Dynamics (how memory evolves)—and identify the gaps MaC fills in each.

### 2.1.1 Memory Forms: From Flat Vectors to Structured Representations

The simplest agent memories are flat vector stores, where each interaction is embedded and stored for later retrieval via cosine similarity. RAG-based systems \cite{lewis2020rag} popularized this approach, and frameworks like LangChain and LlamaIndex provide commodity infrastructure for it. While effective for factual recall, flat embeddings discard structure: two memories with identical embeddings may differ critically in their temporal context, reliability, or relevance conditions.

Structured approaches introduce richer memory representations. HippoRAG \cite{ji2022hipporag} organizes memories into a knowledge graph inspired by hippocampal indexing, enabling associative retrieval beyond keyword matching. A-MEM \cite{xu2025amem} adopts the Zettelkasten paradigm, packaging each memory as a structured note with keywords, tags, contextual descriptions, embeddings, and inter-memory links. MemOS \cite{li2025memos} introduces the MemCube abstraction, unifying plaintext, activation (KV-cache), and parametric (LoRA) memory representations under a single governance framework with lifecycle management, access control, and scheduling.

These systems progressively enrich the memory *container* but do not change the fundamental nature of the *contents*. A-MEM's structured notes are still data to be retrieved; MemOS's MemCubes are still resources to be managed by an external scheduler. None of them make the memory itself executable—capable of evaluating conditions, triggering actions, or modifying its own metadata. MaC's S-expression encoding fills this gap: a MaC memory is simultaneously a data record and a program, encoding not just *what* is remembered but *how it should behave*.

### 2.1.2 Memory Functions: Beyond Passive Retrieval

Hu et al. \cite{hu2025memory_survey} categorize memory functions into factual (user/environment knowledge), experiential (cases, strategies, skills), and working (current-task state). Among these, *experiential memory* is most relevant to MaC, particularly its subdivision into case-based, strategy-based, and skill-based forms.

**Case-based memory** stores raw interaction trajectories for later reuse. ExpeL \cite{zhao2024expel} and Memento \cite{wang2024memento} retain complete task traces, enabling few-shot retrieval but consuming substantial storage. **Strategy-based memory** abstracts from raw cases to generalizable insights. AWM \cite{chen2024awm} and Dynamic Cheatsheet \cite{suzgun2025dynamic_cheatsheet} accumulate task-solving strategies during inference, reducing redundant computation. **Skill-based memory** compiles experience into executable artifacts. Voyager \cite{wang2024voyager} maintains a growing library of JavaScript skills for Minecraft, where each skill is a self-contained function that can be directly invoked—the closest existing analogue to executable memory.

MaC differs from skill-based memory in a crucial respect. Voyager's skills are *externally triggered*: an orchestrator decides which skill to invoke. MaC memories are *self-triggered*: the trigger condition is embedded within the memory itself, enabling autonomous activation without an external dispatch loop. Furthermore, MaC memories carry lifecycle semantics (decay, confidence, self-correction) that Voyager's skills lack—a skill in Voyager never expires, never loses confidence, and never modifies itself in response to feedback.

### 2.1.3 Memory Dynamics: Evolution Without Self-Awareness

A-MEM's memory evolution mechanism \cite{xu2025amem} represents the state of the art in dynamic memory systems. When a new memory is created, it triggers updates to the keywords, tags, and contextual descriptions of related existing memories—a form of *attribute-level evolution*. This captures the important insight that learning something new can change how we understand what we already know.

However, A-MEM's evolution has three limitations. First, it operates only on *descriptive* attributes, not *behavioral* ones: a memory's retrieval strategy, decay policy, and confidence remain fixed regardless of how the memory's context changes. Second, evolution is unidirectional and unchecked: there is no mechanism to detect or roll back erroneous updates, creating a risk of *error propagation through evolution* where a hallucinated memory contaminates its neighbors \cite{xu2025amem}. Third, the system has no meta-cognition about its own memory—no way to assess whether its memory architecture is performing well or poorly.

MemOS addresses some of these concerns at the infrastructure level, introducing lifecycle states (generated → activated → merged → archived → expired), time-machine snapshots for rollback, and governance policies for access control. But MemOS's lifecycle is *externally imposed* by the operating system layer; the memories themselves have no say in their own management.

MaC synthesizes A-MEM's insight (memory should evolve) with MemOS's infrastructure concern (memory needs lifecycle management) while going beyond both: in MaC, **the lifecycle rules are part of the memory**. Each S-expression encodes its own decay strategy, confidence update logic, and forget/revive conditions. Evolution is not attribute-level (changing descriptions) but *structural* (changing behavior). And evolution is constrained by a constitutional hierarchy (§4.5) that prevents unbounded self-modification.

### 2.1.4 Emerging Directions

Several recent systems explore directions complementary to MaC. Memory-R1 \cite{yan2025memoryr1} uses reinforcement learning to train memory extraction modules, learning *what* to remember rather than relying on heuristic summarization. EverMemOS \cite{hu2026evermemos} introduces self-organizing MemCell/MemScene structures for autonomous memory organization. Second-Me proposes L0/L1/L2 memory tiers for personal AI. These systems share MaC's intuition that memory should be more active and autonomous, but none adopt the homoiconic representation that enables memory to be simultaneously data and program.

## 2.2 Neurosymbolic AI and LLMs

MaC's use of S-expressions positions it at the intersection of neural language models and symbolic computation. This intersection has received growing attention.

### 2.2.1 LLMs as Symbolic Reasoners

De la Torre \cite{delatorre2025lisp_metaprogramming} proposed a framework in which an LLM operates within a persistent Lisp REPL, using Lisp's metaprogramming capabilities to build and refine its own tools. This work demonstrates that LLMs can meaningfully interact with symbolic systems, but focuses on *tool creation* rather than *memory architecture*. MaC extends this insight: if LLMs can reason about and generate Lisp code, they can also reason about and modify Lisp-encoded memories.

However, LLMs have documented limitations in symbolic computation. Pantazopoulos et al. \cite{pantazopoulos2025symbolic_limits} show that current architectures struggle with tasks requiring strict symbolic manipulation (e.g., variable binding, recursive evaluation). This is not a refutation of MaC but a design constraint: MaC does not require LLMs to *execute* S-expressions symbolically. Instead, the S-expression serves as a structured representation that LLMs *interpret* at the level their capabilities permit—which is precisely why the graduated comprehension scheme (L1/L2/L3) is essential. A model that cannot symbolically evaluate a trigger condition can still read the L1 natural-language summary of what that trigger does.

### 2.2.2 Neurosymbolic Integration

The broader neurosymbolic AI program seeks to combine neural networks' pattern recognition with symbolic systems' compositional reasoning \cite{garcez2023neurosymbolic, wu2025neurosymbolic_survey}. MaC contributes a specific instantiation: the S-expression is the symbolic component; the LLM is the neural interpreter. Unlike most neurosymbolic systems that require custom training pipelines, MaC operates entirely at inference time—any LLM can consume MaC memories without fine-tuning, and the three-layer encoding ensures that even models with weak symbolic capabilities benefit from the structured representation.

### 2.2.3 Code as Memory

A lineage of work treats executable code as a form of memory. Voyager \cite{wang2024voyager} stores Minecraft skills as JavaScript functions. SkillWeaver and Alita \cite{hu2025memory_survey} compile agent experience into MCP-compatible tools. JARVIS-1 \cite{wang2023jarvis} maintains a multimodal memory for embodied agents that includes executable plans. MaC generalizes this pattern: rather than restricting executable memory to a specific domain (game skills, API tools), MaC proposes a *universal memory language* in which any memory—factual, experiential, or procedural—can carry executable semantics.

## 2.3 Cognitive Science: Language of Thought

### 2.3.1 Fodor's Mentalese Hypothesis

Fodor's Language of Thought (LoT) hypothesis \cite{fodor1975lot} argues that human cognition operates over an internal symbolic language—*Mentalese*—that is distinct from any natural language. Mentalese is compositional (complex thoughts are built from simpler components), productive (a finite vocabulary generates infinite thoughts), and systematic (the ability to think "John loves Mary" entails the ability to think "Mary loves John"). These properties are required for rational thought and cannot be fully captured by natural language, which is ambiguous, context-dependent, and designed for communication rather than computation.

We extend Fodor's hypothesis to AI agents: **LLM agents, like humans, need an internal representational language optimized for computation rather than communication.** Natural language is a lossy channel—it introduces ambiguity and wastes tokens on redundant syntactic structure. An S-expression, by contrast, is unambiguous, compositional, and machine-parseable while remaining LLM-interpretable. MaC's S-expression format is our candidate for an *AI Mentalese*—a language in which memories are expressed in a form optimized for machine reasoning.

### 2.3.2 Constructive Memory and Offline Consolidation

Contemporary cognitive science has moved beyond the "filing cabinet" model of memory. Human memories are not passively stored and faithfully retrieved; they are actively *reconstructed* at recall time, shaped by current context, emotional state, and subsequent experience \cite{bartlett1932remembering, schacter2012constructive}. Furthermore, memory consolidation occurs during sleep—an offline process that reorganizes, abstracts, and strengthens important memories while pruning irrelevant ones \cite{stickgold2005sleep}.

MaC's design echoes these principles. The self-correction engine (§4.4) implements a form of constructive memory: a memory's confidence and decay parameters change in response to usage, so the "same" memory is effectively different each time it is consulted. The forget/revive mechanism (§4.4) parallels offline consolidation: memories that are not accessed degrade, but can be revived if they become relevant again—capturing the observation that human memories are not deleted but become harder to retrieve until a relevant cue reactivates them.

### 2.3.3 Cognitive Architectures

Classical cognitive architectures—ACT-R \cite{anderson2004actr}, SOAR \cite{laird2012soar}, and more recently the Common Model of Cognition \cite{laird2017standard}—have long implemented structured, active memory systems with decay, spreading activation, and production rules. MaC shares their spirit but operates in a fundamentally different computational substrate. Where ACT-R uses hand-crafted production rules and carefully calibrated activation functions, MaC leverages the LLM's generative capabilities to *interpret* (rather than formally execute) S-expressions. This trade-off sacrifices formal guarantees for flexibility: a MaC memory can encode arbitrary conditions in natural-language-enriched S-expressions that classical architectures could not represent.

## 2.4 Positioning Summary

Table \ref{tab:comparison} summarizes how MaC relates to the most relevant prior systems.

| System | Memory Form | Executable? | Self-Evolving? | Multi-Model? | Lifecycle? |
|--------|------------|-------------|----------------|--------------|------------|
| RAG \cite{lewis2020rag} | Flat vectors | ✗ | ✗ | ✗ | ✗ |
| HippoRAG \cite{ji2022hipporag} | Knowledge graph | ✗ | ✗ | ✗ | ✗ |
| A-MEM \cite{xu2025amem} | Structured notes | ✗ | Attribute-level | ✗ | ✗ |
| MemOS \cite{li2025memos} | MemCube (3 types) | ✗ | External lifecycle | ✗ | External |
| Voyager \cite{wang2024voyager} | Code (JS skills) | Partial^† | ✗ | ✗ | ✗ |
| **MaC (ours)** | **S-expression** | **✓** | **Structural** | **✓ (L1/L2/L3)** | **Embedded** |

^† Voyager's skills are executable but externally triggered and domain-specific (Minecraft).

MaC's key differentiation is the convergence of four properties that no prior system combines: (1) homoiconic representation enabling memory-as-program, (2) graduated comprehension via multi-layer compilation, (3) self-correcting lifecycle embedded within each memory, and (4) constitutional governance constraining self-modification.
