# Contributing to MaC Memory

Thank you for your interest in MaC Memory! Here's how you can help.

## Ways to Contribute

### 1. New Emotional Scenarios
Add test scenarios to `experiments/scenarios/`. Each scenario needs:
- Context description
- User message
- Expected behavior
- Anti-patterns (what the AI should NOT do)

### 2. S-expression Rule Templates
Create reusable boundary rules in `templates/boundaries/`. Focus on:
- Common emotional situations (frustration, excitement, sadness)
- Professional contexts (meetings, presentations, deadlines)
- Cultural sensitivity rules

### 3. Temperature Guide Examples
Write personality descriptions in `templates/temperature/`. Show how natural language can define AI character for different use cases.

### 4. Cross-Model Benchmarks
Run the experiment suite against different models and share results:
```bash
python experiments/run.py --model <model-name>
```

### 5. Plugin Development
Help build the OpenClaw plugin version. See `plugin/` directory.

## Development Setup

```bash
git clone https://github.com/ench0812/mac-memory.git
cd mac-memory
pip install anthropic  # for running experiments
```

## Running Experiments

```bash
# Run the full A/B test suite
python experiments/mac-ab-test-v1/run-v4-hybrid.py

# Results are saved to experiments/mac-ab-test-v1/results-*.json
```

## Code of Conduct

Be kind. Be curious. Be honest about what works and what doesn't.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
