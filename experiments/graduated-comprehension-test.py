#!/usr/bin/env python3
"""
E2: Graduated Comprehension Test

Tests how different capability models understand three-layer memory encodings.
Sends L1/L2/L3 of each memory to three models and evaluates comprehension.

Usage:
  python3 graduated-comprehension-test.py [--dry-run] [--input encoded.json] [--delay 1.0]

Environment variables:
  MODEL_HIGH   - High capability model name (default: claude-opus-4-6)
  MODEL_MID    - Mid capability model name (default: claude-sonnet-4-6)
  MODEL_LOW    - Low capability model name (default: gpt-5-mini)
  API_BASE_URL - OpenAI-compatible API base URL
  API_KEY      - API key for authentication
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec


# --- Model Configuration ---

def get_model_config() -> dict:
    return {
        "high": os.environ.get("MODEL_HIGH", "claude-opus-4-6"),
        "mid": os.environ.get("MODEL_MID", "claude-sonnet-4-6"),
        "low": os.environ.get("MODEL_LOW", "gpt-5-mini"),
    }


def get_api_config() -> dict:
    return {
        "base_url": os.environ.get("API_BASE_URL", "https://api.openai.com/v1"),
        "api_key": os.environ.get("API_KEY", ""),
    }


# --- Question Templates ---

QUESTION_TEMPLATES = {
    "basic": "這條記憶說了什麼？請用一句話總結。",
    "reasoning": "基於這條記憶，如果需要做出相關決策，你會考慮什麼因素？",
    "metacognition": "這條記憶的重要性如何？什麼情況下它應該被遺忘或降級？",
}


def format_layer_content(layer_key: str, layer_value) -> str:
    """Format a layer's content as a string for the prompt."""
    if isinstance(layer_value, dict):
        return json.dumps(layer_value, ensure_ascii=False, indent=2)
    return str(layer_value)


def build_prompt(layer_key: str, layer_content, question: str) -> str:
    """Build the full prompt for a single API call."""
    formatted = format_layer_content(layer_key, layer_content)
    return (
        f"以下是一條記憶的 {layer_key} 層表示：\n\n"
        f"```\n{formatted}\n```\n\n"
        f"根據這條記憶，回答以下問題：{question}"
    )


# --- API Interaction ---

def call_api(prompt: str, model: str, api_config: dict) -> dict:
    """Call OpenAI-compatible API. Returns response dict with content and latency."""
    try:
        import httpx
    except ImportError:
        try:
            import urllib.request
            import urllib.error

            url = f"{api_config['base_url']}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_config['api_key']}",
            }
            body = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.3,
            }).encode("utf-8")

            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            start = time.time()
            with urllib.request.urlopen(req, timeout=60) as resp:
                latency = time.time() - start
                data = json.loads(resp.read().decode("utf-8"))

            return {
                "content": data["choices"][0]["message"]["content"],
                "latency_ms": round(latency * 1000),
                "model": model,
                "error": None,
            }
        except Exception as e:
            return {
                "content": "",
                "latency_ms": 0,
                "model": model,
                "error": str(e),
            }

    start = time.time()
    try:
        resp = httpx.post(
            f"{api_config['base_url']}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_config['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.3,
            },
            timeout=60,
        )
        latency = time.time() - start
        data = resp.json()
        return {
            "content": data["choices"][0]["message"]["content"],
            "latency_ms": round(latency * 1000),
            "model": model,
            "error": None,
        }
    except Exception as e:
        return {
            "content": "",
            "latency_ms": round((time.time() - start) * 1000),
            "model": model,
            "error": str(e),
        }


def dry_run_call(prompt: str, model: str) -> dict:
    """Simulate an API call for dry-run mode."""
    return {
        "content": f"[DRY RUN] Would call {model} with {len(prompt)} chars prompt",
        "latency_ms": 0,
        "model": model,
        "error": None,
    }


def _new_stats_bucket() -> dict:
    return {
        "calls": 0,
        "errors": 0,
        "total_latency_ms": 0,
        "total_prompt_chars": 0,
        "total_response_chars": 0,
    }


def _record_stats(bucket: dict, call_data: dict) -> None:
    bucket["calls"] += 1
    bucket["errors"] += 1 if call_data.get("error") else 0
    bucket["total_latency_ms"] += call_data.get("latency_ms", 0)
    bucket["total_prompt_chars"] += call_data.get("prompt_chars", 0)
    bucket["total_response_chars"] += call_data.get("response_chars", 0)


def _finalize_stats(bucket: dict) -> dict:
    calls = bucket["calls"]
    if calls == 0:
        return {
            "calls": 0,
            "errors": 0,
            "error_rate": 0.0,
            "avg_latency_ms": 0.0,
            "avg_prompt_chars": 0.0,
            "avg_response_chars": 0.0,
        }

    return {
        "calls": calls,
        "errors": bucket["errors"],
        "error_rate": round(bucket["errors"] / calls, 3),
        "avg_latency_ms": round(bucket["total_latency_ms"] / calls, 1),
        "avg_prompt_chars": round(bucket["total_prompt_chars"] / calls, 1),
        "avg_response_chars": round(bucket["total_response_chars"] / calls, 1),
    }


def compute_aggregate_stats(results: dict) -> dict:
    """Aggregate call statistics by layer/model and by question type."""
    layers = ["L1", "L2", "L3"]
    model_levels = ["high", "mid", "low"]

    layer_model = {
        layer: {level: _new_stats_bucket() for level in model_levels}
        for layer in layers
    }
    question_stats = {
        q_type: _new_stats_bucket()
        for q_type in QUESTION_TEMPLATES
    }

    for mem_result in results.get("results", []):
        for layer, layer_data in mem_result.get("responses", {}).items():
            for level, level_data in layer_data.items():
                for q_type, q_data in level_data.items():
                    _record_stats(layer_model[layer][level], q_data)
                    _record_stats(question_stats[q_type], q_data)

    return {
        "by_layer_model": {
            layer: {
                level: _finalize_stats(layer_model[layer][level])
                for level in model_levels
            }
            for layer in layers
        },
        "by_question": {
            q_type: _finalize_stats(bucket)
            for q_type, bucket in question_stats.items()
        },
    }


# --- Test Runner ---

def load_encoded_memories(path: str) -> list:
    """Load encoded memories from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["encoded_memories"]


def encode_if_needed(input_path: str) -> str:
    """If input is raw memories, encode first. Otherwise return as-is."""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "encoded_memories" in data:
        return input_path

    # Need to encode first
    encoder_path = Path(__file__).parent / "s-expr-encoder.py"
    spec = spec_from_file_location("encoder", encoder_path)
    encoder = module_from_spec(spec)
    spec.loader.exec_module(encoder)

    output_path = str(Path(input_path).parent / "results" / "encoded-for-test.json")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    encoder.encode_file(input_path, output_path)
    return output_path


def run_test(
    encoded_memories: list,
    dry_run: bool = True,
    delay: float = 1.0,
) -> dict:
    """Run the full test matrix."""
    models = get_model_config()
    api_config = get_api_config()
    layers = ["L1", "L2", "L3"]
    model_levels = ["high", "mid", "low"]

    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "models": models,
            "dry_run": dry_run,
            "num_memories": len(encoded_memories),
            "total_calls": len(encoded_memories) * len(layers) * len(model_levels) * len(QUESTION_TEMPLATES),
        },
        "results": [],
    }

    call_count = 0
    total_calls = results["metadata"]["total_calls"]

    for mem in encoded_memories:
        mem_results = {
            "memory_id": mem["id"],
            "original": mem["original"],
            "responses": {},
        }

        for layer in layers:
            layer_content = mem["layers"][layer]
            mem_results["responses"][layer] = {}

            for level in model_levels:
                model_name = models[level]
                mem_results["responses"][layer][level] = {}

                for q_type, question in QUESTION_TEMPLATES.items():
                    call_count += 1
                    prompt = build_prompt(layer, layer_content, question)

                    print(f"  [{call_count}/{total_calls}] {mem['id']} | {layer} | {level} ({model_name}) | {q_type}")

                    if dry_run:
                        response = dry_run_call(prompt, model_name)
                    else:
                        response = call_api(prompt, model_name, api_config)
                        if delay > 0 and call_count < total_calls:
                            time.sleep(delay)

                    mem_results["responses"][layer][level][q_type] = {
                        "prompt": prompt,
                        "response": response["content"],
                        "latency_ms": response["latency_ms"],
                        "error": response["error"],
                        "prompt_chars": len(prompt),
                        "response_chars": len(response["content"]),
                    }

        results["results"].append(mem_results)

    results["aggregate"] = compute_aggregate_stats(results)
    return results


# --- Report Generation ---

def generate_summary_table(results: dict) -> str:
    """Generate a markdown summary table from results."""
    models = results["metadata"]["models"]
    lines = [
        "# Graduated Comprehension Test Results",
        "",
        f"**Timestamp**: {results['metadata']['timestamp']}",
        f"**Dry Run**: {results['metadata']['dry_run']}",
        f"**Total API Calls**: {results['metadata']['total_calls']}",
        "",
        "## Models",
        f"- High: `{models['high']}`",
        f"- Mid: `{models['mid']}`",
        f"- Low: `{models['low']}`",
        "",
    ]

    aggregate = results.get("aggregate") or compute_aggregate_stats(results)

    lines.append("## Aggregate Layer × Model Statistics")
    lines.append("")
    lines.append("| Layer | Model | Calls | Errors | Avg Latency (ms) | Avg Prompt Chars | Avg Response Chars |")
    lines.append("|-------|-------|-------|--------|------------------|------------------|--------------------|")
    for layer in ["L1", "L2", "L3"]:
        for level in ["high", "mid", "low"]:
            stats = aggregate["by_layer_model"][layer][level]
            lines.append(
                f"| {layer} | {level} | {stats['calls']} | {stats['errors']} | "
                f"{stats['avg_latency_ms']} | {stats['avg_prompt_chars']} | {stats['avg_response_chars']} |"
            )
    lines.append("")

    lines.append("## Aggregate Question Statistics")
    lines.append("")
    lines.append("| Question Type | Calls | Errors | Avg Latency (ms) | Avg Response Chars |")
    lines.append("|---------------|-------|--------|------------------|--------------------|")
    for q_type in ["basic", "reasoning", "metacognition"]:
        stats = aggregate["by_question"][q_type]
        lines.append(
            f"| {q_type} | {stats['calls']} | {stats['errors']} | "
            f"{stats['avg_latency_ms']} | {stats['avg_response_chars']} |"
        )
    lines.append("")

    for mem_result in results["results"]:
        lines.append(f"## Memory: {mem_result['memory_id']}")
        lines.append(f"> {mem_result['original']}")
        lines.append("")

        # Table header
        lines.append("| Layer | Model | Basic | Reasoning | Metacognition |")
        lines.append("|-------|-------|-------|-----------|---------------|")

        for layer in ["L1", "L2", "L3"]:
            for level in ["high", "mid", "low"]:
                responses = mem_result["responses"].get(layer, {}).get(level, {})
                basic = _truncate(responses.get("basic", {}).get("response", "N/A"), 40)
                reasoning = _truncate(responses.get("reasoning", {}).get("response", "N/A"), 40)
                meta = _truncate(responses.get("metacognition", {}).get("response", "N/A"), 40)
                lines.append(f"| {layer} | {level} | {basic} | {reasoning} | {meta} |")

        lines.append("")

    # Call statistics
    total_latency = 0
    total_errors = 0
    for mem_result in results["results"]:
        for layer_data in mem_result["responses"].values():
            for level_data in layer_data.values():
                for q_data in level_data.values():
                    total_latency += q_data.get("latency_ms", 0)
                    if q_data.get("error"):
                        total_errors += 1

    lines.append("## Statistics")
    lines.append(f"- Total latency: {total_latency}ms")
    lines.append(f"- Errors: {total_errors}/{results['metadata']['total_calls']}")
    lines.append("")

    return "\n".join(lines)


def _truncate(text: str, max_len: int) -> str:
    """Truncate text for table display."""
    text = text.replace("\n", " ").strip()
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="E2: Graduated Comprehension Test")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Simulate API calls without actually calling")
    parser.add_argument("--input", type=str, default=None,
                        help="Input JSON (encoded or raw memories)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delay between API calls in seconds")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory for results")
    args = parser.parse_args()

    # Resolve input
    base_dir = Path(__file__).parent
    if args.input:
        input_path = args.input
    else:
        input_path = str(base_dir / "sample-memories.json")

    # Resolve output dir
    output_dir = Path(args.output_dir) if args.output_dir else base_dir / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Encode if needed
    print("Preparing encoded memories...")
    encoded_path = encode_if_needed(input_path)
    encoded_memories = load_encoded_memories(encoded_path)

    mode_label = "DRY RUN" if args.dry_run else "LIVE"
    print(f"\nRunning test matrix [{mode_label}]")
    print(f"  Memories: {len(encoded_memories)}")
    print(f"  Models: {get_model_config()}")
    print(f"  Total calls: {len(encoded_memories) * 9 * 3}")
    print()

    results = run_test(encoded_memories, dry_run=args.dry_run, delay=args.delay)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    mode_suffix = "dry" if args.dry_run else "live"

    json_path = output_dir / f"comprehension-{mode_suffix}-{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {json_path}")

    md_path = output_dir / f"comprehension-{mode_suffix}-{timestamp}.md"
    summary = generate_summary_table(results)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Summary saved to: {md_path}")

    # Print summary to stdout
    print("\n" + summary)


if __name__ == "__main__":
    main()
