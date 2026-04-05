---
date: 2026-04-05
section: abstract
title: Abstract
status: revised
word_count: ~270
author: Mickey 🐭
type: note
tags: [note, mac, abstract]
---

# Abstract

Current LLM agents usually treat memory as passive retrieval: text snippets, vector hits, or external notes that inform generation but do not themselves carry executable semantics. That separation makes it hard for an agent to specify when a memory should activate, how it should decay, and how experience should revise future behavior. We present **Memory-as-Code (MaC)**, an executable memory architecture in which each memory is represented as a homoiconic S-expression carrying content, activation predicates, decay rules, confidence metadata, and bounded self-correction logic. MaC compiles every memory into three access layers (L1/L2/L3) for graduated model access, and places those memories inside a four-layer governance hierarchy (Constitution → Soul → Brain → Storage) that constrains self-modification.

We evaluate MaC in a single-agent feasibility study on a continuously deployed AI assistant over 47 days, combining controlled experiments with production observations. The S-expression encoder compiled 29/29 real memories into valid structures. Trigger evaluation reached F1 = 1.0 on a hand-crafted test set, and the self-correction engine passed 5/5 simulated lifecycle scenarios. In a 135-call cross-model comprehension study, all tested models could interpret the layered representation; the meaningful difference was not parseability, but how deeply each model could critique or operationalize the structure. In a 75-response behavioral A/B study, minimal executable rules improved boundary respect and harm avoidance over a no-rule baseline, while more detailed rules sometimes produced the strongest individual responses but less stable behavior.

These results suggest that the main value of executable memory is not access restriction alone, but information-rich behavioral guidance: memories can act as compact, governable control objects that shape retrieval, action, and self-revision. We frame MaC as an N-of-1 feasibility study, not a general proof, and identify human evaluation, adversarial testing, and broader multi-agent validation as the next steps.
