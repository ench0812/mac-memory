---
date: 2026-03-12
section: 2
title: Related Work (v2)
status: revised-draft
word_count: ~5000
author: Mickey 🐭
revision_from: section-2-related-work.md (2026-03-08)
changes: |
  - Added §2.1.5 Personality and Emotion in Agent Memory (from S4 literature)
  - Expanded §2.1.4 with CoALA, Always On Memory Agent
  - Strengthened §2.3.3 with deeper ACT-R/SOAR comparison (N6 concern)
  - Added §2.4 Constitutional Governance and Self-Modification (from N2)
  - Updated comparison table with personality and governance dimensions
  - Added CoALA to §2.1.1
type: note
tags: [note]
---

# 2. Related Work

MaC draws on and departs from four bodies of work: agent memory systems (§2.1), neurosymbolic approaches to LLM reasoning (§2.2), cognitive science models of memory (§2.3), and governance of self-modifying systems (§2.4). We organize each subsection around the specific gap that MaC addresses.

## 2.1 Agent Memory Systems

The past two years have seen a rapid expansion of memory architectures for LLM agents. Following Hu et al.'s \cite{hu2025memory_survey} taxonomy, we organize these systems along three dimensions—Forms (how memory is stored), Functions (what memory is used for), and Dynamics (how memory evolves)—and identify the gaps MaC fills in each.

### 2.1.1 Memory Forms: From Flat Vectors to Structured Representations

The simplest agent memories are flat vector stores, where each interaction is embedded and stored for later retrieval via cosine similarity. RAG-based systems \cite{lewis2020rag} popularized this approach, and frameworks like LangChain and LlamaIndex provide commodity infrastructure for it. While effective for factual recall, flat embeddings discard structure: two memories with identical embeddings may differ critically in their temporal context, reliability, or relevance conditions.

Structured approaches introduce richer memory representations. HippoRAG \cite{ji2022hipporag} organizes memories into a knowledge graph inspired by hippocampal indexing, enabling associative retrieval beyond keyword matching. A-MEM \cite{xu2025amem} adopts the Zettelkasten paradigm, packaging each memory as a structured note with keywords, tags, contextual descriptions, embeddings, and inter-memory links. MemOS \cite{li2025memos} introduces the MemCube abstraction, unifying plaintext, activation (KV-cache), and parametric (LoRA) memory representations under a single governance framework with lifecycle management, access control, and scheduling.

At the architectural level, CoALA \cite{sumers2023coala} proposed a systematic framework for language agent cognition, decomposing memory into episodic (raw experience), semantic (abstracted knowledge), and procedural (code/skills) modules—a classification inspired by cognitive science. CoALA identified that procedural memory (stored as code) enables agents to update their own behavior, foreshadowing the executable memory concept. However, CoALA treats these memory types as distinct modules managed by separate retrieval mechanisms; it does not propose a unified representation in which a single memory simultaneously carries semantic content, procedural behavior, and lifecycle rules.

These systems progressively enrich the memory *container* but do not change the fundamental nature of the *contents*. A-MEM's structured notes are still data to be retrieved; MemOS's MemCubes are still resources to be managed by an external scheduler; CoALA's procedural memory is executable but architecturally segregated from episodic and semantic memory. None of them make an individual memory itself executable—capable of evaluating conditions, triggering actions, or modifying its own metadata. MaC's S-expression encoding fills this gap: a MaC memory is simultaneously a data record and a program, encoding not just *what* is remembered but *how it should behave*.

### 2.1.2 Memory Functions: Beyond Passive Retrieval

Hu et al. \cite{hu2025memory_survey} categorize memory functions into factual (user/environment knowledge), experiential (cases, strategies, skills), and working (current-task state). Among these, *experiential memory* is most relevant to MaC, particularly its subdivision into case-based, strategy-based, and skill-based forms.

**Case-based memory** stores raw interaction trajectories for later reuse. ExpeL \cite{zhao2024expel} and Memento \cite{wang2024memento} retain complete task traces, enabling few-shot retrieval but consuming substantial storage. **Strategy-based memory** abstracts from raw cases to generalizable insights. AWM \cite{chen2024awm} and Dynamic Cheatsheet \cite{suzgun2025dynamic_cheatsheet} accumulate task-solving strategies during inference, reducing redundant computation. **Skill-based memory** compiles experience into executable artifacts. Voyager \cite{wang2024voyager} maintains a growing library of JavaScript skills for Minecraft, where each skill is a self-contained function that can be directly invoked—the closest existing analogue to executable memory.

MaC differs from skill-based memory in a crucial respect. Voyager's skills are *externally triggered*: an orchestrator decides which skill to invoke. MaC memories are *self-triggered*: the trigger condition is embedded within the memory itself, enabling autonomous activation without an external dispatch loop. Furthermore, MaC memories carry lifecycle semantics (decay, confidence, self-correction) that Voyager's skills lack—a skill in Voyager never expires, never loses confidence, and never modifies itself in response to feedback.

### 2.1.3 Memory Dynamics: Evolution Without Self-Awareness

A-MEM's memory evolution mechanism \cite{xu2025amem} represents the state of the art in dynamic memory systems. When a new memory is created, it triggers updates to the keywords, tags, and contextual descriptions of related existing memories—a form of *attribute-level evolution*. This captures the important insight that learning something new can change how we understand what we already know.

However, A-MEM's evolution has three limitations. First, it operates only on *descriptive* attributes, not *behavioral* ones: a memory's retrieval strategy, decay policy, and confidence remain fixed regardless of how the memory's context changes. Second, evolution is unidirectional and unchecked: there is no mechanism to detect or roll back erroneous updates, creating a risk of *error propagation through evolution* where a hallucinated memory contaminates its neighbors \cite{xu2025amem}. Third, the system has no meta-cognition about its own memory—no way to assess whether its memory architecture is performing well or poorly.

MemOS addresses some of these concerns at the infrastructure level, introducing lifecycle states (generated → activated → merged → archived → expired), time-machine snapshots for rollback, and governance policies for access control. But MemOS's lifecycle is *externally imposed* by the operating system layer; the memories themselves have no say in their own management.

MaC synthesizes A-MEM's insight (memory should evolve) with MemOS's infrastructure concern (memory needs lifecycle management) while going beyond both: in MaC, **the lifecycle rules are part of the memory**. Each S-expression encodes its own decay strategy, confidence update logic, and forget/revive conditions. Evolution is not attribute-level (changing descriptions) but *structural* (changing behavior). And evolution is constrained by a constitutional hierarchy (§5) that prevents unbounded self-modification.

### 2.1.4 Emerging Directions

Several recent systems explore directions complementary to MaC.

**Learning what to remember.** Memory-R1 \cite{yan2025memoryr1} uses reinforcement learning to train memory extraction modules, learning *what* to remember rather than relying on heuristic summarization—addressing memory formation rather than memory representation.

**Self-organizing memory.** EverMemOS \cite{hu2026evermemos} introduces self-organizing MemCell/MemScene structures for autonomous memory organization, and Second-Me proposes L0/L1/L2 memory tiers for personal AI—both sharing MaC's intuition that memory should be more autonomous.

**LLM-native memory management.** The recently open-sourced Always On Memory Agent \cite{saboo2026aoma} (Google Cloud Platform, March 2026) takes the provocative position that vector databases are unnecessary: it uses Gemini directly to read, organize, and consolidate structured memories stored in SQLite, performing scheduled consolidation every 30 minutes. This aligns with MaC's philosophy that the LLM should be the memory's interpreter, not merely its consumer. However, the Always On Memory Agent treats the LLM as an external organizer acting on passive data; MaC goes further by embedding the organizational logic *within the memory itself*.

**Cognitive design patterns.** Work on applying cognitive design patterns to LLM agents \cite{agi25cogpatterns} has identified reconsideration, metalevel reasoning, and episodic memory as transferable patterns from classical cognitive architectures—providing a bridge between ACT-R/SOAR traditions and modern LLM agents that MaC explicitly builds upon.

None of these systems adopt the homoiconic representation that enables memory to be simultaneously data and program, nor do they address personality-modulated memory dynamics.

### 2.1.5 Personality and Emotion in Agent Memory

A small but growing body of work explores the interaction between agent personality/emotion and memory.

**Emotional RAG** \cite{emotionalrag2024} tags memories with emotion labels and uses the agent's current emotional state to bias retrieval, implementing mood-dependent memory from psychology \cite{bower1981mood}. This demonstrates that affective state can meaningfully improve retrieval quality. However, emotions are transient (session-level), while personality traits are stable (agent-level). Emotional RAG captures *state-dependent* memory but not *trait-dependent* memory.

**MemoryBank** \cite{zhong2024memorybank} applies Ebbinghaus's forgetting curve to memory decay, introducing psychologically-grounded temporal dynamics. However, all memories follow the same decay curve regardless of the agent's personality—a design that ignores robust psychological findings linking personality traits to differential memory retention. High-neuroticism individuals show enhanced recall and slower decay for negative emotional events \cite{rusting1998personality, gotlib2010cognition}; high-conscientiousness individuals show stronger retention of procedural and rule-based memories.

**Stanford Generative Agents** \cite{park2023generative} introduced a weighted recall formula (Score = α × Recency + β × Importance + γ × Relevance) that captures situational factors. This formula has become the *de facto* baseline for agent memory retrieval. However, the three weights are globally fixed—they do not vary with the agent's personality. A high-conscientiousness agent should assign higher β to importance; a high-openness agent should assign higher γ to relevance of novel information.

MaC addresses this gap through two mechanisms: (1) a `:personality-affinity` field on each memory that modulates retrieval priority based on the agent's OCEAN-5 personality vector, and (2) personality-dependent decay rate modifiers that adjust effective half-life based on trait-memory type interactions. Crucially, personality acts as a *soft weighting layer* applied after hard predicate filtering—it reranks the candidate set without creating blind spots where personality prevents access to any memory.

## 2.2 Neurosymbolic AI and LLMs

MaC's use of S-expressions positions it at the intersection of neural language models and symbolic computation. This intersection has received growing attention.

### 2.2.1 LLMs as Symbolic Reasoners

De la Torre \cite{delatorre2025lisp_metaprogramming} proposed a framework in which an LLM operates within a persistent Lisp REPL, using Lisp's metaprogramming capabilities to build and refine its own tools. This work demonstrates that LLMs can meaningfully interact with symbolic systems, but focuses on *tool creation* rather than *memory architecture*. MaC extends this insight: if LLMs can reason about and generate Lisp code, they can also reason about and modify Lisp-encoded memories.

However, LLMs have documented limitations in symbolic computation. Pantazopoulos et al. \cite{pantazopoulos2025symbolic_limits} show that current architectures struggle with tasks requiring strict symbolic manipulation (e.g., variable binding, recursive evaluation). This is not a refutation of MaC but a design constraint: MaC does not require LLMs to *execute* S-expressions symbolically. Instead, the S-expression serves as a structured representation that LLMs *interpret* at the level their capabilities permit—which is precisely why the graduated comprehension scheme (L1/L2/L3) is essential. A model that cannot symbolically evaluate a trigger condition can still read the L1 natural-language summary of what that trigger does.

### 2.2.2 Neurosymbolic Integration

The broader neurosymbolic AI program seeks to combine neural networks' pattern recognition with symbolic systems' compositional reasoning \cite{garcez2023neurosymbolic, wu2025neurosymbolic_survey, xiong2024converging}. MaC contributes a specific instantiation: the S-expression is the symbolic component; the LLM is the neural interpreter. Unlike most neurosymbolic systems that require custom training pipelines, MaC operates entirely at inference time—any LLM can consume MaC memories without fine-tuning, and the three-layer encoding ensures that even models with weak symbolic capabilities benefit from the structured representation.

### 2.2.3 Code as Memory

A lineage of work treats executable code as a form of memory. Voyager \cite{wang2024voyager} stores Minecraft skills as JavaScript functions. SkillWeaver and Alita \cite{hu2025memory_survey} compile agent experience into MCP-compatible tools. JARVIS-1 \cite{wang2023jarvis} maintains a multimodal memory for embodied agents that includes executable plans. MaC generalizes this pattern: rather than restricting executable memory to a specific domain (game skills, API tools), MaC proposes a *universal memory language* in which any memory—factual, experiential, or procedural—can carry executable semantics.

## 2.3 Cognitive Science: Language of Thought and Memory Architecture

### 2.3.1 Fodor's Mentalese Hypothesis

Fodor's Language of Thought (LoT) hypothesis \cite{fodor1975lot} argues that human cognition operates over an internal symbolic language—*Mentalese*—that is distinct from any natural language. Mentalese is compositional (complex thoughts are built from simpler components), productive (a finite vocabulary generates infinite thoughts), and systematic (the ability to think "John loves Mary" entails the ability to think "Mary loves John"). These properties are required for rational thought and cannot be fully captured by natural language, which is ambiguous, context-dependent, and designed for communication rather than computation.

We extend Fodor's hypothesis to AI agents: **LLM agents, like humans, need an internal representational language optimized for computation rather than communication.** Natural language is a lossy channel—it introduces ambiguity and wastes tokens on redundant syntactic structure. An S-expression, by contrast, is unambiguous, compositional, and machine-parseable while remaining LLM-interpretable. MaC's S-expression format is our candidate for an *AI Mentalese*—a language in which memories are expressed in a form optimized for machine reasoning.

### 2.3.2 Constructive Memory and Offline Consolidation

Contemporary cognitive science has moved beyond the "filing cabinet" model of memory. Human memories are not passively stored and faithfully retrieved; they are actively *reconstructed* at recall time, shaped by current context, emotional state, and subsequent experience \cite{bartlett1932remembering, schacter2012constructive}. Furthermore, memory consolidation occurs during sleep—an offline process that reorganizes, abstracts, and strengthens important memories while pruning irrelevant ones \cite{stickgold2005sleep}.

MaC's design echoes these principles. The self-correction engine implements a form of constructive memory: a memory's confidence and decay parameters change in response to usage, so the "same" memory is effectively different each time it is consulted. The forget/revive mechanism parallels offline consolidation: memories that are not accessed degrade, but can be revived if they become relevant again—capturing the observation that human memories are not deleted but become harder to retrieve until a relevant cue reactivates them.

### 2.3.3 Cognitive Architectures: ACT-R, SOAR, and the Common Model of Cognition

Classical cognitive architectures have long implemented structured, active memory systems with properties superficially similar to MaC. Understanding the precise relationship is essential for positioning our contribution.

**ACT-R** \cite{anderson2004actr} maintains declarative memory (facts) and procedural memory (IF-THEN production rules) as distinct modules. Declarative memories have activation levels that decay logarithmically with time and receive spreading activation from associated memories. Production rules fire when their conditions match working memory contents—a form of executable memory. ACT-R's activation equation (Base-Level + Spreading Activation + Partial Matching + Noise) provides a mathematically precise model of memory retrieval that has been validated against human behavioral data over four decades.

**SOAR** \cite{laird2012soar} uses a universal subgoaling mechanism where all knowledge is encoded as production rules that propose, evaluate, and apply operators. When an impasse occurs (no operator can be selected), SOAR creates a subgoal and uses *chunking* to compile the solution into a new production rule—a form of learned executable memory. SOAR's long-term memory modules (semantic, episodic, procedural) interact through working memory, with retrieval driven by cue-based activation.

**The Common Model of Cognition** \cite{laird2017standard} abstracts over ACT-R and SOAR to identify shared principles: distinct long-term memory modules (declarative, procedural, spatial), a limited-capacity working memory, perception-action interfaces, and learning mechanisms that compile experience into procedural knowledge.

MaC shares three principles with these architectures: (1) memory has activation/confidence levels that change over time, (2) some memories carry executable conditions (production rules ≈ trigger predicates), and (3) experience can be compiled into reusable knowledge. However, MaC departs in four important ways:

1. **Unified representation.** ACT-R and SOAR strictly segregate declarative and procedural memory into different modules with different representations and retrieval mechanisms. MaC unifies them: a single S-expression encodes both content (what happened) and procedure (what to do about it). This mirrors the insight from embodied cognition that the boundary between "knowing that" and "knowing how" is more porous than classical architectures assume \cite{barsalou2008grounded}.

2. **Self-referential lifecycle.** ACT-R's activation levels are computed by an external equation; SOAR's chunking is performed by an external learning mechanism. MaC memories carry their own lifecycle rules—a memory's `:meta-rule` specifies how its own confidence should change in response to usage. The lifecycle is *endogenous* rather than *exogenous*.

3. **Graduated consumption.** Classical architectures assume a single cognitive processor. MaC's three-layer compilation scheme addresses a novel challenge: heterogeneous processors (LLMs of varying capability) consuming the same memory store. This has no analogue in ACT-R or SOAR.

4. **LLM-native interpretation.** ACT-R and SOAR use formal pattern matching for production rule evaluation. MaC leverages the LLM's generative capabilities to *interpret* (rather than formally execute) S-expressions, trading formal guarantees for flexibility: a MaC memory can encode arbitrary conditions in natural-language-enriched S-expressions that classical architectures could not represent (e.g., `(ctx-contains-any "user seems stressed" "emotional conversation")`).

## 2.4 Governance of Self-Modifying Systems

When memory is executable and self-modifying, governance becomes a first-class concern. This intersects with work on AI alignment, constitutional AI, and safe self-improvement.

**Constitutional AI** \cite{bai2022constitutional} trains models to follow principles specified in a constitution, but operates at the model training level rather than the memory architecture level. MaC's constitutional governance operates at runtime: the hierarchy Constitution → Soul → Brain → Storage constrains what kinds of memory modifications are permissible, with each layer able to veto changes to the layers below it.

**Bounded self-modification** has been explored in the AI safety literature \cite{soares2015corrigibility}. The key concern is that a self-modifying system might modify its own modification rules, leading to unbounded change. MaC addresses this through a simple but effective mechanism: the Constitution layer is immutable by the system itself and can only be modified by the human operator. This is analogous to the separation between kernel mode and user mode in operating systems—the system can freely modify user-level memories but cannot alter its own safety invariants.

**Sandbox verification** for executable memory draws on the BPF verifier model from Linux kernel security: before a memory's predicate is evaluated, it is checked for bounded execution (no unbounded loops, no external side effects). This ensures that making memory executable does not introduce arbitrary code execution risks—the predicates are Turing-incomplete by design, restricted to propositional logic with bounded quantification.

## 2.5 Positioning Summary

Table \ref{tab:comparison} summarizes how MaC relates to the most relevant prior systems across seven dimensions.

| System | Memory Form | Executable? | Self-Evolving? | Multi-Model? | Lifecycle? | Personality? | Governance? |
|--------|------------|-------------|----------------|--------------|------------|-------------|------------|
| RAG \cite{lewis2020rag} | Flat vectors | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| HippoRAG \cite{ji2022hipporag} | Knowledge graph | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| A-MEM \cite{xu2025amem} | Structured notes | ✗ | Attribute-level | ✗ | ✗ | ✗ | ✗ |
| MemOS \cite{li2025memos} | MemCube (3 types) | ✗ | External lifecycle | ✗ | External | ✗ | External |
| CoALA \cite{sumers2023coala} | Modular (3 types) | Partial^† | ✗ | ✗ | ✗ | ✗ | ✗ |
| Voyager \cite{wang2024voyager} | Code (JS skills) | Partial^‡ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Stanford GA \cite{park2023generative} | Natural language | ✗ | ✗ | ✗ | Time-decay | Fixed weights | ✗ |
| Emotional RAG \cite{emotionalrag2024} | Emotion-tagged | ✗ | ✗ | ✗ | ✗ | Mood (transient) | ✗ |
| MemoryBank \cite{zhong2024memorybank} | Natural language | ✗ | ✗ | ✗ | Ebbinghaus | ✗ | ✗ |
| ACT-R \cite{anderson2004actr} | Chunks + rules | Yes (rules) | Chunking | ✗ | Activation decay | ✗ | Fixed arch. |
| **MaC (ours)** | **S-expression** | **✓** | **Structural** | **✓ (L1/L2/L3)** | **Embedded** | **OCEAN-5 (trait)** | **Constitutional** |

^† CoALA's procedural memory is executable but architecturally segregated from episodic/semantic memory.
^‡ Voyager's skills are executable but externally triggered and domain-specific (Minecraft).

MaC's key differentiation is the convergence of seven properties that no prior system combines: (1) homoiconic representation enabling memory-as-program, (2) graduated comprehension via multi-layer compilation, (3) self-correcting lifecycle embedded within each memory, (4) personality-trait-dependent retrieval and decay modulation, (5) constitutional governance constraining self-modification, (6) unified representation collapsing declarative/procedural boundaries, and (7) LLM-native interpretation preserving flexibility while leveraging symbolic structure.
