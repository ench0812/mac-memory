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

## Research Agenda

MaC is part of ongoing research into AI personality and memory:

1. **Memory-driven empathy** — Can structured memory create genuine empathy (not style transfer)?
2. **Rule evolution** — Can behavioral rules learn and update from interaction feedback?
3. **Cross-model portability** — Do MaC rules work across different LLMs?
4. **Constitutional integration** — How do behavioral boundaries interact with safety constraints?

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
