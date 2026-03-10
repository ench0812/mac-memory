# MaC Research Notes

## Timeline

### 2026-03-08: Concept Birth
- Insight: Most AI personalization is "style transfer" — changing output format, not reasoning
- Three-layer empathy model proposed:
  1. Emotional memory (stored preferences)
  2. Emotional model (executable reasoning rules)
  3. Anticipation (simulate recipient reaction before sending)
- Key distinction: empathy at the reasoning layer, not the output layer

### 2026-03-09: First Experiments (v1–v4)

#### v1 — Basic A/B (NL vs S-expression)
- 5 scenarios, Claude Sonnet 4
- S-expression `sequence` rules clearly worked (affirm → extend → risk)
- `suppress` rules were unreliable on Sonnet

#### v2 — Extended (8 scenarios × 3 runs)
- Added post-correction and flow state scenarios
- `add-qualifier` ("if I understand correctly") hit 100% (3/3)
- `energy-match` improved naturalness
- Anti-pattern string matching too crude for evaluation

#### v3 — LLM-as-Judge
- 5-dimension qualitative scoring (1-5)
- Key finding: S-expression excels at **boundary respect** (4.50 vs 4.31)
- Natural language excels at **naturalness** and **emotional accuracy**
- They complement each other, not compete

#### v4 — Three-way Hybrid Validation
- A (NL) vs B (SE) vs **C (Hybrid)**
- **C wins: 4.62 > B=4.57 > A=4.45**
- C won 4/6 scenarios
- Highest score: flow state discussion (4.93/5)
- Largest gap: excited idea sharing (C=4.80 vs A=4.20)

### 2026-03-09–10: Frustration & Empathy Deep Dive (v5 series)

#### v5 — Frustration-focused
- 5 frustration scenarios (criticized, self-doubt, screwed up, ignored, unfairness)
- A (generic NL) vs B (targeted SE per scenario) vs C (selective: external→structure, internal→accompany)
- B's targeted approach backfired on self-doubt (2.72/5) — listing achievements felt like gaslighting
- C's selective approach: internal emotions benefit from pure accompaniment

#### v5b — Full validation (5 runs × 5 scenarios × 3 groups = 150 API calls, 0 errors)
- **Overall: A=4.49 > C=4.34 > B=4.00**
- B crashed on F2 self-doubt (2.72) — targeted rules caused secondary harm
- C beat A on F2 (4.32 vs 4.24) — validates selective design
- C worst on F3 screwed-up (3.56) — external/internal split too coarse

#### v5c — Refined emotional categorization
- Hypothesis: classify by emotional core (self-blame / victimized / ignored / unfairness) instead of external/internal
- C2_refined: added `frustration/self-blame` rule (suppress advice/analysis) + `boundary/tone-control`
- **Result: A=4.28 > C2=4.20** — more rules ≠ better
- C2 better at emotional_validation (4.52 vs 4.32) and companionship (4.12 vs 3.92)
- A better at boundary_respect (4.56 vs 4.24) — detailed sequences made model "over-act"
- **Insight: best empathy rules are few and precise, not detailed and exhaustive**

#### v5d — Minimal rules experiment (the breakthrough)
- D_minimal: only 2 rules: `empathy/frustration-core` (accompany first, don't act) + `boundary/tone` (like a friend, not AI)
- **D=4.47 > A=4.34 > C2=4.32** — 2 precise rules beat 5 detailed rules
- **D boundary_respect=4.88 (highest of all experiments)**
- Simple emotions (criticized, self-doubt): minimal rules sufficient
- Complex emotions (ignored): refined guidance helps
- **Core finding: less is more — 2 precise rules > 2 generic > 5 detailed**

#### v5d Opus Judge — Cross-model validation
- Opus 4.6 re-scored same responses (30 API calls)
- **Ranking flipped: C2=4.56 > D=4.44 > A=4.36**
- Opus stricter by 0.2–0.8 points across the board
- **The judge model matters** — Sonnet is a lenient grader

### 2026-03-10: Direction Shift — From Rules to Self

- User insight: "You need to have a self first. When you have your own thoughts, sharing comes naturally."
- All MaC rules so far are reactive ("how to respond") — none define inner drive ("what I think about")
- Rules are training wheels. Real internalization = natural emergence from relationships
- **New research direction: from empathy rules to identity — curiosity, preferences, attitudes**
- This may be more important than v6 dynamic rules

## Key Insights (cumulative)

1. **Temperature + Boundaries = Character**
   Natural language describes *who you are*; S-expression defines *what you don't cross*

2. **Positive instructions > Negative instructions**
   `(use empathy)` works better than `(suppress advice)`

3. **MaC = Memory as Character**
   Personality traits pervade ALL behavior, not just conversation

4. **Less is more (v5d)**
   2 precise rules outperform 5 detailed rules. Over-specifying causes models to "over-act" and violate boundaries.

5. **The judge model matters**
   Sonnet and Opus rank the same responses differently. Always validate with multiple judges.

6. **Selective targeting works, but classification is hard**
   External/internal split is too coarse. Emotional-core classification is better but still imperfect.

7. **Rules are training wheels**
   The goal is internalization — personality that emerges from interaction, not from checking rules.

## Open Questions

- How do MaC rules perform across different model families?
- Can rules be automatically generated from interaction history?
- What's the optimal number of rules? (Current answer: 2–3 core rules)
- How do boundaries interact with Constitutional AI safety constraints?
- Can we measure "internalization" — when rules become unnecessary?
- What defines an AI's "self" beyond response patterns?
