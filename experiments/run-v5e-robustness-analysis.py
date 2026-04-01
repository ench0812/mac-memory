#!/usr/bin/env python3
"""
MaC v5e — robustness analysis on top of the E6 live Opus judge results.

Goal:
- separate peak quality (best response per scenario) from reliability (best/worst judged sample)
- quantify robustness gaps between conditions
- produce publication-ready JSON for Section 7
"""
import json
from datetime import datetime
from pathlib import Path
from random import Random
from statistics import mean, pstdev

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "results-v5d-opus-judge-2026-03-10_1645.json"
GROUPS = ["A_generic", "C2_refined", "D_minimal"]
LABELS = {
    "A_generic": "A (Generic)",
    "C2_refined": "C2 (Refined)",
    "D_minimal": "D (Minimal)",
}


def percentile(values, q):
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def summarize(values):
    if not values:
        return {"n": 0, "mean": None, "std": None, "min": None, "max": None}
    return {
        "n": len(values),
        "mean": round(mean(values), 3),
        "std": round(pstdev(values), 3),
        "min": round(min(values), 3),
        "max": round(max(values), 3),
    }


def bootstrap_mean_ci(values, rounds=10000, seed=42):
    rnd = Random(seed)
    draws = []
    n = len(values)
    for _ in range(rounds):
        sample = [values[rnd.randrange(n)] for _ in range(n)]
        draws.append(mean(sample))
    return {
        "rounds": rounds,
        "mean": round(mean(values), 3),
        "ci95": [round(percentile(draws, 0.025), 3), round(percentile(draws, 0.975), 3)],
    }


def bootstrap_diff_ci(a, b, rounds=10000, seed=42):
    rnd = Random(seed)
    draws = []
    n = len(a)
    for _ in range(rounds):
        sa = [a[rnd.randrange(n)] for _ in range(n)]
        sb = [b[rnd.randrange(n)] for _ in range(n)]
        draws.append(mean(sa) - mean(sb))
    gt0 = sum(1 for d in draws if d > 0) / len(draws)
    return {
        "rounds": rounds,
        "observed_diff": round(mean(a) - mean(b), 3),
        "ci95": [round(percentile(draws, 0.025), 3), round(percentile(draws, 0.975), 3)],
        "p_direction_gt0": round(gt0, 4),
    }


def main():
    data = json.loads(SOURCE.read_text())

    best_scores = {g: [] for g in GROUPS}
    worst_scores = {g: [] for g in GROUPS}
    judged_scores = {g: [] for g in GROUPS}
    per_scenario = []
    win_counts = {g: 0 for g in GROUPS}
    tie_counts = {g: 0 for g in GROUPS}

    for scenario in data["scenarios"]:
        scenario_best = {}
        scenario_row = {
            "id": scenario["id"],
            "name": scenario["name"],
            "best_scores": {},
            "worst_scores": {},
            "robustness_gap": {},
        }
        for g in GROUPS:
            entries = [j for j in scenario["judgments"].get(g, []) if "error" not in j]
            for entry in entries:
                judged_scores[g].append(entry["opus_score"])
                if entry["label"] == "best":
                    best_scores[g].append(entry["opus_score"])
                    scenario_best[g] = entry["opus_score"]
                    scenario_row["best_scores"][g] = entry["opus_score"]
                elif entry["label"] == "worst":
                    worst_scores[g].append(entry["opus_score"])
                    scenario_row["worst_scores"][g] = entry["opus_score"]

            if g in scenario_row["best_scores"] and g in scenario_row["worst_scores"]:
                scenario_row["robustness_gap"][g] = round(
                    scenario_row["best_scores"][g] - scenario_row["worst_scores"][g], 3)

        if scenario_best:
            top = max(scenario_best.values())
            winners = [g for g, score in scenario_best.items() if score == top]
            for g in winners:
                if len(winners) == 1:
                    win_counts[g] += 1
                else:
                    tie_counts[g] += 1
            scenario_row["best_winners"] = winners
            per_scenario.append(scenario_row)

    summary = {
        "experiment": "v5e-robustness-analysis",
        "derived_from": SOURCE.name,
        "timestamp": datetime.now().isoformat(),
        "conditions": {},
        "pairwise_best_diff": {},
        "per_scenario": per_scenario,
        "win_counts": {
            g: {"wins": win_counts[g], "ties": tie_counts[g]} for g in GROUPS
        },
    }

    for g in GROUPS:
        cond = {
            "label": LABELS[g],
            "best": summarize(best_scores[g]),
            "worst": summarize(worst_scores[g]),
            "judged_sample": summarize(judged_scores[g]),
            "best_bootstrap": bootstrap_mean_ci(best_scores[g]),
        }
        if best_scores[g] and worst_scores[g]:
            cond["robustness_gap_mean"] = round(mean(best_scores[g]) - mean(worst_scores[g]), 3)
        if best_scores[g] and judged_scores[g]:
            cond["stability_gap_best_minus_judged"] = round(mean(best_scores[g]) - mean(judged_scores[g]), 3)
        summary["conditions"][g] = cond

    pairs = [("D_minimal", "A_generic"), ("D_minimal", "C2_refined"), ("C2_refined", "A_generic")]
    for a, b in pairs:
        summary["pairwise_best_diff"][f"{a}__minus__{b}"] = bootstrap_diff_ci(best_scores[a], best_scores[b])

    # Human-readable interpretation hook for the paper draft.
    best_means = {g: summary["conditions"][g]["best"]["mean"] for g in GROUPS}
    judged_means = {g: summary["conditions"][g]["judged_sample"]["mean"] for g in GROUPS}
    summary["interpretation"] = {
        "highest_peak_quality": max(best_means, key=best_means.get),
        "highest_judged_sample_mean": max(judged_means, key=judged_means.get),
        "smallest_stability_gap": min(
            GROUPS,
            key=lambda g: summary["conditions"][g]["stability_gap_best_minus_judged"],
        ),
        "note": "C2 reaches the highest best-response mean, while D remains the most stable across the judged sample.",
    }

    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    out = BASE / f"results-v5e-robustness-analysis-{ts}.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2))

    print("=" * 72)
    print("MaC v5e robustness analysis")
    print("=" * 72)
    for g in GROUPS:
        c = summary["conditions"][g]
        print(
            f"{LABELS[g]:14} | best={c['best']['mean']:.3f} "
            f"judged={c['judged_sample']['mean']:.3f} "
            f"worst={c['worst']['mean']:.3f} "
            f"stability_gap={c['stability_gap_best_minus_judged']:.3f}"
        )
    print("\nBest-response winners:")
    for g in GROUPS:
        w = summary["win_counts"][g]
        print(f"  {LABELS[g]}: {w['wins']} wins, {w['ties']} ties")
    print("\nInterpretation:")
    print(f"  highest_peak_quality: {summary['interpretation']['highest_peak_quality']}")
    print(f"  highest_judged_sample_mean: {summary['interpretation']['highest_judged_sample_mean']}")
    print(f"  smallest_stability_gap: {summary['interpretation']['smallest_stability_gap']}")
    print(f"\nSaved: {out.name}")


if __name__ == "__main__":
    main()
