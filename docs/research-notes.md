# MaC Research Notes

## Timeline

### 2026-03-08: Concept Birth
- Insight: Most AI personalization is "style transfer" — changing output format, not reasoning
- Three-layer empathy model proposed:
  1. Emotional memory (stored preferences)
  2. Emotional model (executable reasoning rules)
  3. Anticipation (simulate recipient reaction before sending)
- Key distinction: empathy at the reasoning layer, not the output layer

### 2026-03-09: First Experiments

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

### Key Insights

1. **Temperature + Boundaries = Character**
   Natural language describes *who you are*; S-expression defines *what you don't cross*

2. **Positive instructions > Negative instructions**
   `(use empathy)` works better than `(suppress advice)`
   Tell the model what TO do, not just what NOT to do

3. **MaC = Memory as Character**
   Personality traits should pervade ALL behavior, not just conversation
   The same traits that make chat empathetic should make articles authentic

4. **Rules should evolve**
   Static rules are templates; living rules learn from interaction feedback
   Goal: interaction → trigger rule → respond → feedback → update rule

## Open Questions

- How do MaC rules perform across different model families?
- Can rules be automatically generated from interaction history?
- What's the optimal ratio of temperature (NL) to boundaries (SE)?
- How do boundaries interact with Constitutional AI safety constraints?
