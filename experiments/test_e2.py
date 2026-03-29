#!/usr/bin/env python3
"""Unit tests for E2 (graduated-comprehension-test.py)."""

import json
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

import pytest

BASE_DIR = Path(__file__).parent
SAMPLE_PATH = BASE_DIR / "sample-memories.json"


def _load_module(name, filename):
    spec = spec_from_file_location(name, BASE_DIR / filename)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


e2 = _load_module("e2", "graduated-comprehension-test.py")
encoder = _load_module("encoder", "s-expr-encoder.py")


@pytest.fixture
def encoded_memories():
    result = encoder.encode_file(str(SAMPLE_PATH))
    return result["encoded_memories"]


class TestE2Config:
    def test_model_config_has_three_levels(self):
        config = e2.get_model_config()
        assert set(config.keys()) == {"high", "mid", "low"}

    def test_question_templates_complete(self):
        assert set(e2.QUESTION_TEMPLATES.keys()) == {"basic", "reasoning", "metacognition"}


class TestE2PromptBuilding:
    def test_build_prompt_l1(self, encoded_memories):
        prompt = e2.build_prompt("L1", encoded_memories[0]["layers"]["L1"], "test?")
        assert "L1" in prompt
        assert "test?" in prompt
        assert encoded_memories[0]["layers"]["L1"] in prompt

    def test_build_prompt_l2_formats_json(self, encoded_memories):
        prompt = e2.build_prompt("L2", encoded_memories[0]["layers"]["L2"], "test?")
        assert "category" in prompt
        assert "keywords" in prompt


class TestE2DryRun:
    def test_dry_run_call(self):
        result = e2.dry_run_call("test prompt", "test-model")
        assert result["content"].startswith("[DRY RUN]")
        assert result["model"] == "test-model"
        assert result["error"] is None


class TestE2Aggregation:
    def test_compute_aggregate_stats(self):
        results = {
            "results": [
                {
                    "responses": {
                        "L1": {
                            "high": {
                                "basic": {
                                    "latency_ms": 100,
                                    "error": None,
                                    "prompt_chars": 40,
                                    "response_chars": 20,
                                },
                                "reasoning": {
                                    "latency_ms": 200,
                                    "error": "timeout",
                                    "prompt_chars": 60,
                                    "response_chars": 0,
                                },
                                "metacognition": {
                                    "latency_ms": 300,
                                    "error": None,
                                    "prompt_chars": 80,
                                    "response_chars": 40,
                                },
                            },
                            "mid": {},
                            "low": {},
                        },
                        "L2": {"high": {}, "mid": {}, "low": {}},
                        "L3": {"high": {}, "mid": {}, "low": {}},
                    }
                }
            ]
        }

        aggregate = e2.compute_aggregate_stats(results)
        stats = aggregate["by_layer_model"]["L1"]["high"]
        assert stats["calls"] == 3
        assert stats["errors"] == 1
        assert stats["avg_latency_ms"] == 200.0
        assert stats["avg_prompt_chars"] == 60.0
        assert stats["avg_response_chars"] == 20.0

        reasoning = aggregate["by_question"]["reasoning"]
        assert reasoning["calls"] == 1
        assert reasoning["errors"] == 1


class TestE2Integration:
    def test_run_test_dry(self, encoded_memories):
        results = e2.run_test(encoded_memories[:1], dry_run=True, delay=0)
        assert results["metadata"]["dry_run"] is True
        assert results["metadata"]["total_calls"] == 27
        assert "aggregate" in results
        assert results["aggregate"]["by_layer_model"]["L1"]["high"]["calls"] == 3

        sample = results["results"][0]["responses"]["L1"]["high"]["basic"]
        assert sample["prompt_chars"] > 0
        assert sample["response_chars"] > 0

    def test_generate_summary_table_contains_aggregate_sections(self, encoded_memories):
        results = e2.run_test(encoded_memories[:1], dry_run=True, delay=0)
        report = e2.generate_summary_table(results)
        assert "Aggregate Layer × Model Statistics" in report
        assert "Aggregate Question Statistics" in report
        assert "Memory: mem-001" in report
