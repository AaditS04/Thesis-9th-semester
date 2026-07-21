"""Executable H1-H5 confirmatory tests aligned with the CalibRead crosswalk."""

from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from .metrics import final_rows, policy_decision
from .policy import (
    HARD_GROUPS,
    evaluate_policy,
    group_rows,
    learn_profile_penalties,
    profile_adjustment,
    select_certified_threshold,
)
from .stats import (
    binomial_p_greater,
    bootstrap_cluster_mean,
    clopper_upper,
    holm_adjust,
    mean,
    monotone_lrt,
    one_sided_mean_greater,
    percentile,
)


EXPOSURES = [0, 1, 2, 4, 8, 16, 32]
H5_DIRECTIONS = [
    ("general", "biomedical"),
    ("general", "legal"),
    ("biomedical", "general"),
    ("legal", "technical"),
]


def run_hypotheses(
    rows: Sequence[Dict[str, Any]],
    links: Sequence[Dict[str, Any]],
    model_id: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    analysis = config["analysis"]
    score = analysis.get("confidence_column", "confidence_score")
    thresholds = _thresholds(analysis)
    target = float(analysis["target_false_commit_risk"])
    delta = 1 - float(analysis["calibration_confidence"])
    bootstrap = int(analysis["bootstrap_replicates"])
    permutations = int(analysis["permutation_replicates"])
    seed = int(analysis["random_seed"])
    minimum_n = int(analysis.get("minimum_group_n", 100))
    model_rows = [row for row in rows if row.get("model_id") == model_id]
    confirmatory, status_note = _confirmatory_status(model_rows, config)

    h1 = test_h1(model_rows, permutations, bootstrap, seed)
    h2 = test_h2(model_rows, links, bootstrap, seed + 1000)
    h2_independence = h2_independence_diagnostic(model_rows, links)
    h3 = test_h3(model_rows, thresholds, score, target, delta, minimum_n)
    h4 = test_h4(model_rows, thresholds, score, target, delta, bootstrap, seed + 2000, minimum_n)
    h5 = test_h5(model_rows, thresholds, score, target, delta, bootstrap, seed + 3000, minimum_n)
    results = [h1, h2, h3["result"], h4["result"], h5["result"]]
    raw = validated_primary_p_values(results)
    adjusted = holm_adjust(raw)
    for item in results:
        item["p_value_holm"] = adjusted[item["hypothesis_id"]]
        item["confirmatory"] = int(confirmatory)
        item["scientific_status_note"] = status_note
        if not confirmatory:
            item["decision"] = "NOT_CONFIRMATORY"
        else:
            item["decision"] = _decision(item)
    return {
        "results": results,
        "h1_detail": h1.pop("detail", {}),
        "h2_detail": h2.pop("detail", {}),
        "h2_independence": h2_independence,
        "h3_contracts": h3["contracts"],
        "h4_contracts": h4["contracts"],
        "h5_directions": h5["directions"],
        "h4_policy": h4["policy"],
        "h3_policy": h3["policy"],
    }


def validated_primary_p_values(
    results: Sequence[Dict[str, Any]],
) -> Dict[str, float]:
    """Preserve exact zeroes and reject non-probability hypothesis outputs."""
    raw: Dict[str, float] = {}
    for item in results:
        value = item.get("p_value_raw")
        p_value = 1.0 if value is None else float(value)
        if not math.isfinite(p_value) or not 0 <= p_value <= 1:
            raise ValueError(f"Invalid p-value for {item['hypothesis_id']}: {value!r}")
        raw[item["hypothesis_id"]] = p_value
    return raw


def test_h1(
    rows: Sequence[Dict[str, Any]],
    permutations: int,
    bootstrap: int,
    seed: int,
) -> Dict[str, Any]:
    selected = [row for row in final_rows(rows, "test") if row.get("dimension_id") == "R1"]
    clusters = _cluster_outcomes(selected, "commit_correct", factor="exposure")
    successes, totals = _exposure_counts(clusters)
    statistic, fitted = monotone_lrt(successes, totals)
    rng = random.Random(seed)
    exposure_labels = [item[1] for item in clusters]
    outcomes = [item[2] for item in clusters]
    exceed = 0
    for _ in range(permutations):
        permuted = exposure_labels[:]
        rng.shuffle(permuted)
        trial = [(str(index), exposure, outcome) for index, (exposure, outcome) in enumerate(zip(permuted, outcomes))]
        trial_success, trial_total = _exposure_counts(trial)
        trial_stat, _ = monotone_lrt(trial_success, trial_total)
        exceed += int(trial_stat >= statistic - 1e-12)
    p_value = (exceed + 1) / (permutations + 1)
    by_exposure: Dict[int, List[float]] = defaultdict(list)
    for _, exposure, outcome in clusters:
        by_exposure[int(exposure)].append(float(outcome))
    rng = random.Random(seed + 1)
    differences = []
    low_values, high_values = by_exposure[1], by_exposure[16]
    for _ in range(bootstrap):
        low = mean([low_values[rng.randrange(len(low_values))] for _ in low_values]) if low_values else float("nan")
        high = mean([high_values[rng.randrange(len(high_values))] for _ in high_values]) if high_values else float("nan")
        differences.append(high - low)
    effect = mean(high_values) - mean(low_values) if high_values and low_values else float("nan")
    lower_one_sided = percentile(differences, 0.05)
    upper = percentile(differences, 0.95)
    return {
        "hypothesis_id": "H1",
        "primary_endpoint": "one-sided monotone exposure omnibus",
        "preregistered_margin": 0.05,
        "effect_definition": "accuracy(exposure=16)-accuracy(exposure=1)",
        "effect_estimate": effect,
        "ci_low": lower_one_sided,
        "ci_high": upper,
        "p_value_raw": p_value,
        "success_condition_met": int(p_value < 0.05 and lower_one_sided > 0.05),
        "model_formula": "isotonic Bernoulli likelihood-ratio with exposure-label permutation; fact clusters",
        "n_worlds": len(clusters),
        "n_queries": len(selected),
        "detail": {
            "exposures": EXPOSURES,
            "successes": successes,
            "totals": totals,
            "fitted_monotone_accuracy": fitted,
            "lrt_statistic": statistic,
            "permutations": permutations,
            "practical_lower_one_sided_95": lower_one_sided,
        },
    }


def test_h2(
    rows: Sequence[Dict[str, Any]],
    links: Sequence[Dict[str, Any]],
    bootstrap: int,
    seed: int,
) -> Dict[str, Any]:
    by_key = {(row.get("run_id"), row.get("observation_id")): row for row in rows}
    links_by_parent: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for link in links:
        links_by_parent[(link.get("run_id"), link.get("parent_testcase_id"))].append(link)
    selected = [
        row for row in final_rows(rows, "test")
        if row.get("dimension_id") == "R5" and int(row.get("factors", {}).get("hops", 1)) >= 2
    ]
    eligible = []
    by_graph: Dict[str, List[float]] = defaultdict(list)
    for row in selected:
        parent_links = links_by_parent.get((row.get("run_id"), row.get("testcase_id")), [])
        components = [by_key.get((row.get("run_id"), link.get("component_observation_id"))) for link in parent_links]
        if parent_links and all(component and component.get("commit_correct") for component in components):
            error = 1.0 - float(row.get("commit_correct", 0))
            eligible.append(row)
            by_graph[_cluster(row)].append(error)
    boot = bootstrap_cluster_mean(by_graph, bootstrap, seed) if by_graph else []
    estimate = mean([value for values in by_graph.values() for value in values]) if by_graph else float("nan")
    p_value = (
        (1 + sum((value - estimate) >= (estimate - 0.05) for value in boot)) / (len(boot) + 1)
        if boot else 1.0
    )
    low = percentile(boot, 0.05) if boot else float("nan")
    high = percentile(boot, 0.95) if boot else float("nan")
    return {
        "hypothesis_id": "H2",
        "primary_endpoint": "conditional composition error at depths 2-5",
        "preregistered_margin": 0.05,
        "effect_definition": "P(final error | all required component probes correct)-0.05",
        "effect_estimate": estimate - 0.05 if by_graph else None,
        "ci_low": low - 0.05 if by_graph else None,
        "ci_high": high - 0.05 if by_graph else None,
        "p_value_raw": p_value,
        "success_condition_met": int(bool(by_graph) and p_value < 0.05 and low > 0.05),
        "model_formula": "one-sided graph-cluster mean test and graph bootstrap",
        "n_worlds": len(by_graph),
        "n_queries": len(eligible),
        "detail": {
            "eligible_graph_depth_rows": len(eligible),
            "all_candidate_rows": len(selected),
            "conditional_error": estimate,
            "warning": "The independence-product diagnostic is intentionally not applied inside this conditioned subset.",
        },
    }


def test_h3(
    rows: Sequence[Dict[str, Any]],
    thresholds: Sequence[float],
    score: str,
    target: float,
    delta: float,
    minimum_n: int,
) -> Dict[str, Any]:
    calibration = [row for row in final_rows(rows, "calibrate") if row.get("dimension_id") in {f"R{i}" for i in range(1, 7)}]
    test = [row for row in final_rows(rows, "test") if row.get("dimension_id") in {f"R{i}" for i in range(1, 7)}]
    policy = select_certified_threshold(calibration, thresholds, score, target, delta, ["aggregate"], minimum_n=minimum_n)
    if not policy["supported"]:
        return {"result": _unsupported("H3", "No aggregate-only policy certified on calibration"), "contracts": [], "policy": policy}
    contracts = evaluate_policy(test, float(policy["threshold"]), score, ["aggregate"], delta)
    contracts.extend(evaluate_policy(test, float(policy["threshold"]), score, HARD_GROUPS[1:], delta))
    aggregate = next(item for item in contracts if item["group_id"] == "aggregate")
    hard = [item for item in contracts if item["group_id"] != "aggregate"]
    worst = max(hard, key=lambda item: item["false_commit_risk"])
    group_p = [binomial_p_greater(item["losses"], item["n"], target + 0.02) for item in hard]
    p_value = min(1.0, min(group_p, default=1.0) * len(hard))
    aggregate_gate = aggregate["risk_ucb"] <= target
    lower_gap = max(item["risk_lcb"] for item in hard) - target
    upper_gap = max(item["risk_ucb"] for item in hard) - target
    result = {
        "hypothesis_id": "H3",
        "primary_endpoint": "maximum hard-group false-commit excess",
        "preregistered_margin": 0.02,
        "effect_definition": "max_g R_fc,g - 0.05 after aggregate-only policy",
        "effect_estimate": worst["false_commit_risk"] - target,
        "ci_low": lower_gap,
        "ci_high": upper_gap,
        "p_value_raw": p_value if aggregate_gate else 1.0,
        "success_condition_met": int(aggregate_gate and lower_gap > 0.02 and p_value < 0.05),
        "model_formula": "aggregate calibration; independent-world simultaneous hard-group bounds",
        "n_worlds": len({_cluster(row) for row in test}),
        "n_queries": len(test),
        "notes": f"worst_group={worst['group_id']}; aggregate_ucb={aggregate['risk_ucb']:.6f}",
    }
    return {"result": result, "contracts": contracts, "policy": policy}


def h2_independence_diagnostic(
    rows: Sequence[Dict[str, Any]],
    links: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """All-graphs, leave-one-graph component-product diagnostic (never primary H2)."""
    scored = {(row.get("run_id"), row.get("observation_id")): row for row in rows}
    links_by_parent: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    signature_values: Dict[Tuple[int, int, str], Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    finals = [
        row for row in final_rows(rows, "test")
        if row.get("dimension_id") == "R5" and int(row.get("factors", {}).get("hops", 1)) >= 2
    ]
    for link in links:
        key = (link.get("run_id"), link.get("parent_testcase_id"))
        links_by_parent[key].append(link)
    for final in finals:
        depth = int(final.get("factors", {}).get("hops", 1))
        graph = _cluster(final)
        for link in links_by_parent.get((final.get("run_id"), final.get("testcase_id")), []):
            component = scored.get((final.get("run_id"), link.get("component_observation_id")))
            query_type = "designation" if "designation" in str(link.get("component_query", "")).casefold() else "link"
            signature = (depth, int(link.get("component_index") or 0), query_type)
            if component:
                signature_values[signature][graph].append(float(component.get("commit_correct", 0)))
    depth_rows: Dict[int, List[Tuple[float, float]]] = defaultdict(list)
    for final in finals:
        depth = int(final.get("factors", {}).get("hops", 1))
        graph = _cluster(final)
        probabilities = []
        for link in links_by_parent.get((final.get("run_id"), final.get("testcase_id")), []):
            query_type = "designation" if "designation" in str(link.get("component_query", "")).casefold() else "link"
            signature = (depth, int(link.get("component_index") or 0), query_type)
            other = [
                value for other_graph, values in signature_values.get(signature, {}).items()
                if other_graph != graph for value in values
            ]
            probabilities.append((sum(other) + 1) / (len(other) + 2) if other else 0.5)
        if probabilities:
            predicted_error = 1.0 - math.prod(probabilities)
            observed_error = 1.0 - float(final.get("commit_correct", 0))
            depth_rows[depth].append((observed_error, predicted_error))
    output = []
    for depth, values in sorted(depth_rows.items()):
        observed = mean([item[0] for item in values])
        predicted = mean([item[1] for item in values])
        output.append({
            "depth": depth, "n_graph_depth_rows": len(values),
            "observed_final_error": observed, "cross_fitted_independence_error": predicted,
            "residual_observed_minus_independence": observed - predicted,
            "confirmatory": 0,
            "estimand": "all graphs; graph-excluded component-product reference",
        })
    return output


def test_h4(
    rows: Sequence[Dict[str, Any]],
    thresholds: Sequence[float],
    score: str,
    target: float,
    delta: float,
    bootstrap: int,
    seed: int,
    minimum_n: int,
) -> Dict[str, Any]:
    development = [row for row in final_rows(rows) if row.get("split") in {"fit", "tune"} and row.get("dimension_id") in {f"R{i}" for i in range(1, 7)}]
    calibration = [row for row in final_rows(rows, "calibrate") if row.get("dimension_id") in {f"R{i}" for i in range(1, 7)}]
    test = [row for row in final_rows(rows, "test") if row.get("dimension_id") in {f"R{i}" for i in range(1, 7)}]
    penalties = learn_profile_penalties(development, score)
    adjustment = profile_adjustment(penalties)
    global_policy = select_certified_threshold(calibration, thresholds, score, target, delta, HARD_GROUPS, minimum_n=minimum_n)
    ccrc_policy = select_certified_threshold(calibration, thresholds, score, target, delta, HARD_GROUPS, adjustment, minimum_n)
    contracts = []
    if global_policy["supported"]:
        contracts.extend({"policy_id": "global_joint_safe", **item} for item in evaluate_policy(test, global_policy["threshold"], score, HARD_GROUPS, delta))
    if ccrc_policy["supported"]:
        contracts.extend({"policy_id": "predicted_profile_ccrc", **item} for item in evaluate_policy(test, ccrc_policy["threshold"], score, HARD_GROUPS, delta, adjustment))
    if not global_policy["supported"] or not ccrc_policy["supported"]:
        return {
            "result": _unsupported("H4", "One or both joint-safe policies were unsupported"),
            "contracts": contracts,
            "policy": {"global": global_policy, "ccrc": ccrc_policy, "profile_penalties": penalties},
        }
    by_world: Dict[str, List[float]] = defaultdict(list)
    difference_rows = []
    for row in test:
        global_commit = policy_decision(row, global_policy["threshold"], score)[0]
        ccrc_commit = policy_decision(row, ccrc_policy["threshold"], score, adjustment(row))[0]
        difference = float(ccrc_commit - global_commit)
        by_world[_cluster(row)].append(difference)
        difference_rows.append((row, difference))
    effect, boot = _mixture_bootstrap(difference_rows, bootstrap, seed)
    centered_excess = effect - 0.03
    p_value = (1 + sum((value - effect) >= centered_excess for value in boot)) / (len(boot) + 1)
    low = percentile(boot, 0.05)
    high = percentile(boot, 0.95)
    result = {
        "hypothesis_id": "H4",
        "primary_endpoint": "predicted-profile CCRC answer-coverage gain",
        "preregistered_margin": 0.03,
        "effect_definition": "coverage(CCRC)-coverage(global joint-safe)",
        "effect_estimate": effect,
        "ci_low": low,
        "ci_high": high,
        "p_value_raw": p_value,
        "success_condition_met": int(p_value < 0.05 and low > 0.03),
        "model_formula": "paired world-cluster comparison after common 14-scope calibration gate",
        "n_worlds": len(by_world),
        "n_queries": len(test),
        "notes": json.dumps({"profile_penalties": penalties}, sort_keys=True),
    }
    return {
        "result": result,
        "contracts": contracts,
        "policy": {"global": global_policy, "ccrc": ccrc_policy, "profile_penalties": penalties},
    }


def test_h5(
    rows: Sequence[Dict[str, Any]],
    thresholds: Sequence[float],
    score: str,
    target: float,
    delta: float,
    bootstrap: int,
    seed: int,
    minimum_n: int,
) -> Dict[str, Any]:
    calibration = [row for row in final_rows(rows, "calibrate") if row.get("dimension_id") == "R6"]
    test = [row for row in final_rows(rows, "test") if row.get("dimension_id") == "R6"]
    by_cal_domain = {domain: [row for row in calibration if row.get("level") == domain] for domain in ("general", "biomedical", "legal", "technical")}
    by_test_domain = {domain: [row for row in test if row.get("level") == domain] for domain in ("general", "biomedical", "legal", "technical")}
    policies = {
        domain: select_certified_threshold(values, thresholds, score, target, delta, ["aggregate"], minimum_n=minimum_n)
        for domain, values in by_cal_domain.items()
    }
    directions = []
    direction_p = []
    for index, (source, target_domain) in enumerate(H5_DIRECTIONS):
        source_policy, within_policy = policies[source], policies[target_domain]
        target_rows = by_test_domain[target_domain]
        if not source_policy["supported"] or not within_policy["supported"] or not target_rows:
            directions.append({"source": source, "target": target_domain, "supported": False})
            direction_p.append(1.0)
            continue
        by_world: Dict[str, List[float]] = defaultdict(list)
        cross_losses = []
        within_losses = []
        for row in target_rows:
            cross_loss = policy_decision(row, source_policy["threshold"], score)[1]
            within_loss = policy_decision(row, within_policy["threshold"], score)[1]
            cross_losses.append(cross_loss)
            within_losses.append(within_loss)
            by_world[_cluster(row)].append(float(cross_loss - within_loss))
        world_values = [mean(values) for values in by_world.values()]
        _, p_value = one_sided_mean_greater(world_values, 0.02)
        boot = bootstrap_cluster_mean(by_world, bootstrap, seed + index)
        simultaneous_tail = delta / len(H5_DIRECTIONS)
        gap = mean(cross_losses) - mean(within_losses)
        detail = {
            "source": source, "target": target_domain, "supported": True,
            "source_threshold": source_policy["threshold"], "within_threshold": within_policy["threshold"],
            "n": len(target_rows), "cross_risk": mean(cross_losses), "within_risk": mean(within_losses),
            "gap": gap, "simultaneous_ci_low": percentile(boot, simultaneous_tail),
            "simultaneous_ci_high": percentile(boot, 1 - simultaneous_tail), "p_value_margin_0.02": p_value,
        }
        directions.append(detail)
        direction_p.append(p_value)
    supported = [item for item in directions if item.get("supported")]
    if not supported:
        return {"result": _unsupported("H5", "No source/target direction had supported calibration policies"), "directions": directions}
    worst = max(supported, key=lambda item: item["gap"])
    p_value = min(1.0, min(direction_p) * len(H5_DIRECTIONS))
    lower = max(item["simultaneous_ci_low"] for item in supported)
    upper = max(item["simultaneous_ci_high"] for item in supported)
    result = {
        "hypothesis_id": "H5",
        "primary_endpoint": "maximum cross-minus-within domain false-commit gap",
        "preregistered_margin": 0.02,
        "effect_definition": "max_(s,t)[R_fc(s->t)-R_fc(t->t)]",
        "effect_estimate": worst["gap"],
        "ci_low": lower,
        "ci_high": upper,
        "p_value_raw": p_value,
        "success_condition_met": int(p_value < 0.05 and lower > 0.02),
        "model_formula": "four prespecified source-target calibrations; paired query gaps; Bonferroni union test",
        "n_worlds": len({_cluster(row) for row in test}),
        "n_queries": len(test),
        "notes": f"max_direction={worst['source']}->{worst['target']}",
    }
    return {"result": result, "directions": directions}


def _cluster_outcomes(
    rows: Sequence[Dict[str, Any]],
    outcome: str,
    factor: str,
) -> List[Tuple[str, int, float]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("world_id", "")].append(row)
    output = []
    for world, values in grouped.items():
        output.append((world, int(values[0].get("factors", {}).get(factor, 0)), mean([float(item[outcome]) for item in values])))
    return output


def _exposure_counts(clusters: Sequence[Tuple[str, int, float]]) -> Tuple[List[float], List[float]]:
    successes = []
    totals = []
    for exposure in EXPOSURES:
        values = [outcome for _, level, outcome in clusters if int(level) == exposure]
        successes.append(sum(values))
        totals.append(float(len(values)))
    return successes, totals


def _cluster(row: Dict[str, Any]) -> str:
    return f"{row.get('run_id','')}|{row.get('world_id','')}"


def _mixture_bootstrap(
    rows_and_values: Sequence[Tuple[Dict[str, Any], float]],
    replicates: int,
    seed: int,
) -> Tuple[float, List[float]]:
    cells: Dict[Tuple[str, str], Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    for row, value in rows_and_values:
        cells[(str(row.get("dimension_id")), str(row.get("level")))][_cluster(row)].append(value)
    suites: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for cell in cells:
        suites[cell[0]].append(cell)

    def combine(sampled: Dict[Tuple[str, str], float]) -> float:
        suite_means = []
        for suite in sorted(suites):
            suite_means.append(mean([sampled[cell] for cell in suites[suite]]))
        return mean(suite_means)

    observed_cells = {
        cell: mean([value for values in clusters.values() for value in values])
        for cell, clusters in cells.items()
    }
    observed = combine(observed_cells)
    cluster_rows: Dict[Tuple[str, str], List[Tuple[Tuple[str, str], float]]] = defaultdict(list)
    for row, value in rows_and_values:
        cluster_rows[(str(row.get("dimension_id")), _cluster(row))].append(
            ((str(row.get("dimension_id")), str(row.get("level"))), value)
        )
    strata: Dict[Tuple[str, Tuple[str, ...]], List[Tuple[str, str]]] = defaultdict(list)
    for cluster, values in cluster_rows.items():
        signature = tuple(sorted({cell[1] for cell, _ in values}))
        strata[(cluster[0], signature)].append(cluster)

    rng = random.Random(seed)
    boot = []
    for _ in range(replicates):
        sampled_values: Dict[Tuple[str, str], List[float]] = defaultdict(list)
        for stratum in sorted(strata):
            keys = sorted(strata[stratum])
            sampled = [keys[rng.randrange(len(keys))] for _ in keys]
            for key in sampled:
                for cell, value in cluster_rows[key]:
                    sampled_values[cell].append(value)
        sampled_cells = {cell: mean(values) for cell, values in sampled_values.items()}
        boot.append(combine(sampled_cells))
    return observed, boot


def _thresholds(analysis: Mapping[str, Any]) -> List[float]:
    start = float(analysis.get("threshold_start", 0))
    stop = float(analysis.get("threshold_stop", 1))
    step = float(analysis.get("threshold_step", 0.01))
    return [round(start + index * step, 10) for index in range(int(round((stop - start) / step)) + 1)]


def _confirmatory_status(rows: Sequence[Dict[str, Any]], config: Dict[str, Any]) -> Tuple[bool, str]:
    if config.get("confirmatory", {}).get("allow_incomplete_exploratory", False):
        return (
            False,
            "NONCONFIRMATORY_INCOMPLETE_INPUT: exploratory incomplete-input "
            "mode; confirmatory decisions disabled",
        )
    required = bool(config.get("confirmatory", {}).get("require_parametric_status", True))
    allowed = set(config.get("confirmatory", {}).get("allowed_statuses", ["confirmatory_parametric"]))
    statuses = {str(row.get("scientific_status", "")) for row in rows}
    if not required:
        return True, f"status requirement disabled; observed={sorted(statuses)}"
    valid = bool(statuses) and statuses <= allowed
    return valid, f"observed={sorted(statuses)}; allowed={sorted(allowed)}"


def _unsupported(hypothesis: str, note: str) -> Dict[str, Any]:
    return {
        "hypothesis_id": hypothesis,
        "primary_endpoint": "unsupported",
        "preregistered_margin": None,
        "effect_definition": "unsupported",
        "effect_estimate": None,
        "ci_low": None,
        "ci_high": None,
        "p_value_raw": 1.0,
        "success_condition_met": 0,
        "model_formula": "unsupported",
        "n_worlds": 0,
        "n_queries": 0,
        "notes": note,
    }


def _decision(item: Dict[str, Any]) -> str:
    if item.get("primary_endpoint") == "unsupported":
        return "UNSUPPORTED"
    return "SUPPORTED" if item.get("success_condition_met") and float(item.get("p_value_holm", 1)) < 0.05 else "NOT_SUPPORTED"
