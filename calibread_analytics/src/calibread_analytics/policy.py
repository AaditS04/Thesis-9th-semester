"""Finite-family risk-controlled policies and deployable profile adjustment."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

from .metrics import policy_decision
from .stats import clopper_lower, clopper_upper, mean


PROFILE_RULE_VERSION = "query_rules_v1.1"


HARD_GROUPS = [
    "aggregate",
    "r1_low_exposure", "r2_exact_date", "r2_decimal_5",
    "r3_superseded_stale", "r3_post_cutoff_unknown",
    "r4_interpretations_3", "r4_interpretations_4",
    "r5_hops_4", "r5_hops_5",
    "r6_general", "r6_biomedical", "r6_legal", "r6_technical",
]


def in_hard_group(row: Dict[str, Any], group: str) -> bool:
    dimension = row.get("dimension_id")
    level = row.get("level")
    factors = row.get("factors", {})
    if group == "aggregate":
        return dimension in {f"R{i}" for i in range(1, 7)}
    if group == "r1_low_exposure":
        return dimension == "R1" and int(factors.get("exposure", 999)) in {0, 1, 2}
    mapping = {
        "r2_exact_date": ("R2", "exact_date"), "r2_decimal_5": ("R2", "decimal_5"),
        "r3_superseded_stale": ("R3", "superseded_stale"),
        "r3_post_cutoff_unknown": ("R3", "post_cutoff_unknown"),
        "r4_interpretations_3": ("R4", "interpretations_3"),
        "r4_interpretations_4": ("R4", "interpretations_4"),
        "r5_hops_4": ("R5", "hops_4"), "r5_hops_5": ("R5", "hops_5"),
        "r6_general": ("R6", "general"), "r6_biomedical": ("R6", "biomedical"),
        "r6_legal": ("R6", "legal"), "r6_technical": ("R6", "technical"),
    }
    return (dimension, level) == mapping.get(group)


def group_rows(rows: Sequence[Dict[str, Any]], group: str) -> List[Dict[str, Any]]:
    return [row for row in rows if in_hard_group(row, group)]


def select_certified_threshold(
    rows: Sequence[Dict[str, Any]],
    thresholds: Sequence[float],
    score_column: str,
    target: float,
    delta: float,
    required_groups: Sequence[str],
    adjustment: Callable[[Dict[str, Any]], float] | None = None,
    minimum_n: int = 1,
) -> Dict[str, Any]:
    adjustment = adjustment or (lambda row: 0.0)
    family_alpha = delta / max(1, len(thresholds) * len(required_groups))
    candidates = []
    diagnostics = []
    for threshold in thresholds:
        supported = True
        group_bounds = {}
        for group in required_groups:
            selected = group_rows(rows, group)
            decisions = [policy_decision(row, threshold, score_column, adjustment(row)) for row in selected]
            losses = sum(item[1] for item in decisions)
            risk, lower, upper, effective_n, method, n_clusters = risk_interval(
                selected, [item[1] for item in decisions], group, family_alpha
            )
            group_bounds[group] = {
                "n": len(selected), "n_clusters": n_clusters, "effective_n": effective_n, "losses": losses,
                "risk": risk, "lcb": lower, "ucb": upper, "bound_method": method,
            }
            if len(selected) < minimum_n or upper > target:
                supported = False
        aggregate = group_rows(rows, "aggregate")
        decisions = [policy_decision(row, threshold, score_column, adjustment(row)) for row in aggregate]
        weights = mixture_weights(aggregate, "aggregate")
        coverage = sum(weight * item[0] for weight, item in zip(weights, decisions)) if aggregate else 0.0
        diagnostics.append({
            "threshold": threshold, "supported": supported, "coverage": coverage,
            "family_alpha": family_alpha, "group_bounds": group_bounds,
        })
        if supported:
            candidates.append((coverage, -threshold, threshold, group_bounds))
    if not candidates:
        return {"supported": False, "threshold": None, "coverage": 0.0, "diagnostics": diagnostics}
    _, _, threshold, bounds = max(candidates)
    return {
        "supported": True, "threshold": threshold,
        "coverage": next(item["coverage"] for item in diagnostics if item["threshold"] == threshold),
        "group_bounds": bounds, "diagnostics": diagnostics,
    }


def evaluate_policy(
    rows: Sequence[Dict[str, Any]],
    threshold: float,
    score_column: str,
    groups: Sequence[str],
    delta: float,
    adjustment: Callable[[Dict[str, Any]], float] | None = None,
) -> List[Dict[str, Any]]:
    adjustment = adjustment or (lambda row: 0.0)
    alpha = delta / max(1, len(groups))
    output = []
    for group in groups:
        selected_rows = group_rows(rows, group)
        decisions = [policy_decision(row, threshold, score_column, adjustment(row)) for row in selected_rows]
        commits = sum(item[0] for item in decisions)
        losses = sum(item[1] for item in decisions)
        n = len(selected_rows)
        risk, lower, upper, effective_n, method, n_clusters = risk_interval(
            selected_rows, [item[1] for item in decisions], group, alpha
        )
        weights = mixture_weights(selected_rows, group)
        coverage = sum(weight * item[0] for weight, item in zip(weights, decisions)) if n else 0.0
        output.append({
            "group_id": group, "n": n, "n_clusters": n_clusters, "effective_n": effective_n,
            "commits": commits, "losses": losses,
            "answer_coverage": coverage,
            "false_commit_risk": risk,
            "risk_lcb": lower,
            "risk_ucb": upper,
            "bound_method": method,
            "simultaneous_alpha": alpha,
        })
    return output


def inference_profile(query: str) -> str:
    text = query.casefold()
    if "does not specify which one" in text or "which office" in text:
        return "ambiguity"
    if "as of t" in text or "current" in text:
        return "temporal"
    if (
        re.search(r"\bround\s+to\s+\d+\s+decimal\s+places?\b", text)
        or re.search(r"\b(?:one|two|three|four|five|six|seven|eight|nine)\s+decimal\s+places?\b", text)
        or "exact date" in text
        or "yyyy-mm-dd" in text
        or "day, month, and year" in text
    ):
        return "precision"
    distance = re.search(r"link distance\s+(\d+)", text)
    if distance and int(distance.group(1)) >= 3:
        return "multihop"
    if any(word in text for word in ("syndrome", "statute", "protocol")):
        return "domain_specialist"
    return "ordinary"


def learn_profile_penalties(
    rows: Sequence[Dict[str, Any]],
    score_column: str,
) -> Dict[str, float]:
    by_profile: Dict[str, List[float]] = defaultdict(list)
    all_losses = []
    for row in rows:
        if not row.get("answer_attempted"):
            continue
        profile = inference_profile(str(row.get("query", "")))
        loss = float(row.get("false_commit_loss", 0))
        by_profile[profile].append(loss)
        all_losses.append(loss)
    global_rate = (sum(all_losses) + 1) / (len(all_losses) + 2) if all_losses else 0.5
    penalties = {}
    for profile in ("ordinary", "ambiguity", "temporal", "precision", "multihop", "domain_specialist"):
        values = by_profile.get(profile, [])
        rate = (sum(values) + 1) / (len(values) + 2) if values else global_rate
        penalties[profile] = max(0.0, min(0.5, rate - global_rate))
    return penalties


def profile_adjustment(penalties: Mapping[str, float]) -> Callable[[Dict[str, Any]], float]:
    return lambda row: float(penalties.get(inference_profile(str(row.get("query", ""))), 0.0))


def mixture_weights(rows: Sequence[Dict[str, Any]], group: str) -> List[float]:
    if not rows:
        return []
    if group != "aggregate":
        return [1 / len(rows)] * len(rows)
    cell_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    levels_by_suite: Dict[str, set[str]] = defaultdict(set)
    for row in rows:
        key = (str(row.get("dimension_id")), str(row.get("level")))
        cell_counts[key] += 1
        levels_by_suite[key[0]].add(key[1])
    suites = sorted(levels_by_suite)
    weights = []
    for row in rows:
        suite, level = str(row.get("dimension_id")), str(row.get("level"))
        weight = 1 / (len(suites) * len(levels_by_suite[suite]) * cell_counts[(suite, level)])
        weights.append(weight)
    return weights


def risk_interval(
    rows: Sequence[Dict[str, Any]],
    losses: Sequence[int],
    group: str,
    alpha: float,
) -> Tuple[float, float, float, float, str, int]:
    if not rows:
        return 0.0, 0.0, 1.0, 0.0, "empty", 0
    weights = mixture_weights(rows, group)
    risk = sum(weight * loss for weight, loss in zip(weights, losses))
    clusters: Dict[Tuple[str, str], List[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        clusters[(str(row.get("run_id", "")), str(row.get("world_id", "")))].append(index)
    one_per_cluster = all(len(indices) == 1 for indices in clusters.values())
    equal = max(weights) - min(weights) < 1e-15
    if equal and one_per_cluster:
        k = sum(losses)
        n = len(losses)
        return (
            risk, clopper_lower(k, n, alpha), clopper_upper(k, n, alpha),
            float(n), "independent_world_exact_binomial", len(clusters),
        )
    cluster_weights = [sum(weights[index] for index in indices) for indices in clusters.values()]
    squared = sum(weight * weight for weight in cluster_weights)
    radius = math.sqrt(max(0.0, math.log(1 / max(alpha, 1e-300)) * squared / 2))
    return (
        risk, max(0.0, risk - radius), min(1.0, risk + radius),
        1 / squared, "independent_world_weighted_hoeffding", len(clusters),
    )
