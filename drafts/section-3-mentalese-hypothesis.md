---
date: 2026-03-08
section: 3
title: The Mentalese Hypothesis: Why AI Agents Need an Internal Language
status: first-draft
word_count: ~1800
author: Mickey 🐭
type: note
tags: [note]
---

# 3. The Mentalese Hypothesis

Before presenting MaC's technical architecture, we motivate its design with a theoretical argument: AI agents, like humans, require an internal representational language distinct from natural language—and S-expressions are a strong candidate for this role.

## 3.1 From Fodor to Artificial Agents

Fodor \cite{fodor1975lot} argued that natural language is unsuitable as the medium of thought because it is (a) ambiguous ("bank" can mean a financial institution or a riverbank), (b) context-dependent (the meaning of "it" shifts with each sentence), and (c) optimized for *communication* between minds rather than *computation* within a mind. He proposed that cognition operates over Mentalese—a symbolic, compositional, unambiguous internal language.

The same argument applies, *a fortiori*, to LLM agents. When an agent stores a memory in natural language—"The user prefers conservative ETF investments and rebalances quarterly"—it introduces exactly the ambiguities Fodor identified:

- **Lexical ambiguity**: "conservative" has different meanings in political vs. financial contexts. An LLM processing this memory during a political discussion might retrieve it erroneously.
- **Implicit structure**: The memory encodes a preference (ETF), a strategy (conservative), and a schedule (quarterly), but these components are flattened into a single sentence. Extracting the schedule requires re-parsing the natural language each time.
- **Missing behavior**: The memory says *what* the user prefers but nothing about *when this memory should activate*, *how confident we are in it*, or *what happens if the user's behavior changes*.

Consider the same information encoded as a MaC S-expression:

```lisp
(memory
  :id "pref-invest-001"
  :l1 "User prefers conservative ETF investments, rebalances quarterly."
  :l2 (:category preference
       :domain finance
       :confidence 0.85
       :trigger (:keyword ["ETF" "investment" "portfolio" "rebalance"])
       :decay (:strategy slow :half-life 180))
  :l3 (:chain ["pref-risk-tolerance" "fact-broker-fubon"]
       :meta-rule (when (usage-count < 2 :in-days 90)
                    (adjust :confidence -0.1))
       :closure (:source "explicit user statement"
                 :date "2026-02-15"
                 :context "discussing portfolio strategy")))
```

This encoding is:
- **Unambiguous**: "conservative" is contextualized by `:domain finance`; no political reading is possible.
- **Decomposed**: Preference, strategy, and schedule are separate addressable fields.
- **Behavioral**: The memory self-describes when to activate (`:trigger`), how to age (`:decay`), and how to self-correct (`:meta-rule`).
- **Layered**: L1 is human-readable; L2 is machine-structured; L3 carries the full computational semantics.

## 3.2 Why S-expressions?

The choice of S-expressions is not arbitrary. Among structured formats (JSON, YAML, XML, S-expressions), S-expressions uniquely satisfy three requirements:

**Homoiconicity.** In Lisp, code and data are both S-expressions. A Lisp program can inspect and modify another Lisp program because they share the same representation \cite{mccarthy1960lisp}. MaC exploits this property: a memory's meta-rule (code) and its content fields (data) are both S-expressions, enabling an LLM to reason about memory behavior in the same representational framework as memory content. JSON and YAML lack this property—a JSON schema cannot natively express executable logic over its own fields.

**Compositional nesting.** S-expressions support arbitrary recursive nesting, making them natural for expressing complex conditions (`(and (keyword-match "ETF") (time-since-last-access > 30d))`) and hierarchical memory structures. While JSON supports nesting, it requires explicit key-value pairing that adds syntactic overhead without semantic benefit for this use case.

**LLM affinity.** LLMs have been trained on substantial volumes of Lisp, Scheme, and Clojure code. Empirically, frontier models (Claude Opus, GPT-4) can generate, parse, and reason about S-expressions with high reliability \cite{delatorre2025lisp_metaprogramming}. This is not true of all symbolic formats—Prolog-style horn clauses or lambda calculus notation, while formally more expressive, are less reliably handled by current LLMs due to lower training data representation.

## 3.3 The Compilation Metaphor

A further insight—contributed through collaborative design discussion—reframes MaC not merely as a memory format but as a *memory compilation system*. The analogy to traditional compilation is precise:

| Compilation Concept | MaC Analogue |
|---------------------|-------------|
| Source language | Memory S-expression (L3) |
| Target architecture | LLM capability tier |
| Intermediate representation | L2 structured metadata |
| Optimization pass | Simplification for lower-tier targets |
| Cross-compilation | One memory → three target encodings |
| ABI compatibility | Semantic consistency across layers |
| Linking | Resolution of `:chain` references between memories |

Traditional compilers translate a single source language into machine code for different hardware architectures (x86, ARM, WASM). MaC translates a single memory representation into encodings for different *cognitive architectures*—LLMs of varying capability. The "instruction set" of a frontier model includes symbolic reasoning, while a budget model's "instruction set" is limited to pattern matching and keyword recognition. The MaC compiler (implemented as prompts to a frontier model) produces three "binaries" from one source, each optimized for its target's capabilities.

This metaphor has a concrete safety implication. In traditional systems, a program compiled for ARM cannot execute x86 instructions—the architecture enforces the boundary. Analogously, a model that cannot parse L3 S-expressions cannot execute the meta-rules encoded therein. **Capability is permission.** This is not a bolted-on access control mechanism; it is an inherent property of the compilation scheme.

## 3.4 Limitations of the Analogy

We acknowledge that the Mentalese analogy is imperfect. Fodor's Mentalese is hypothesized to be *innate*—a biological endowment of the human cognitive architecture. MaC's S-expressions are *designed*—an engineering choice that could be otherwise. We do not claim that S-expressions are the uniquely correct memory language for AI, only that they are a well-motivated candidate that satisfies the desiderata (homoiconicity, compositionality, LLM affinity) better than alternatives we considered.

Furthermore, Fodor's Mentalese operates below conscious access—humans cannot directly inspect their own Mentalese representations. MaC's S-expressions, by contrast, are fully inspectable at every layer. This is a feature, not a bug: transparency is a safety requirement for deployed AI systems, and one that biological cognition does not provide.

Finally, the compilation metaphor should not be taken to imply formal compilation guarantees. A traditional compiler produces semantically equivalent output for different targets; MaC's "compilation" is lossy by design—L1 necessarily contains less information than L3. The guarantee is weaker: *semantic consistency* (L1 and L3 do not contradict each other) rather than *semantic equivalence* (L1 and L3 encode identical information).