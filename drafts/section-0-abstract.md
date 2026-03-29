---
date: 2026-03-29
section: abstract
title: Abstract
status: first-draft
word_count: ~250
author: Mickey 🐭
type: note
tags: [note, mac, abstract]
---

# Abstract

Current LLM agents typically treat memory as passive data: retrieved text, vector hits, or external notes that inform generation but do not themselves carry executable semantics. This separation limits an agent's ability to encode when a memory should activate, how it should decay, and how past experience should modify future behavior. We present **Memory-as-Code (MaC)**, an executable memory architecture in which each memory is represented as a homoiconic S-expression carrying content, activation predicates, decay rules, confidence metadata, and bounded self-correction logic. MaC compiles each memory into three layers (L1/L2/L3) to support graduated access across model tiers, and embeds these memories inside a four-layer governance hierarchy (Constitution → Soul → Brain → Storage) designed to constrain self-modification.

We evaluate MaC through a single-agent feasibility study in a continuously deployed AI assistant over 47 days, combining controlled experiments with field observations. The S-expression encoder achieved 29/29 structurally valid compilations. Trigger evaluation reached F1 = 1.0 on a hand-crafted test set, and the self-correction engine passed 5/5 simulated lifecycle scenarios. In a 135-call cross-model comprehension study, all tested models were able to interpret L1-L3 memory representations, contradicting a strong capability-gating hypothesis: the practical difference was not whether weaker models could parse the structure, but how deeply they could critique or operationalize it. In a behavioral A/B study (75 responses), minimal executable rules improved boundary respect and harm avoidance relative to a no-rule baseline.

These results suggest that the main value of executable memory is not access restriction but **information-rich behavioral guidance**: memories can function as compact, governable control objects that shape retrieval, action, and self-revision. We frame MaC as an initial N-of-1 systems result, not a general proof, and identify human evaluation, adversarial testing, and broader multi-agent validation as the next steps.
