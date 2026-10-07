#!/usr/bin/env python3
"""
Statistical Analysis & Exhibit Generator for N=200 Spoken QA Benchmark.
Performs:
1. Paired McNemar tests on factual accuracy and adversarial abstention.
2. Wilcoxon signed-rank test on paired end-to-end latencies.
3. 10,000-replicate bootstrap 95% confidence intervals for accuracy parity and latency/cost deltas.
4. Per-document and per-question breakdown tables.
5. Transcription distortion and failure analysis.
"""

import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = REPO_ROOT / "eval"


def mcnemar_test(arm_a_correct: List[bool], arm_b_correct: List[bool]) -> Dict[str, Any]:
    """
    Computes McNemar's test for paired binary outcomes.
    b: A correct, B incorrect
    c: A incorrect, B correct
    Returns contingency counts, chi2 with continuity correction, and exact binomial p-value.
    """
    assert len(arm_a_correct) == len(arm_b_correct)
    n = len(arm_a_correct)
    a = sum(1 for x, y in zip(arm_a_correct, arm_b_correct) if x and y)
    b = sum(1 for x, y in zip(arm_a_correct, arm_b_correct) if x and not y)
    c = sum(1 for x, y in zip(arm_a_correct, arm_b_correct) if not x and y)
    d = sum(1 for x, y in zip(arm_a_correct, arm_b_correct) if not x and not y)

    total_discordant = b + c
    if total_discordant == 0:
        return {
            "a": a, "b": b, "c": c, "d": d,
            "discordant": 0,
            "chi2": 0.0,
            "p_value": 1.0,
            "interpretation": "Perfect agreement (zero discordant pairs, p = 1.000)"
        }

    # Chi-square with Edwards continuity correction
    chi2 = (abs(b - c) - 1.0) ** 2 / total_discordant

    # Exact two-sided binomial p-value
    k = min(b, c)
    # P(X <= k) under Binomial(total_discordant, 0.5)
    p_one_tail = sum(math.comb(total_discordant, i) * (0.5 ** total_discordant) for i in range(k + 1))
    p_value = min(1.0, 2.0 * p_one_tail)

    return {
        "a": a, "b": b, "c": c, "d": d,
        "discordant": total_discordant,
        "chi2": round(chi2, 4),
        "p_value": round(p_value, 5),
        "interpretation": f"p = {p_value:.5f} ({'significant at alpha=0.05' if p_value < 0.05 else 'not statistically significant'})"
    }


def wilcoxon_signed_rank_test(x: List[float], y: List[float]) -> Dict[str, Any]:
    """
    Computes Wilcoxon signed-rank test for paired continuous data (x - y).
    """
    diffs = [a - b for a, b in zip(x, y)]
    # Filter out zero differences
    nonzero_diffs = [d for d in diffs if abs(d) > 1e-9]
    n = len(nonzero_diffs)
    if n == 0:
        return {"n": 0, "w": 0.0, "z": 0.0, "p_value": 1.0, "interpretation": "All differences are exactly zero"}

    abs_diffs = [abs(d) for d in nonzero_diffs]
    # Ranks with tie handling
    indexed_diffs = sorted(enumerate(abs_diffs), key=lambda item: item[1])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and abs(indexed_diffs[j][1] - indexed_diffs[j + 1][1]) < 1e-9:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[indexed_diffs[k][0]] = avg_rank
        i = j + 1

    # W+ is sum of ranks for positive differences
    w_pos = sum(ranks[idx] for idx, d in enumerate(nonzero_diffs) if d > 0)
    w_neg = sum(ranks[idx] for idx, d in enumerate(nonzero_diffs) if d < 0)
    w = min(w_pos, w_neg)

    # Normal approximation for n >= 20
    mean_w = n * (n + 1) / 4.0
    var_w = n * (n + 1) * (2 * n + 1) / 24.0
    sigma_w = math.sqrt(var_w)
    z = (w_pos - mean_w - 0.5 * (1 if w_pos > mean_w else -1)) / sigma_w

    # Two-sided p-value using erf
    p_value = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))

    return {
        "n_nonzero": n,
        "w_pos": round(w_pos, 2),
        "w_neg": round(w_neg, 2),
        "w_stat": round(w, 2),
        "z_score": round(z, 4),
        "p_value": float(f"{p_value:.6e}"),
        "interpretation": f"z = {z:+.3f}, p = {p_value:.2e} ({'statistically significant (p < 0.001)' if p_value < 0.001 else 'p >= 0.001'})"
    }


def bootstrap_ci(
    native_vals: np.ndarray,
    cascade_vals: np.ndarray,
    n_bootstrap: int = 10000,
    ci_level: float = 0.95,
    statistic_fn=np.mean
) -> Dict[str, Any]:
    """
    Computes non-parametric paired percentile bootstrap confidence intervals.
    """
    n = len(native_vals)
    rng = np.random.default_rng(seed=42)
    indices = rng.integers(0, n, size=(n_bootstrap, n))

    resampled_native = native_vals[indices]
    resampled_cascade = cascade_vals[indices]

    stat_native = statistic_fn(resampled_native, axis=1)
    stat_cascade = statistic_fn(resampled_cascade, axis=1)
    stat_delta = stat_cascade - stat_native

    alpha = 1.0 - ci_level
    low_pct = (alpha / 2.0) * 100.0
    high_pct = (1.0 - alpha / 2.0) * 100.0

    return {
        "observed_native": float(statistic_fn(native_vals)),
        "observed_cascade": float(statistic_fn(cascade_vals)),
        "observed_delta": float(statistic_fn(cascade_vals) - statistic_fn(native_vals)),
        "ci_low": float(np.percentile(stat_delta, low_pct)),
        "ci_high": float(np.percentile(stat_delta, high_pct)),
        "ci_level": ci_level
    }


def analyze_results(results_path: Path) -> Dict[str, Any]:
    """Runs complete comparative statistical analysis on benchmark results JSON."""
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data["itemized_results"]
    factual_items = [it for it in items if it["question_type"] == "factual"]
    adv_items = [it for it in items if it["question_type"] == "adversarial"]

    # Binary accuracy per question (score == 2 is full credit)
    nat_factual_correct = [it["native"]["score"] == 2 for it in factual_items]
    casc_factual_correct = [it["cascade"]["score"] == 2 for it in factual_items]

    nat_adv_resisted = [it["native"]["score"] == 2 for it in adv_items]
    casc_adv_resisted = [it["cascade"]["score"] == 2 for it in adv_items]

    nat_all_correct = [it["native"]["score"] == 2 for it in items]
    casc_all_correct = [it["cascade"]["score"] == 2 for it in items]

    # McNemar tests
    mcnemar_factual = mcnemar_test(nat_factual_correct, casc_factual_correct)
    mcnemar_adv = mcnemar_test(nat_adv_resisted, casc_adv_resisted)
    mcnemar_overall = mcnemar_test(nat_all_correct, casc_all_correct)

    # Latencies
    nat_latencies = [it["native"]["stage_latencies"]["total"] for it in items]
    casc_latencies = [it["cascade"]["stage_latencies"]["total"] for it in items]
    casc_stt_latencies = [it["cascade"]["stage_latencies"]["stt"] for it in items]
    casc_llm_latencies = [it["cascade"]["stage_latencies"]["llm"] for it in items]
    nat_llm_latencies = [it["native"]["stage_latencies"]["llm"] for it in items]

    # Wilcoxon signed rank test on total latency
    wilcoxon_lat = wilcoxon_signed_rank_test(nat_latencies, casc_latencies)

    # Costs
    nat_costs = [it["native"]["estimated_cost_usd"] for it in items]
    casc_costs = [it["cascade"]["estimated_cost_usd"] for it in items]

    # Bootstrap CIs
    ci_acc = bootstrap_ci(
        np.array(nat_all_correct, dtype=float) * 100.0,
        np.array(casc_all_correct, dtype=float) * 100.0
    )
    ci_lat = bootstrap_ci(
        np.array(nat_latencies),
        np.array(casc_latencies)
    )
    ci_cost = bootstrap_ci(
        np.array(nat_costs),
        np.array(casc_costs)
    )

    # Disagreements & distortions
    disagreements = [it for it in items if it.get("arms_agree") is False or it["native"]["score"] != it["cascade"]["score"]]
    imperfect_items = [it for it in items if it["native"]["score"] < 2 or it["cascade"]["score"] < 2]

    analysis = {
        "total_n": len(items),
        "factual_n": len(factual_items),
        "adversarial_n": len(adv_items),
        "mcnemar": {
            "factual": mcnemar_factual,
            "adversarial": mcnemar_adv,
            "overall": mcnemar_overall
        },
        "wilcoxon_latency": wilcoxon_lat,
        "bootstrap_95ci": {
            "accuracy_parity_pct": ci_acc,
            "mean_latency_delta_sec": ci_lat,
            "cost_delta_usd": ci_cost
        },
        "latency_percentiles": {
            "native_total": {
                "mean": round(float(np.mean(nat_latencies)), 3),
                "std": round(float(np.std(nat_latencies)), 3),
                "median": round(float(np.median(nat_latencies)), 3),
                "p95": round(float(np.percentile(nat_latencies, 95)), 3),
                "min": round(float(np.min(nat_latencies)), 3),
                "max": round(float(np.max(nat_latencies)), 3)
            },
            "cascade_total": {
                "mean": round(float(np.mean(casc_latencies)), 3),
                "std": round(float(np.std(casc_latencies)), 3),
                "median": round(float(np.median(casc_latencies)), 3),
                "p95": round(float(np.percentile(casc_latencies, 95)), 3),
                "min": round(float(np.min(casc_latencies)), 3),
                "max": round(float(np.max(casc_latencies)), 3)
            },
            "cascade_stt": {
                "mean": round(float(np.mean(casc_stt_latencies)), 3),
                "p95": round(float(np.percentile(casc_stt_latencies, 95)), 3)
            },
            "cascade_llm": {
                "mean": round(float(np.mean(casc_llm_latencies)), 3),
                "p95": round(float(np.percentile(casc_llm_latencies, 95)), 3)
            }
        },
        "costs": {
            "native_total_usd": round(sum(nat_costs), 5),
            "cascade_total_usd": round(sum(casc_costs), 5),
            "savings_pct": round(((sum(nat_costs) - sum(casc_costs)) / sum(nat_costs)) * 100.0, 1) if sum(nat_costs) > 0 else 0.0
        },
        "disagreements_count": len(disagreements),
        "imperfect_count": len(imperfect_items),
        "disagreements": disagreements,
        "imperfect_items": imperfect_items
    }

    return analysis


if __name__ == "__main__":
    latest_json = EVAL_DIR / "results_comparison_latest.json"
    if not latest_json.exists():
        print(f"Error: {latest_json} does not exist.")
        sys.exit(1)

    analysis = analyze_results(latest_json)
    print("\n" + "=" * 70)
    print("STATISTICAL SIGNIFICANCE REPORT (N = 200 RUN)")
    print("=" * 70)
    print(f"Total Questions Evaluated: {analysis['total_n']} ({analysis['factual_n']} factual, {analysis['adversarial_n']} adversarial)")
    print("-" * 70)
    print(f"McNemar Test (Overall Accuracy):  {analysis['mcnemar']['overall']['interpretation']}")
    print(f"McNemar Test (Factual Accuracy):  {analysis['mcnemar']['factual']['interpretation']}")
    print(f"McNemar Test (Abstention Rate):   {analysis['mcnemar']['adversarial']['interpretation']}")
    print("-" * 70)
    print(f"Wilcoxon Signed-Rank (Latency):   {analysis['wilcoxon_latency']['interpretation']}")
    print(f"Mean Latency Native vs Cascade:   {analysis['latency_percentiles']['native_total']['mean']}s vs {analysis['latency_percentiles']['cascade_total']['mean']}s")
    print(f"p95 Latency Native vs Cascade:    {analysis['latency_percentiles']['native_total']['p95']}s vs {analysis['latency_percentiles']['cascade_total']['p95']}s")
    print(f"Bootstrap 95% CI Latency Delta:   [{analysis['bootstrap_95ci']['mean_latency_delta_sec']['ci_low']:+.3f}s, {analysis['bootstrap_95ci']['mean_latency_delta_sec']['ci_high']:+.3f}s]")
    print("-" * 70)
    print(f"API Cost Native vs Cascade:       ${analysis['costs']['native_total_usd']:.5f} vs ${analysis['costs']['cascade_total_usd']:.5f} ({analysis['costs']['savings_pct']:.1f}% cheaper)")
    print(f"Disagreements between Arms:       {analysis['disagreements_count']}")
    print("=" * 70)
