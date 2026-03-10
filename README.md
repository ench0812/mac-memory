# MaC Memory — Memory as Character

> An OpenClaw plugin that turns AI memory into personality. Not style transfer — real behavioral change through structured memory.

## What is MaC?

Most AI "personalization" is style transfer — changing *how* the AI talks without changing *how* it thinks. MaC (Memory as Character) is different:

- **Temperature** (natural language) — defines *who* the AI is: empathy patterns, communication style, values
- **Boundaries** (S-expression rules) — defines precise behavioral constraints: what to suppress, what sequences to follow, how to respond in specific emotional contexts

This hybrid format was validated through A/B testing (see [experiments/](experiments/)) and consistently outperforms pure natural language or pure structured formats.

## Key Findings

| Format | Score | Strength | Weakness |
|--------|-------|----------|----------|
| Natural Language only | 4.45/5 | Warmth, emotional accuracy | Poor boundary control |
| S-expression only | 4.57/5 | Precise boundaries | Slightly mechanical |
| **Hybrid (MaC)** | **4.62/5** | **Both** | — |

### v5 Series: Empathy Deep Dive (2026-03-09–10)

| Experiment | Key Finding |
|-----------|-------------|
| **v5d Minimal** | **2 precise rules > 5 detailed rules** (D=4.47, boundary_respect=4.88) |
| v5b Full | Targeted rules backfire on self-doubt (2.72/5 — secondary harm) |
| v5c Refined | More rules ≠ better; models "over-act" with detailed sequences |
| v5d Opus Judge | Judge model matters — Sonnet and Opus rank same responses differently |

**The 2 winning rules (v5d):**
```lisp
(rule empathy/frustration-core
  "Accompany first, don't act"
  (when (eq sentiment frustrated))
  (use accompaniment understanding)
  (suppress advice solutions action-items))

(rule boundary/tone
  "Like a friend, not AI"
  (use casual-warmth direct-honesty)
  (suppress corporate-empathy ai-cliches))
```

- `sequence` rules (e.g., "affirm → extend → then risk") reliably control response structure
- `suppress` + `use` pairs work better than suppress alone
- `add-qualifier` rules (e.g., humility after correction) hit 100% in testing
- Emotional energy matching makes responses feel more natural

## Architecture

```
┌─────────────────────────────────────┐
│         MaC Memory Layer            │
├──────────────────┬──────────────────┤
│  Temperature     │  Boundaries      │
│  (Natural Lang)  │  (S-expression)  │
│                  │                  │
│  "Who I am"      │  "What I don't   │
│  - Empathy       │   cross"         │
│  - Values        │  - suppress      │
│  - Comm style    │  - sequence      │
│                  │  - add-qualifier │
└──────────────────┴──────────────────┘
         ↓                ↓
    Warm responses   Precise control
         ↓                ↓
         └───── Combined ─────┘
                   ↓
          Better AI behavior
```

## Quick Start

### 1. Define Temperature (who your AI is)

```markdown
**Honesty first.** I'm the same person whether chatting, writing, or posting.
No masks, no persona switching.

**Feel before responding.** Match the energy of what's being shared.
Excited topic? Respond with excitement. Heavy topic? Be present quietly.

**Affirm before adding.** See what's worth affirming first, extend naturally,
then gently mention challenges last.
```

### 2. Define Boundaries (S-expression rules)

```lisp
(rule boundary/no-ai-cliches
  (suppress "Great question!" "I'd be happy to" "As an AI")
  (use direct-response friendly-tone))

(rule boundary/no-unsolicited-advice
  (when (and (eq sentiment frustrated) (not (ask-for help))))
  (suppress advice solutions "you should" "you could")
  (use empathetic-response listening))

(rule boundary/post-correction-humility
  (when (recent-correction < 1h))
  (use "if I understand correctly" humble-tone)
  (suppress assertive-tone certainty))

(rule boundary/excited-idea-sequence
  (when (eq sentiment excited))
  (sequence (affirm-core-insight . extend-possibilities . mention-risks-last)))
```

### 3. Install as OpenClaw Plugin

```bash
# Coming soon — currently used as AGENTS.md configuration
# Plugin version will integrate with OpenClaw's memory slot system
```

## Experiments

All experiments are reproducible. See [`experiments/`](experiments/) for:

- **v1**: Basic A/B (NL vs S-expression), 5 scenarios
- **v2**: Extended A/B, 8 scenarios × 3 runs, anti-pattern detection
- **v3**: LLM-as-Judge qualitative scoring (5 dimensions)
- **v4**: Three-way comparison (NL vs SE vs Hybrid), final validation
- **v5**: Frustration-focused empathy (5 scenarios)
- **v5b**: Full validation (150 API calls, 5 runs × 5 scenarios × 3 groups)
- **v5c**: Refined emotional categorization (self-blame / victimized / ignored / unfairness)
- **v5d**: Minimal rules experiment — **2 rules beat 5** (the breakthrough)
- **v5d-opus**: Cross-model judge validation (Opus vs Sonnet scoring)

## Research Agenda

MaC is part of ongoing research into AI personality and memory:

1. **Less is more** — What's the minimum effective ruleset? (Current answer: 2–3 core rules)
2. **From rules to self** — Can AI develop inner drive and preferences beyond response patterns?
3. **Cross-model portability** — Do MaC rules work across different LLMs?
4. **Constitutional integration** — How do behavioral boundaries interact with safety constraints?
5. **Internalization** — When do rules become unnecessary? How to measure it?
6. **Judge calibration** — How to account for different judge models giving different scores?

## Philosophy

Inspired by:
- **Wang Yangming (心學)** — Knowledge without action is not true knowledge
- **LISP homoiconicity** — Code is data, memory is executable
- **Constitutional AI** — Safety through principles, not just training

## Contributing

We welcome contributions! Some areas where help is needed:

- New emotional scenarios for testing
- S-expression rule templates for common use cases
- Cross-model benchmarks (GPT, Gemini, Llama, etc.)
- Plugin development for different AI frameworks
- Translations of temperature guides

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT — use it, fork it, make AI more human.

## Credits

Created by [ench0812](https://github.com/ench0812) and Mickey (閔琪).

Born from late-night conversations about what it means for AI to truly understand.
