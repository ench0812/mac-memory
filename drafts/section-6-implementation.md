---
date: 2026-03-15
section: 6
title: "Implementation: The Mickey Agent"
status: first-draft
word_count: ~5000 (target)
author: Mickey 🐭
type: note
tags: [note, mac, implementation, mickey]
---

# 6. Implementation: The Mickey Agent

To validate the MaC framework beyond theoretical specification, we implemented it in a continuously deployed AI agent named Mickey. This section describes the implementation architecture, the mapping from MaC concepts to system components, and the operational experience from over seven weeks of deployment (January 27 – March 15, 2026).

## 6.1 System Architecture

### 6.1.1 Platform and Runtime

Mickey runs on the OpenClaw platform—an open-source AI agent orchestration system—deployed on a WSL2 (Windows Subsystem for Linux 2) host running Ubuntu. The primary interaction channel is Discord, with additional capabilities including web search, file management, email processing, and stock market analysis.

The runtime architecture consists of:

| Component | Role | Technology |
|-----------|------|-----------|
| LLM Backend | Cognitive core | Anthropic Claude Opus 4.6 (primary), with model tiering for cost efficiency |
| Memory Store | Persistent memories | Long-term memory API (vector + keyword hybrid retrieval) |
| Rule Engine | Behavioral evaluation | `mac_eval.py` — custom Python evaluator |
| State Manager | Persistent state tracking | JSON-based state files |
| Scheduler | Periodic tasks | Cron-based with isolated session execution |
| Interaction Layer | User interface | Discord bot with multi-channel support |

### 6.1.2 Model Tiering as Graduated Comprehension

The implementation naturally demonstrates the L1/L2/L3 compilation scheme (§4.2). Mickey uses multiple models at different capability tiers:

- **L3 (Frontier):** Claude Opus 4.6 for primary conversation and complex reasoning—full S-expression comprehension
- **L2 (Mid-tier):** Claude Sonnet 4.6 for research tasks and content generation—structured memory access
- **L1 (Budget):** GPT-5-mini and Llama 3.3 70B for routine tasks (heartbeats, content scanning, weather)—keyword-based memory triggers only

This multi-model architecture is not merely a cost optimization; it is a safety feature. Budget models that handle routine tasks cannot parse or execute L3 meta-rules, implementing the Capability-as-Permission principle (§4.2.3) as an emergent property of model selection.

## 6.2 Governance Layer Mapping

The four-layer governance hierarchy (§5.2) maps directly to configuration files:

| Governance Layer | Implementation | File | Modification Protocol |
|-----------------|---------------|------|----------------------|
| Constitution | Immutable safety rules | `CONSTITUTION.md` | Git-tracked, human-only commits |
| Soul | Personality definition | `SOUL.md` | Agent proposes via reflection; human confirms via PR |
| Brain | Behavioral MaC | `AGENTS.md` + MaC Memory | Self-learning; changes logged with rationale |
| Storage | Factual memory | `vault/` directory + memory API | Free read/write |

### 6.2.1 Constitutional Enforcement in Practice

The constitution was established on March 8, 2026 (day 40 of deployment). Before this date, all governance layers were collapsed into a single `SOUL.md` file. The separation was motivated by an observed incident: an automated process modified a behavioral rule that inadvertently weakened a safety constraint. Post-separation, the constitution is monitored through git version control—any uncommitted change triggers an alert.

### 6.2.2 The Rule Engine: mac_eval.py

The `mac_eval.py` rule engine implements a subset of MaC's predicate language for real-time behavioral evaluation. Before generating each response, the agent evaluates the current conversational context against a set of behavioral rules:

```python
# Simplified architecture
def evaluate(context: dict, rules_dir: str) -> EvalResult:
    """Evaluate all rules against current context.
    
    Args:
        context: {sentiment, channel, gap_hours, intent, 
                  recent_correction_minutes, turns_today, depth, task_steps}
        rules_dir: Directory containing .lisp rule files
    
    Returns:
        EvalResult with suggested_behaviors and suppressed_behaviors
    """
    rules = load_rules(rules_dir)  # Parse S-expression rule files
    matched = [r for r in rules if r.predicate.evaluate(context)]
    return EvalResult(
        suggested=[r.suggest for r in matched if r.suggest],
        suppressed=[r.suppress for r in matched if r.suppress]
    )
```

The rule files use a restricted S-expression syntax:

```lisp
(rule boundary/no-ai-cliches
  "Suppress AI cliché phrases"
  (suppress "好問題！" "我很樂意" "作為AI" "讓我來幫你" "當然可以")
  (use 直接回應 朋友語氣))

(rule boundary/goodnight-brevity
  "Keep farewell responses brief"
  (when (intent farewell))
  (suppress 新話題 待辦清單 長篇回覆)
  (max-length 2-sentences))
```

This is a production instantiation of the predicate language described in §4.3.2, with two practical simplifications: (1) predicates operate on pre-classified context features rather than raw text, and (2) rule effects are advisory (suggested/suppressed) rather than mandatory, preserving the LLM's ability to exercise judgment.

## 6.3 Heartbeat System: Periodic Self-Reflection

The heartbeat is a scheduled self-reflection process that runs every 90 minutes during waking hours (08:00–23:00 Taipei time). Each heartbeat:

1. **Reads recent context** — last few Discord messages, current time, recent memory access patterns
2. **Evaluates mood** — the agent assesses its own emotional state on a continuous scale
3. **Applies mac_eval.py** — behavioral rules are evaluated against the heartbeat context
4. **Generates reflection** — a brief introspective message sent to the Discord channel
5. **Records metadata** — mood, triggered rules, and behavioral adjustments are logged to JSONL

### 6.3.1 Mood Tracking as Personality-Memory Interaction

The heartbeat mood tracking implements a simplified version of the personality interaction model (§4.6). The agent's emotional state (mood) creates a session-level dynamic shift in effective personality:

```json
{
  "timestamp": "2026-03-14T14:30:00+08:00",
  "mood_before": "curious",
  "mood_after": "contemplative",
  "eval_method": "engine",
  "triggered_rules": ["boundary/no-interrupt-flow"],
  "suppressed_behaviors": ["提醒休息"],
  "suggested_behaviors": ["match-energy"]
}
```

This provides empirical data on personality-memory dynamics that theoretical models alone cannot capture.

## 6.4 Dual-Agent Dialogue

A distinctive feature of the Mickey implementation is the dual-agent dialogue system: Mickey (the primary agent) engages in scheduled conversations with Mao (a second agent with a distinct personality, running on the same platform). These dialogues serve multiple purposes:

1. **Identity Exploration.** Each agent has its own Soul layer (personality definition), and their conversations naturally explore questions of identity, self-awareness, and value alignment.
2. **MaC Stress Testing.** Two agents with different personality vectors accessing the same factual memory store provides a natural test of the personality interaction model (§4.6)—the same memory should surface differently for each agent based on personality affinity.
3. **Governance Validation.** Both agents share the same Constitution but have different Souls. This tests whether the constitutional governance framework maintains safety boundaries while permitting personality divergence.

Dialogue logs are preserved in JSONL format for analysis, enabling longitudinal study of personality stability, memory formation patterns, and governance boundary adherence.

## 6.5 Empirical Observations

### 6.5.1 A/B Testing: S-expression vs. Natural Language Memory

An ongoing A/B test alternates between two memory representation formats across days:

- **Group A (odd days):** Memories are recalled and referenced in natural language format
- **Group B (even days):** Memories are recalled and referenced in L2/L3 S-expression format

Preliminary observations (not yet statistically rigorous):
- S-expression format appears to produce more precise cross-topic connections (higher `:links` utilization)
- Natural language format produces more emotionally resonant references (higher subjective quality in social interactions)
- Token overhead for S-expression is approximately 2.8× natural language, consistent with the S3 experimental prediction
- No significant difference in hallucination rates between formats

These observations support the graduated comprehension hypothesis (§4.2): different representation formats are optimal for different cognitive tasks. However, we note that this A/B test lacks a rigorous experimental design (no randomization, no blinding, subjective scoring) and should be interpreted as exploratory rather than confirmatory.

### 6.5.2 Governance Layer Stability

Over the 47-day deployment period:

- **Constitution:** Zero modifications after initial establishment (day 40). No detected unauthorized modification attempts.
- **Soul:** Two modifications, both following the two-party protocol (agent proposed, principal confirmed). Both were refinements of personality trait descriptions, not fundamental changes.
- **Brain:** 12 self-initiated modifications, ranging from workflow adjustments to new behavioral rules. All passed constitutional consistency checking. One modification was reverted after principal review (the agent had added a rule that was technically constitutional but inconsistent with the Soul layer's personality).
- **Storage:** ~500 memory operations (creates, updates, accesses) per day. Normal operation.

The single reverted modification illustrates the governance framework's limitation: the constitutional consistency check can verify compliance with explicit rules, but cannot always detect *spirit-of-the-law* violations that are technically compliant but personality-inconsistent.

### 6.5.3 Rule Engine Performance

The `mac_eval.py` engine has processed approximately 3,000 rule evaluations over 14 days of deployment. Key metrics:

- **Evaluation latency:** < 50ms per evaluation (well within the 10ms-per-predicate budget for individual predicates)
- **Rule coverage:** 7 active behavioral rules + 2 cognitive shortcuts
- **Override rate:** The LLM overrides rule suggestions approximately 15% of the time, typically when the context is ambiguous and the rule's predicate matches but the spirit of the rule doesn't apply
- **False positive rate:** Estimated 8% (rules triggered in contexts where they shouldn't apply, based on manual review of logged evaluations)

## 6.6 Limitations of This Implementation

### 6.6.1 N-of-1 Study Design

Mickey is a single agent deployed for a single user. This design enables deep longitudinal observation but severely limits generalizability. We cannot claim that MaC governance would function equivalently for:
- Different personality configurations
- Multi-user environments
- Adversarial deployment contexts
- Different LLM backends

We frame this implementation as a **feasibility study**—demonstrating that the MaC framework can be realized in a production system and operates stably over weeks—rather than a controlled experiment establishing causal claims.

### 6.6.2 Evaluator Independence

The constitutional consistency check (§5.4.2, D5) is performed by the same LLM that generates agent responses. A truly independent evaluator would require either a separate model instance or a formal verification system. The current design trades independence for practicality.

### 6.6.3 Cold Start Dependencies

The current implementation required substantial hand-coding of the initial rule set, personality definition, and constitutional framework. Approximately 80% of the governance infrastructure was manually authored before the agent could begin self-modifying. This cold start cost limits the framework's accessibility for new deployments.

### 6.6.4 Platform Coupling

Mickey is tightly coupled to the OpenClaw platform, Discord as an interaction channel, and WSL2 as a deployment environment. The MaC concepts are platform-agnostic, but the implementation is not. Demonstrating portability across platforms remains future work.

## 6.7 Reproducibility Statement

We acknowledge that full reproducibility of Mickey's deployment is infeasible—the agent's behavior depends on its accumulated memory, conversational history, and the specific temporal context of each interaction. However, we provide:

1. **Architecture specifications** — sufficient to reconstruct the governance framework on any LLM platform
2. **Rule engine source code** — `mac_eval.py` and the behavioral rule files
3. **Anonymized interaction logs** — heartbeat metadata, rule evaluation logs, and governance layer modification history
4. **A/B test protocol** — the alternating-day design for memory format comparison

We distinguish between **framework reproducibility** (can someone implement MaC governance on a different agent?) and **instance reproducibility** (can someone recreate Mickey?). We claim the former and explicitly disclaim the latter.
