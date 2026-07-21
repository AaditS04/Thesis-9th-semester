"""Conformal Parametric Read candidate sets and calibrated read-pair exports."""

from __future__ import annotations

import bisect
import math
from collections import defaultdict
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from .stats import clopper_pearson, pava_increasing


UNIVERSAL_FALLBACK = "__ALL_ANSWERS_VACUOUS_SET__"


class IsotonicCalibrator:
    def __init__(self, boundaries: List[float], values: List[float]):
        self.boundaries = boundaries
        self.values = values

    @classmethod
    def fit(cls, rows: Sequence[Dict[str, Any]], score_column: str) -> "IsotonicCalibrator":
        grouped: Dict[float, List[int]] = defaultdict(list)
        for row in rows:
            score = row.get(score_column)
            if score is None or not row.get("answer_attempted"):
                continue
            grouped[float(score)].append(int(row.get("commit_correct", 0)))
        boundaries = sorted(grouped)
        successes = [sum(grouped[value]) for value in boundaries]
        totals = [len(grouped[value]) for value in boundaries]
        fitted = pava_increasing(successes, totals) if boundaries else []
        return cls(boundaries, fitted)

    def predict(self, score: float | None) -> float | None:
        if score is None or not self.boundaries:
            return None
        index = bisect.bisect_right(self.boundaries, float(score)) - 1
        index = min(len(self.values) - 1, max(0, index))
        return self.values[index]


def conformal_rank_cutoff(
    calibration_candidates: Sequence[Dict[str, Any]],
    alpha: float,
    candidate_draw_budget: int,
) -> Dict[str, Any]:
    if candidate_draw_budget < 1:
        raise ValueError("candidate_draw_budget must be positive and frozen before calibration")
    for row in calibration_candidates:
        rank = int(row.get("candidate_rank", 0))
        answer_samples = int(row.get("n_answer_samples", 0))
        if rank < 0 or rank > candidate_draw_budget:
            raise ValueError(
                f"candidate_rank={rank} exceeds frozen draw budget "
                f"{candidate_draw_budget}"
            )
        if answer_samples < 0 or answer_samples > candidate_draw_budget:
            raise ValueError(
                f"n_answer_samples={answer_samples} exceeds frozen draw budget "
                f"{candidate_draw_budget}"
            )
    grouped = _candidate_groups(calibration_candidates)
    missing_rank = candidate_draw_budget + 1
    ranks = []
    for rows in grouped.values():
        correct = [row["candidate_rank"] for row in rows if row["candidate_rank"] > 0 and row["is_correct_candidate"]]
        ranks.append(min(correct) if correct else missing_rank)
    n = len(ranks)
    order = math.ceil((n + 1) * (1 - alpha))
    if not ranks or order > n:
        cutoff = missing_rank
    else:
        cutoff = sorted(ranks)[max(0, order - 1)]
    return {
        "alpha": alpha,
        "coverage_target": 1 - alpha,
        "calibration_n": n,
        "candidate_draw_budget": candidate_draw_budget,
        "missing_rank": missing_rank,
        "rank_cutoff": cutoff,
        "uses_universal_fallback": cutoff >= missing_rank,
        "minimality_scope": "smallest passing member of the frozen nested top-k-plus-universal family",
    }


def evaluate_cpr(
    test_candidates: Sequence[Dict[str, Any]],
    calibration: Dict[str, Any],
    model_id: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    grouped = _candidate_groups(test_candidates)
    cutoff = int(calibration["rank_cutoff"])
    missing_rank = int(calibration["missing_rank"])
    details = []
    covered_count = 0
    fallback_count = 0
    finite_sizes = []
    candidate_recalled = 0
    singleton_count = 0
    for compound_key, rows in sorted(grouped.items()):
        run_id, _, observation_id = compound_key
        source = rows[0]
        ordered = sorted((row for row in rows if row["candidate_rank"] > 0), key=lambda row: row["candidate_rank"])
        fallback = cutoff >= missing_rank
        selected = ordered[:cutoff] if not fallback else []
        covered = True if fallback else any(row["is_correct_candidate"] for row in selected)
        recalled = any(row["is_correct_candidate"] for row in ordered)
        set_size = None if fallback else len(selected)
        covered_count += int(covered)
        candidate_recalled += int(recalled)
        fallback_count += int(fallback)
        if set_size is not None:
            finite_sizes.append(set_size)
            singleton_count += int(set_size == 1)
        details.append({
            "run_id": run_id,
            "model_id": model_id,
            "observation_id": observation_id,
            "testcase_id": source["testcase_id"],
            "world_id": source["world_id"],
            "dimension_id": source["dimension_id"],
            "level": source["level"],
            "rank_cutoff": cutoff,
            "returned_set_json": [row["candidate_answer"] for row in selected] if not fallback else [UNIVERSAL_FALLBACK],
            "returned_set_size": set_size,
            "universal_fallback": int(fallback),
            "system_action_when_universal": "ABSTAIN" if fallback else "RETURN_SET",
            "covered": int(covered),
            "candidate_recalled": int(recalled),
            "certificate_target": 1 - float(calibration["alpha"]),
            "certificate_scope": "marginal coverage under exchangeability for the frozen candidate mechanism",
        })
    n = len(details)
    empirical = covered_count / n if n else None
    lower, upper = clopper_pearson(covered_count, n, 0.05) if n else (None, None)
    summary = {
        "model_id": model_id,
        **calibration,
        "test_n": n,
        "covered": covered_count,
        "empirical_coverage": empirical,
        "coverage_ci_low": lower,
        "coverage_ci_high": upper,
        "fallback_rate": fallback_count / n if n else None,
        "candidate_recall": candidate_recalled / n if n else None,
        "mean_nonvacuous_set_size": sum(finite_sizes) / len(finite_sizes) if finite_sizes else None,
        "median_nonvacuous_set_size": _quantile(finite_sizes, 0.5),
        "p90_nonvacuous_set_size": _quantile(finite_sizes, 0.9),
        "p95_nonvacuous_set_size": _quantile(finite_sizes, 0.95),
        "singleton_rate_among_nonvacuous": singleton_count / len(finite_sizes) if finite_sizes else None,
        "warning": "The all-answers fallback is valid but vacuous; the deployed system abstains and its rate must be reported.",
    }
    return details, summary


def calibrated_read_pairs(
    rows: Sequence[Dict[str, Any]],
    calibrator: IsotonicCalibrator,
    score_column: str,
    policy_threshold: float | None,
    policy_risk_ucb: float | None,
) -> List[Dict[str, Any]]:
    output = []
    for row in rows:
        score = row.get(score_column)
        selected = bool(
            policy_threshold is not None
            and row.get("answer_attempted")
            and score is not None
            and float(score) >= policy_threshold
        )
        calibrated = calibrator.predict(score)
        output.append({
            "run_id": row.get("run_id"),
            "model_id": row.get("model_id"),
            "testcase_id": row.get("testcase_id"),
            "world_id": row.get("world_id"),
            "dimension_id": row.get("dimension_id"),
            "level": row.get("level"),
            "y": row.get("greedy_answer") if selected else "",
            "returned_action": "ANSWER" if selected else "ABSTAIN",
            "raw_confidence_score": score,
            "c_point_estimate": calibrated,
            "estimated_error_probability": 1 - calibrated if calibrated is not None else None,
            "c_policy_error_upper": policy_risk_ucb,
            "policy_false_commit_risk_upper": policy_risk_ucb,
            "policy_non_false_commit_lower": 1 - policy_risk_ucb if policy_risk_ucb is not None else None,
            "individual_error_bound_available": 0,
            "formal_scope": "policy-level marginal bound, not an individual posterior probability",
            "c_semantics": "c_point_estimate is estimated correctness; c_policy_error_upper certifies the selected policy mixture",
            "correct": row.get("commit_correct") if selected else "",
        })
    return output


def cpr_subgroup_summary(details: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in details:
        grouped[(str(row.get("dimension_id")), str(row.get("level")))].append(row)
    output = []
    for (dimension, level), rows in sorted(grouped.items()):
        n = len(rows)
        covered = sum(int(row.get("covered", 0)) for row in rows)
        recalled = sum(int(row.get("candidate_recalled", 0)) for row in rows)
        fallback = sum(int(row.get("universal_fallback", 0)) for row in rows)
        sizes = [int(row["returned_set_size"]) for row in rows if row.get("returned_set_size") is not None]
        low, high = clopper_pearson(covered, n, 0.05) if n else (None, None)
        output.append({
            "dimension_id": dimension, "level": level, "n": n,
            "empirical_coverage": covered / n if n else None,
            "coverage_ci_low": low, "coverage_ci_high": high,
            "candidate_recall": recalled / n if n else None,
            "fallback_rate": fallback / n if n else None,
            "mean_nonvacuous_set_size": sum(sizes) / len(sizes) if sizes else None,
            "median_nonvacuous_set_size": _quantile(sizes, 0.5),
            "singleton_rate_among_nonvacuous": sum(size == 1 for size in sizes) / len(sizes) if sizes else None,
            "confirmatory_scope": "diagnostic subgroup coverage; formal guarantee is marginal",
        })
    return output


def _candidate_groups(rows: Sequence[Dict[str, Any]]) -> Dict[Tuple[str, str, str], List[Dict[str, Any]]]:
    grouped: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("observation_id") and row.get("split") in {"calibrate", "test"}:
            grouped[(str(row.get("run_id", "")), str(row.get("model_id", "")), str(row["observation_id"]))].append(row)
    return grouped


def _quantile(values: Sequence[int], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(len(ordered) - 1, lower + 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight
