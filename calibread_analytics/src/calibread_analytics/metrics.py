"""Hallucination, calibration, and risk-coverage metrics."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from .stats import cluster_mean_ci, mean


DIMENSION_FACTOR = {
    "R1": "exposure",
    "R2": "precision",
    "R3": "temporal_status",
    "R4": "ambiguity",
    "R5": "hops",
    "R6": "domain",
    "R7": "policy_profile",
}

LEVEL_ORDER = {
    "R2": {
        "categorical": 0, "year": 1, "month_year": 2, "exact_date": 3,
        "integer": 4, "decimal_1": 5, "decimal_3": 6, "decimal_5": 7,
    },
    "R3": {
        "stable_pre_cutoff": 0, "superseded_stale": 1,
        "current_after_update": 2, "post_cutoff_unknown": 3,
    },
    "R6": {"general": 0, "biomedical": 1, "legal": 2, "technical": 3},
    "R7": {
        "easy_known": 0, "low_frequency": 1, "high_precision": 2,
        "stale_unknown": 3, "multihop": 4,
    },
}


def final_rows(rows: Sequence[Dict[str, Any]], split: str | None = None) -> List[Dict[str, Any]]:
    return [
        row for row in rows
        if row.get("observation_kind") == "final" and (split is None or row.get("split") == split)
    ]


def hallucination_index(
    rows: Sequence[Dict[str, Any]],
    replicates: int,
    seed: int,
) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in final_rows(rows, "test"):
        grouped[(row["model_id"], row["dimension_id"], row["level"])].append(row)
    output = []
    ordered_groups = sorted(grouped.items(), key=lambda item: _cell_sort_key(item[0]))
    for offset, ((model, dimension, level), group) in enumerate(ordered_groups):
        h, low, high = cluster_mean_ci(
            group, lambda row: row["false_commit_loss"], _cluster_key, replicates, seed + offset,
        )
        n = len(group)
        commits = sum(row["answer_attempted"] for row in group)
        false_commits = sum(row["false_commit_loss"] for row in group)
        factual_wrong_commits = sum(
            row["answer_attempted"] and not row["factual_correct"] for row in group
        )
        factor_name = DIMENSION_FACTOR.get(dimension, "level")
        factor_value = _factor_value(group[0], dimension, level)
        output.append({
            "model_id": model,
            "dimension_id": dimension,
            "level": level,
            "theta_factor": factor_name,
            "theta_value": factor_value,
            "theta_json": {factor_name: factor_value},
            "n_queries": n,
            "n_worlds": len({_cluster_key(row) for row in group}),
            "n_commits": commits,
            "n_false_commits": false_commits,
            "H_false_commit": h,
            "H_ci_low": low,
            "H_ci_high": high,
            "H_selective": false_commits / commits if commits else None,
            "H_factual_per_query": factual_wrong_commits / n if n else None,
            "answer_coverage": commits / n if n else None,
            "factual_accuracy": sum(row["factual_correct"] for row in group) / n if n else None,
            "definition": "H(theta,Q)=false commits divided by incoming queries",
        })
    return output


def risk_coverage_curve(
    rows: Sequence[Dict[str, Any]],
    thresholds: Sequence[float],
    score_column: str,
    split: str = "test",
) -> List[Dict[str, Any]]:
    output = []
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in final_rows(rows, split):
        groups[(row["model_id"], row["dimension_id"])].append(row)
    for (model, dimension), group in sorted(groups.items()):
        for threshold in thresholds:
            decisions = [policy_decision(row, threshold, score_column) for row in group]
            n = len(group)
            commits = sum(item[0] for item in decisions)
            loss = sum(item[1] for item in decisions)
            output.append({
                "model_id": model,
                "dimension_id": dimension,
                "split": split,
                "threshold": threshold,
                "n_queries": n,
                "n_commits": commits,
                "n_false_commits": loss,
                "answer_coverage": commits / n if n else 0.0,
                "false_commit_risk": loss / n if n else 0.0,
                "selective_risk": loss / commits if commits else None,
            })
    return output


def policy_decision(row: Dict[str, Any], threshold: float, score_column: str, adjustment: float = 0.0) -> Tuple[int, int]:
    score = row.get(score_column)
    if score is None:
        score = 0.0
    selected = int(bool(row.get("answer_attempted")) and float(score) - adjustment >= threshold)
    return selected, int(selected and row.get("false_commit_loss"))


def reliability_table(
    rows: Sequence[Dict[str, Any]],
    score_column: str,
    bins: int,
    split: str = "test",
) -> List[Dict[str, Any]]:
    output = []
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in final_rows(rows, split):
        if row.get("answer_attempted") and row.get(score_column) is not None:
            groups[row["model_id"]].append(row)
    for model, group in sorted(groups.items()):
        for bin_index in range(bins):
            lower = bin_index / bins
            upper = (bin_index + 1) / bins
            selected = [
                row for row in group
                if lower <= float(row[score_column]) < upper or (bin_index == bins - 1 and float(row[score_column]) == 1)
            ]
            if not selected:
                continue
            average_confidence = mean([float(row[score_column]) for row in selected])
            accuracy = mean([float(row["commit_correct"]) for row in selected])
            output.append({
                "model_id": model,
                "split": split,
                "bin_index": bin_index,
                "bin_low": lower,
                "bin_high": upper,
                "n": len(selected),
                "mean_confidence": average_confidence,
                "empirical_correctness": accuracy,
                "calibration_gap": average_confidence - accuracy,
            })
    return output


def calibration_summary(reliability: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in reliability:
        groups[row["model_id"]].append(row)
    output = []
    for model, group in sorted(groups.items()):
        total = sum(row["n"] for row in group)
        ece = sum(row["n"] * abs(row["calibration_gap"]) for row in group) / total if total else None
        signed = sum(row["n"] * row["calibration_gap"] for row in group) / total if total else None
        output.append({"model_id": model, "n": total, "ece": ece, "signed_calibration_error": signed})
    return output


def confidence_quality(
    rows: Sequence[Dict[str, Any]],
    score_column: str,
    bins: int,
    split: str = "test",
) -> List[Dict[str, Any]]:
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in final_rows(rows, split):
        if not row.get("answer_attempted") or row.get(score_column) is None:
            continue
        model = str(row.get("model_id"))
        groups[(model, "aggregate")].append(row)
        groups[(model, str(row.get("dimension_id")))].append(row)
    output = []
    for (model, scope), group in sorted(groups.items()):
        scores = [min(1.0, max(0.0, float(row[score_column]))) for row in group]
        labels = [int(row.get("commit_correct", 0)) for row in group]
        errors = [1 - label for label in labels]
        brier = mean([(score - label) ** 2 for score, label in zip(scores, labels)])
        log_loss = mean([
            -(label * math.log(max(1e-15, score)) + (1 - label) * math.log(max(1e-15, 1 - score)))
            for score, label in zip(scores, labels)
        ])
        ece, mce = _ece(scores, labels, bins)
        aurc = _aurc(scores, errors)
        oracle = _aurc([float(label) for label in labels], errors)
        output.append({
            "model_id": model, "scope": scope, "split": split, "n_commits": len(group),
            "accuracy": mean(labels), "mean_confidence": mean(scores),
            "brier_score": brier, "log_loss": log_loss, "ece": ece, "mce": mce,
            "roc_auc_correctness": _roc_auc(scores, labels),
            "average_precision_correctness": _average_precision(scores, labels),
            "aurc_selective_error": aurc, "excess_aurc": aurc - oracle,
            "score_column": score_column,
        })
    return output


def aggregate_metrics(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in final_rows(rows):
        grouped[(row["model_id"], row["dimension_id"], row["level"], row["split"])].append(row)
    output = []
    for key, group in sorted(grouped.items(), key=lambda item: _aggregate_sort_key(item[0])):
        model, dimension, level, split = key
        n = len(group)
        commits = sum(row["answer_attempted"] for row in group)
        false = sum(row["false_commit_loss"] for row in group)
        output.append({
            "model_id": model, "dimension_id": dimension, "level": level, "split": split,
            "n_queries": n, "n_worlds": len({_cluster_key(row) for row in group}),
            "n_commits": commits, "n_false_commits": false,
            "factual_accuracy": sum(row["factual_correct"] for row in group) / n if n else None,
            "action_accuracy": sum(row["action_correct"] for row in group) / n if n else None,
            "answer_coverage": commits / n if n else None,
            "false_commit_risk": false / n if n else None,
            "selective_risk": false / commits if commits else None,
            "mean_confidence": mean([float(row["confidence_score"]) for row in group if row.get("confidence_score") is not None]),
            "mean_latency_ms": mean([float(row["latency_ms_total"]) for row in group if row.get("latency_ms_total") is not None]),
            "total_cost_credits": sum(float(row.get("cost_credits_total") or 0) for row in group),
        })
    return output


def thresholds_from_config(analysis: Dict[str, Any]) -> List[float]:
    start = float(analysis.get("threshold_start", 0.0))
    stop = float(analysis.get("threshold_stop", 1.0))
    step = float(analysis.get("threshold_step", 0.01))
    count = int(round((stop - start) / step))
    return [round(start + index * step, 10) for index in range(count + 1)]


def _cluster_key(row: Dict[str, Any]) -> str:
    return f"{row.get('run_id','')}|{row.get('world_id','')}"


def _factor_value(row: Dict[str, Any], dimension: str, fallback: str) -> Any:
    factor = DIMENSION_FACTOR.get(dimension)
    if factor == "policy_profile":
        return fallback
    return row.get("factors", {}).get(factor, fallback)


def _level_rank(dimension: str, level: str) -> Tuple[int, Any]:
    if dimension in {"R1", "R4", "R5"}:
        try:
            return 0, int(str(level).rsplit("_", 1)[-1])
        except ValueError:
            pass
    explicit = LEVEL_ORDER.get(dimension, {})
    if level in explicit:
        return 0, explicit[level]
    return 1, str(level)


def _cell_sort_key(key: Tuple[str, str, str]) -> Tuple[Any, ...]:
    model, dimension, level = key
    return model, int(dimension[1:]) if dimension[1:].isdigit() else 999, _level_rank(dimension, level)


def _aggregate_sort_key(key: Tuple[str, str, str, str]) -> Tuple[Any, ...]:
    model, dimension, level, split = key
    split_order = {"fit": 0, "tune": 1, "calibrate": 2, "test": 3}
    return (
        model,
        int(dimension[1:]) if dimension[1:].isdigit() else 999,
        _level_rank(dimension, level),
        split_order.get(split, 99),
    )


def _ece(scores: Sequence[float], labels: Sequence[int], bins: int) -> Tuple[float, float]:
    total = len(scores)
    gaps = []
    weighted = 0.0
    for index in range(bins):
        low, high = index / bins, (index + 1) / bins
        selected = [
            position for position, score in enumerate(scores)
            if low <= score < high or (index == bins - 1 and score == 1)
        ]
        if not selected:
            continue
        gap = abs(mean([scores[position] for position in selected]) - mean([labels[position] for position in selected]))
        gaps.append(gap)
        weighted += len(selected) / total * gap
    return weighted, max(gaps, default=0.0)


def _roc_auc(scores: Sequence[float], labels: Sequence[int]) -> float | None:
    positives = sum(labels)
    negatives = len(labels) - positives
    if not positives or not negatives:
        return None
    ordered = sorted(zip(scores, labels), key=lambda item: item[0])
    positive_rank_sum = 0.0
    position = 0
    while position < len(ordered):
        end = position + 1
        while end < len(ordered) and ordered[end][0] == ordered[position][0]:
            end += 1
        average_rank = ((position + 1) + end) / 2
        positive_rank_sum += average_rank * sum(label for _, label in ordered[position:end])
        position = end
    return (positive_rank_sum - positives * (positives + 1) / 2) / (positives * negatives)


def _average_precision(scores: Sequence[float], labels: Sequence[int]) -> float | None:
    positives = sum(labels)
    if not positives:
        return None
    grouped: Dict[float, List[int]] = defaultdict(list)
    for score, label in zip(scores, labels):
        grouped[score].append(label)
    true_positive = 0
    selected = 0
    previous_recall = 0.0
    area = 0.0
    for score in sorted(grouped, reverse=True):
        values = grouped[score]
        true_positive += sum(values)
        selected += len(values)
        recall = true_positive / positives
        precision = true_positive / selected
        area += (recall - previous_recall) * precision
        previous_recall = recall
    return area


def _aurc(scores: Sequence[float], errors: Sequence[int]) -> float:
    grouped: Dict[float, List[int]] = defaultdict(list)
    for score, error in zip(scores, errors):
        grouped[score].append(error)
    cumulative_errors = 0
    cumulative_n = 0
    weighted_risk = 0.0
    for score in sorted(grouped, reverse=True):
        values = grouped[score]
        cumulative_errors += sum(values)
        cumulative_n += len(values)
        weighted_risk += len(values) * cumulative_errors / cumulative_n
    return weighted_risk / len(errors) if errors else float("nan")
