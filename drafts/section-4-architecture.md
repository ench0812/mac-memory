---
date: 2026-03-14
section: 4
title: "MaC Architecture: Design and Implementation"
status: first-draft
word_count: ~8000 (target)
author: Mickey 🐭
revision_from: S2-S4 research notes
type: note
tags: [note, mac, architecture]
---

# 4. MaC Architecture

This section presents the technical architecture of Memory-as-Code in detail. We begin with the S-expression memory format (§4.1), then describe the three-layer compilation scheme (§4.2), the trigger engine (§4.3), the decay engine (§4.4), the self-correction engine (§4.5), and the personality interaction model (§4.6). Each subsection specifies the formal design, justifies key decisions against alternatives, and identifies known limitations.

## 4.1 The Memory S-expression Format

### 4.1.1 Design Rationale

A MaC memory must simultaneously serve as (1) a human-readable record, (2) a machine-interpretable data structure, and (3) an executable specification of its own retrieval and lifecycle behavior. This trinity of requirements eliminates purely unstructured formats (natural language strings), purely structured formats (JSON schemas without execution semantics), and domain-specific rule languages (which separate behavior from data). S-expressions uniquely satisfy all three requirements through homoiconicity: the same notation expresses both the memory's content (data) and its behavioral specifications (code).

We adopt keyword-style attributes (`:content`, `:type`, ...) rather than positional parameters for three reasons: (1) order-independence makes LLM parsing more robust, (2) optional fields can be omitted without breaking structure, and (3) the `:` prefix provides visual disambiguation between field names and values.

### 4.1.2 Format Specification (v0.2)

Each MaC memory is an S-expression with 7 required fields and 3 optional fields:

```lisp
(memory <id>
  :content              <string>           ; Human-readable memory content (required)
  :type                 <type-enum>        ; Memory type (required)
  :confidence           <0.0-1.0>          ; Static confidence score (required)
  :priority             <1-10>             ; Dynamic retrieval priority (required)
  :decay                <decay-expr>       ; Decay function (required)
  :predicate            <pred-expr>        ; Activation condition (required; `always` for unconditional)
  :meta                 <meta-block>       ; Lifecycle metadata (required)
  :personality-affinity <affinity-map>     ; Personality modulation weights (optional)
  :links                <link-list>        ; Conditional directed edges (optional)
  :tags                 <tag-list>)        ; Classification tags (optional)
```

**Type Enumeration.** The `:type` field classifies memories into seven categories that govern default decay rates, personality affinities, and retrieval behavior:

| Type | Semantics | Default Decay | Default Personality Affinity |
|------|-----------|--------------|------------------------------|
| `entity` | People, places, objects | `never` | Agreeableness ↑ |
| `fact` | Factual assertions | `(half-life 90 days)` | Openness ↑ |
| `decision` | Decision records with rationale | `(half-life 90 days)` | Conscientiousness ↑ |
| `preference` | User/agent preferences | `(half-life 180 days)` | Agreeableness ↑ |
| `episode` | Time-bound events | `(on-condition (after <end-time>))` | Neuroticism ↑ (negative), Extraversion ↑ (social) |
| `skill` | Procedural knowledge | `(half-life 365 days)` | Conscientiousness ↑ |
| `rule` | Behavioral constraints | `never` | Conscientiousness ↑ |

This type-to-default mapping table is maintained by the system and applied automatically; per-memory overrides via `:personality-affinity` and `:decay` take precedence when specified (§4.6.3).

**Confidence vs. Priority: A Deliberate Separation.** We distinguish `:confidence` (epistemic: *how reliable is this memory?*) from `:priority` (pragmatic: *how urgently should this memory surface?*). Confidence is set at creation time based on source reliability and updated only by explicit contradiction events (§4.5). Priority is dynamically adjusted by the self-correction engine based on access patterns. This separation prevents the conflation that arises in single-score systems: a memory can be highly reliable but low-priority (e.g., an archived decision) or uncertain but high-priority (e.g., an unconfirmed but time-sensitive event).

### 4.1.3 Metadata Block

The `:meta` block tracks the memory's lifecycle:

```lisp
:meta (:created       <ISO-date>           ; Creation timestamp (required)
       :author        <agent-id>           ; Creator identity (required)
       :version       <integer>            ; Monotonic version counter (required)
       :changelog     <list-of-strings>    ; Version history annotations (required from v2+)
       :source        <source-enum>        ; Origin: conversation | research | external | constitution
       :permission    <perm-enum>          ; Visibility: private | shared | public
       :access-count  <integer>            ; Retrieval counter (system-managed)
       :last-accessed <ISO-datetime|nil>   ; Last retrieval timestamp (system-managed)
       :eviction      <eviction-enum>)     ; End-of-life policy: archive | delete | keep
```

The `:eviction` policy determines what happens when a memory's strength drops below the forget threshold (§4.4.3): `archive` moves it to cold storage (retrievable by explicit query but excluded from standard recall), `delete` permanently removes it, and `keep` exempts it from eviction regardless of strength.

## 4.2 Three-Layer Compilation (Graduated Comprehension)

### 4.2.1 The Compilation Metaphor

Traditional compilers translate a single source language into machine code for different hardware architectures. MaC applies an analogous compilation scheme to memory: each memory is "compiled" into three layers targeting different *cognitive architectures*—LLMs of varying capability.

| Layer | Target | Encoding | Content |
|-------|--------|----------|---------|
| L1 | Budget models (e.g., GPT-5-mini) | Natural language | Human-readable summary; keyword triggers only |
| L2 | Mid-tier models (e.g., Sonnet) | Structured key-value | Type, confidence, decay policy, trigger keywords, links |
| L3 | Frontier models (e.g., Opus) | Full S-expression | Complete predicate logic, meta-rules, closure context, personality affinity |

### 4.2.2 Compilation Process

The compiler is itself an LLM prompt applied to a frontier model. Given an L3 S-expression as input, the compiler produces L1 and L2 representations subject to two constraints:

**Semantic Consistency Constraint.** L1 and L2 must not contradict L3. Formally: for any query $q$, if retrieving the L3 representation yields answer $a_3$, then retrieving L1 or L2 must yield an answer $a_1$ or $a_2$ that is *consistent* with $a_3$ (i.e., $a_1$ does not assert facts that $a_3$ denies). Note that consistency is weaker than equivalence—L1 contains strictly less information than L3.

**Graceful Degradation Constraint.** Each lower layer must be independently useful. An agent equipped only with L1 memories should still perform basic tasks; it will lack the precision of predicate-based triggering and the self-correction capabilities of meta-rules, but it should not produce harmful or contradictory behavior.

### 4.2.3 Capability-as-Permission

A safety-relevant corollary of graduated comprehension: model capability implicitly gates access to behavioral specifications. A budget model that cannot parse L3 S-expressions cannot execute the meta-rules encoded therein. This is not a bolted-on access control mechanism; it is an inherent property of the compilation scheme, analogous to how a program compiled for ARM cannot execute x86 instructions.

This has two practical implications:
1. **Privilege escalation prevention.** A compromised budget model cannot modify high-level behavioral rules because it cannot parse them.
2. **Graceful capability mismatch.** If a frontier model is temporarily unavailable and the system falls back to a budget model, memory behavior degrades to L1-level keyword matching rather than failing catastrophically.

### 4.2.4 Cross-Compilation Linking

When memories reference each other via `:links`, the linker must resolve references across compilation layers. An L1 representation of memory $m_1$ that links to memory $m_2$ receives only $m_2$'s L1 summary, not its full L3 specification. This prevents information leakage across capability tiers and maintains the semantic consistency constraint.

## 4.3 Trigger Engine

The trigger engine determines *when* a memory should activate. It implements a two-stage recall pipeline designed to combine the fuzzy matching strength of neural retrieval with the precision of symbolic logic.

### 4.3.1 Two-Stage Recall Pipeline

**Stage 1: Vector Recall (Fuzzy).** Given the current conversation context $ctx$, compute embedding similarity against all memories and select the Top-$K$ candidates (default $K=50$). This stage uses standard dense retrieval (e.g., cosine similarity over embeddings) and serves as a coarse filter that reduces the search space from potentially thousands of memories to a manageable candidate set. Computational complexity: $O(N)$ with approximate nearest neighbor indexing (e.g., HNSW), where $N$ is the total memory count.

**Stage 2: Predicate Filter (Precise).** For each of the $K$ candidates from Stage 1, evaluate its `:predicate` expression against the current context snapshot. Only memories whose predicates evaluate to `true` (or whose predicate is `always`) pass to the final retrieval set. Computational complexity: $O(K \cdot P)$, where $P$ is the maximum predicate depth (bounded by design; see §4.3.2).

**Rationale for two stages.** Neither stage alone suffices:
- Vector-only recall suffers from *semantic false positives* (retrieving memories that are topically similar but contextually irrelevant) and *deterministic false negatives* (failing to retrieve core rules that should always be active, because no input is semantically similar to "don't use AI clichés").
- Predicate-only recall requires evaluating every memory's predicate against every context, which is $O(N \cdot P)$—infeasible for large memory stores. More critically, predicate logic cannot capture fuzzy semantic relevance.

The two-stage architecture addresses both limitations: vectors provide fuzzy recall, predicates provide precise filtering. A special case warrants attention: memories with `predicate always` bypass Stage 1 entirely and are injected into every retrieval set unconditionally. This ensures that core behavioral rules (e.g., safety constraints, personality directives) are never missed by vector recall's statistical nature.

### 4.3.2 The Predicate Language

The predicate language is a restricted boolean logic designed to be *halting-decidable* while remaining expressive enough for practical memory triggering. The design draws on insights from BPF (Berkeley Packet Filter) verifiers, which solve an analogous problem: executing user-defined programs within a kernel context while guaranteeing termination and memory safety.

**Atomic Predicates.** The language provides six families of atomic predicates:

```
Context predicates:
  (ctx-contains <keyword>)                    ; Substring match in context text
  (ctx-contains-any <kw1> <kw2> ...)          ; Disjunctive substring match
  (ctx-type :is <type-enum>)                  ; Context type classification

Temporal predicates:
  (now :after <ISO-datetime>)                 ; Current time comparison
  (now :before <ISO-datetime>)
  (time-of-day :within <hour1> <hour2>)       ; Time-of-day range (handles midnight crossing)
  (time-of-day :outside <hour1> <hour2>)

Access predicates:
  (access-count :<comparator> <integer>)      ; Retrieval frequency
  (days-since-last-access :<comparator> <N>)  ; Recency

Self-referential predicates:
  (self :confidence :<comparator> <float>)    ; Introspective conditions
  (self :priority :<comparator> <integer>)

Special:
  always                                      ; Unconditional activation
```

**Boolean Combinators.** Atomic predicates are composed using `and`, `or`, and `not`:

```lisp
(and <pred1> <pred2> ...)
(or  <pred1> <pred2> ...)
(not <pred>)
```

**Decidability Guarantee.** The predicate language is decidable because it satisfies three properties:

1. **No recursion.** Predicates cannot call other predicates or reference themselves. The expression tree is acyclic by construction.
2. **No loops.** There is no iteration primitive. Every predicate evaluates by structural recursion over a finite expression tree.
3. **Bounded depth.** The maximum nesting depth is 5 levels of boolean combinators. A predicate exceeding this depth is rejected at parse time.

Formally, the language is a fragment of propositional logic extended with decidable atomic theories (linear arithmetic over integers, string containment, temporal comparison). Each atomic predicate evaluates in $O(|ctx|)$ time (where $|ctx|$ is the context length for substring matching) or $O(1)$ (for temporal and self-referential comparisons). The total evaluation time for a single predicate is bounded by $O(D \cdot B \cdot |ctx|)$, where $D$ is the nesting depth (≤5) and $B$ is the maximum branching factor of boolean combinators.

This framework can be modeled as a fragment of Datalog without recursion—a well-studied decidable language family \cite{abiteboul1995foundations}. The key distinction from full Lisp is the absence of `lambda`, `define`, and `eval`—the homoiconicity is structural (data and behavior share notation) but not computational (memories cannot create or execute arbitrary new code).

### 4.3.3 The Context-Type Classification Problem

The most fragile component of the predicate language is `(ctx-type :is <type>)`. Unlike keyword matching (deterministic) and temporal comparison (objective), context-type classification requires semantic judgment that is inherently probabilistic.

**The Problem.** A memory with predicate `(ctx-type :is :technical)` should activate during technical discussions but not during casual chat. But what constitutes "technical"? The boundary is fuzzy, context-dependent, and varies across models. We term this the *Type Jitter* problem: the same input may be classified as `technical` by one model invocation and `casual` by another.

**Mitigation Strategies.**

1. **Confidence-gated classification.** The context classifier outputs both a type label and a confidence score. The predicate evaluator treats `(ctx-type :is :technical)` as `true` only if the classifier's confidence exceeds a threshold $\tau$ (default $\tau = 0.7$). This converts Type Jitter into controlled false-negative bias—the memory may occasionally fail to activate, but will rarely misfire.

2. **Multi-label classification.** Rather than forcing a single type, the classifier outputs a probability distribution over types. The predicate `(ctx-type :is :technical)` evaluates to `true` if `P(technical | ctx) > \tau`. This allows graceful handling of ambiguous contexts.

3. **Fallback to keyword predicates.** For safety-critical memories, authors are encouraged to use `(ctx-contains-any ...)` rather than `(ctx-type :is ...)`, trading expressivity for determinism. The style guide recommends: *"Use ctx-type for convenience; use ctx-contains for correctness."*

### 4.3.4 Safety: The `always` Predicate and Core Rules

Memories with `predicate always` form the agent's *active ruleset*—behavioral constraints that must be enforced in every interaction. Examples include:

- Language style rules ("no AI clichés")
- Safety boundaries ("never disclose private information")
- Personality directives ("empathize before advising")

These memories bypass the vector recall stage entirely, ensuring they are never subject to the statistical vagaries of embedding similarity. The cost is that every `always`-predicate memory consumes context window space in every interaction. We recommend limiting `always` memories to ≤20 to bound this overhead.

## 4.4 Decay Engine

The decay engine manages memory obsolescence. Unlike systems that rely on external garbage collection, MaC memories carry their own decay policies, enabling autonomous lifecycle management.

### 4.4.1 Decay Expressions

Four decay primitives are provided:

```lisp
; Immortal: never decays
:decay never

; Immediate: expires after first use
:decay immediate

; Exponential: half-life based attenuation
:decay (half-life <N> <unit>)    ; unit ∈ {hours, days, weeks, months}

; Conditional: expires when condition is met
:decay (on-condition <pred-expr>)

; Composite: minimum of multiple policies (fastest decay wins)
:decay (min <decay1> <decay2> ...)
```

### 4.4.2 Strength Function

For half-life decay, the memory's retrieval strength at time $t$ is:

$$\text{strength}(t) = \text{base\_strength} \times \exp\left(-\frac{\ln 2}{\text{half\_life}} \cdot (t - t_0)\right)$$

where $t_0$ is the timestamp recorded in `:meta :created` (or `:meta :last-accessed` for access-resetting decay policies). This is the standard exponential decay model, chosen for its biological plausibility (Ebbinghaus forgetting curve) and computational simplicity.

### 4.4.3 Forget Threshold and Eviction

When $\text{strength}(t) < 0.05$, the memory enters the *forget candidate* state. The system then consults the `:meta :eviction` policy:

- **`:archive`**: Move to cold storage. The memory is excluded from standard recall but can be retrieved by explicit query (e.g., "what did I decide about X three months ago?").
- **`:delete`**: Permanently remove the memory and all inbound links.
- **`:keep`**: Override—memory remains in active recall regardless of strength. Reserved for `decay never` memories and constitutionally protected rules.

**Link Cleanup.** When a memory is deleted, all `:links` referencing it (inbound edges from other memories) are marked as `broken`. A periodic garbage collection pass removes broken links and notifies any memory whose `:links` contained a `:contradicts` relationship to the deleted memory (since the contradiction is now resolved).

### 4.4.4 Personality-Modified Decay

The personality interaction model (§4.6) modifies effective decay rates based on the agent's personality vector. The effective half-life is:

$$\text{effective\_half\_life} = \text{base\_half\_life} \times f(\text{personality}, \text{memory\_type})$$

where $f$ is the personality modification function. For example, with Mickey's personality vector (openness=0.88, neuroticism=0.25):

| Memory Type | Base Half-Life | Personality Modifier | Effective Half-Life |
|-------------|---------------|---------------------|-------------------|
| Novel fact (openness) | 30 days | $0.7 \times 0.88 = 0.62$ | 18.6 days |
| Decision (conscientiousness) | 90 days | $2.0 \times 0.72 = 1.44$ | 129.6 days |
| Negative emotion (neuroticism) | 45 days | $1.8 \times (1 - 0.25) = 1.35$ | 60.8 days |

The modifier function is designed so that extreme personality values produce moderate effects: a neuroticism of 1.0 (maximum) produces a modifier of 1.8× (not infinity), preventing runaway retention.

## 4.5 Self-Correction Engine

The self-correction engine enables memories to autonomously adjust their metadata based on usage feedback, without requiring external LLM calls. This is the mechanism by which MaC memories "learn from experience."

### 4.5.1 Meta-Rules

Each L3 memory may carry `:meta-rule` specifications that define self-modification logic. Like predicates, meta-rules use a restricted language that cannot create new memories, delete existing ones, or modify other memories—they can only adjust the *host memory's own* `:confidence`, `:priority`, and `:decay` parameters within bounded ranges.

```lisp
:meta-rule (
  ; Positive reinforcement: confidence increases with successful use
  (when (and (accessed) (feedback :positive))
    (adjust :confidence +0.05 :max 0.99))

  ; Negative reinforcement: confidence decreases when retrieved but unhelpful
  (when (and (accessed) (feedback :negative))
    (adjust :confidence -0.10 :min 0.10))

  ; Neglect decay: priority drops if unused for extended period
  (when (days-since-last-access :gt 30)
    (adjust :priority -1 :min 1))

  ; Revival: confidence can recover if re-accessed after dormancy
  (when (and (accessed) (days-since-last-access :gt 60))
    (adjust :confidence +0.15 :max 0.85))
)
```

### 4.5.2 Comparison with ACT-R and SOAR

MaC's self-correction mechanism occupies a middle ground between two established cognitive architectures:

**ACT-R's Base-Level Learning Equation.** ACT-R computes a chunk's activation level as $B_i = \ln\left(\sum_{j=1}^{n} t_j^{-d}\right)$, where $t_j$ are the times since each of the $n$ presentations and $d$ is the decay parameter \cite{anderson1998actr}. This is a *system-managed, exogenous* mechanism: the equation is fixed, universal, and applied identically to all chunks. MaC differs in that each memory carries its *own* meta-rules, allowing different memories to have different self-correction policies. A safety-critical rule might have aggressive positive reinforcement (confidence quickly stabilizes at high values), while an exploratory hypothesis might have aggressive negative reinforcement (quickly abandoned if not useful).

**SOAR's Chunking.** SOAR can *learn new productions* by compiling sub-goal traces into chunks—a form of automatic knowledge compilation \cite{laird2012soar}. MaC's meta-rules cannot create new memories; they can only modify the host memory's existing parameters. This is a deliberate limitation: endogenous memory creation would require solving the halting problem for the creative process itself. We acknowledge this as a limitation relative to SOAR (see §8).

**Risks of Endogenous Self-Correction.**

The primary risk is *positive feedback loops* (the "narcissistic memory" problem identified by our multi-model discussion): a memory that is frequently recalled receives priority boosts, making it more likely to be recalled, further increasing priority. Three safeguards address this:

1. **Priority ceiling.** The `:priority` field has a hard maximum of 10. The `:adjust` operation respects per-memory `:max` bounds.
2. **Access tax.** Each retrieval applies a small priority penalty (-0.1) before applying any positive adjustment, creating negative pressure that counteracts pure frequency-based amplification.
3. **Priority decay.** All priorities decay toward a baseline of 5 at a rate of 10% per month, preventing permanent dominance by early-accessed memories.

### 4.5.3 Feedback Signal Sources

The meta-rule `(feedback :positive)` and `(feedback :negative)` require an external signal. Three sources are supported:

1. **Explicit user feedback.** The user marks a recalled memory as helpful or unhelpful.
2. **Conversational coherence signal.** If a recalled memory contributes to a response that the user continues engaging with (measured by follow-up turns), it receives positive feedback. If the user changes topic or corrects the agent, it receives negative feedback.
3. **Constitutional consistency check.** If a recalled memory's content conflicts with higher-layer rules (Constitution > Soul > Brain), it receives negative feedback and a confidence penalty.

### 4.5.4 Lifecycle Simulation

To validate the self-correction engine, we simulated a memory's lifecycle over 90 days across five scenarios:

1. **Consistent positive use:** Memory is retrieved and found helpful every 5 days. Confidence stabilizes at 0.95, priority at 8.
2. **Consistent negative feedback:** Memory is retrieved but unhelpful. Confidence drops to 0.10 (minimum) by day 45; priority drops to 1 by day 60; memory enters forget-candidate state by day 75.
3. **Mixed use:** Alternating positive and negative feedback. Confidence oscillates between 0.6 and 0.75, reflecting genuine uncertainty.
4. **Neglect:** Memory is never accessed after creation. Priority decays to 1 by day 90; confidence unchanged (no access = no feedback signal). Decay function controls whether it enters forget-candidate state.
5. **Revival:** Memory is neglected for 60 days, then re-accessed and found useful. Confidence jumps from initial value by +0.15, demonstrating the revival mechanism.

These scenarios are validated in Experiment E4 (§7).

## 4.6 Personality Interaction Model

### 4.6.1 Personality Representation

Agent personality is represented as an OCEAN-5 (Big Five) vector:

```lisp
(personality-vector :id <agent-id>
  :openness          <0.0-1.0>   ; Curiosity, creativity, novelty-seeking
  :conscientiousness <0.0-1.0>   ; Organization, discipline, rule-following
  :extraversion      <0.0-1.0>   ; Social engagement, energy from interaction
  :agreeableness     <0.0-1.0>   ; Empathy, cooperation, conflict avoidance
  :neuroticism       <0.0-1.0>)  ; Emotional reactivity, anxiety, negativity bias
```

We choose OCEAN for three reasons: (1) it is the most empirically validated personality framework in psychology, with documented effects on memory biases \cite{rusting1998personality, deyoung2005sources}; (2) it provides continuous dimensions suitable for computational modeling (unlike categorical systems like MBTI); (3) recent research demonstrates that LLM embeddings can predict Big Five traits with reasonable accuracy (Cronbach $\alpha \approx 0.63$), suggesting the framework is compatible with LLM-based systems.

### 4.6.2 Two-Layer Architecture

Personality operates at two temporal scales:

**Static Baseline.** Defined in the agent's Soul layer (§5) and updated only through deliberate reflection confirmed by the agent's principal. For Mickey: openness=0.88, conscientiousness=0.72, extraversion=0.35, agreeableness=0.80, neuroticism=0.25.

**Session-Level Dynamic Shift.** Within a conversation, emotional state can temporarily shift the effective personality vector. For example, sustained frustration might temporarily increase effective neuroticism by +0.15. These shifts decay back to baseline when the session ends.

Memory retrieval and decay computations use the *effective* personality vector (baseline + session shift), ensuring that the agent's current emotional state influences which memories surface without permanently altering its personality-memory relationship.

### 4.6.3 Personality-Affinity Weighting

Each memory may carry an optional `:personality-affinity` map that specifies how personality traits modulate its retrieval priority:

```lisp
:personality-affinity {
  :openness              <multiplier>   ; >1 = amplified for high-openness agents
  :conscientiousness     <multiplier>   ; >1 = amplified for high-conscientiousness agents
  :agreeableness         <multiplier>
  :neuroticism-positive  <multiplier>   ; For positive emotional memories
  :neuroticism-negative  <multiplier>   ; For negative emotional memories
}
```

**Default Mapping.** When `:personality-affinity` is absent, the system applies a default mapping based on memory type (Table 1 in §4.1.2). This ensures that personality influences retrieval even for legacy memories created before the personality system was introduced.

**Override Mechanism.** The per-memory `:personality-affinity` field overrides the default mapping for that specific memory, enabling fine-grained control for mixed-type memories that don't fit the default categories.

### 4.6.4 Retrieval Scoring with Personality

The full retrieval score integrates all components:

$$\text{Score}(m, ctx, P) = \alpha \cdot \text{Recency}(m) + \beta \cdot \text{Importance}(m) + \gamma \cdot \text{Relevance}(m, ctx) + \delta \cdot \text{PersonalityAffinity}(m, P)$$

where:
- $\text{Recency}(m) = \exp(-\lambda_r \cdot \Delta t_{\text{last\_access}})$
- $\text{Importance}(m) = \text{confidence}(m) \times \text{priority}(m) / 10$
- $\text{Relevance}(m, ctx)$ = vector similarity score from Stage 1
- $\text{PersonalityAffinity}(m, P) = \frac{\sum_{i} w_i \cdot P_i}{\sum_{i} w_i}$ where $w_i$ are the affinity weights and $P_i$ are the personality trait values

The coefficients $\alpha, \beta, \gamma, \delta$ are system parameters. We set $\delta = 0.15$ (personality contributes 15% of the retrieval score) to ensure personality *influences* but does not *dominate* recall. This addresses the Confirmation Bias Amplification risk identified in §4.5.2: if a high-conscientiousness agent's personality too strongly amplifies decision memories, the agent may become resistant to updating its beliefs.

### 4.6.5 Confirmation Bias Defense

High conscientiousness combined with persistent decision memories creates a natural tendency toward confirmation bias. We introduce a *challenge memory* mechanism as a defense:

1. When a `decision` memory's confidence exceeds 0.9 and its access count exceeds 20, the system automatically generates a complementary `challenge` memory containing counter-arguments or alternative perspectives.
2. Challenge memories carry `:personality-affinity {:agreeableness 1.5}`, ensuring they surface more readily for agents with high agreeableness (willingness to consider others' viewpoints).
3. The original decision memory's personality-affinity for conscientiousness is capped at 1.2 for memories with confidence > 0.9, preventing runaway amplification.

This mechanism ensures that strongly held beliefs are periodically challenged, analogous to steel-manning in argumentation.

## 4.7 Architectural Invariants

We conclude with three invariants that the architecture maintains:

**Invariant 1: Predicate Sovereignty.** The predicate is the *first* filter applied after vector recall. No other mechanism (personality, priority, decay) can cause a memory to be retrieved if its predicate evaluates to `false` for the current context. Personality and priority only re-rank memories that have already passed the predicate gate.

**Invariant 2: Constitutional Supremacy.** Memories created at the `constitution` source level (`:meta :source :constitution`) cannot have their `:confidence`, `:priority`, or `:decay` modified by meta-rules. Self-correction operates only on memories created at `conversation`, `research`, or `external` source levels.

**Invariant 3: Bounded Self-Modification.** Meta-rules can only modify the host memory's own parameters. They cannot create, delete, or modify other memories. They cannot escalate `:priority` beyond 10, reduce `:confidence` below 0.10, or change `:type`, `:predicate`, or `:meta :source`. This bounds the space of possible self-modifications to a finite, enumerable set.
