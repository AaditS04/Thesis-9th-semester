"""Auxiliary suite diagnostics, error taxonomy, and operational-cost summaries."""

from __future__ import annotations

import json
import random
from itertools import combinations
from collections import defaultdict
from typing import Any, Dict, List, Sequence, Tuple

from .stats import mean


def confidence_feature_availability(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(
            str(row.get("model_id")), str(row.get("provider_returned")),
            str(row.get("dimension_id")), str(row.get("split")),
            str(row.get("confidence_method")),
        )].append(row)
    output = []
    for key, group in sorted(grouped.items()):
        available = sum(int(row.get("confidence_available", row.get("confidence_score") is not None)) for row in group)
        output.append({
            "model_id": key[0], "provider_returned": key[1], "dimension_id": key[2],
            "split": key[3], "confidence_method": key[4], "n": len(group),
            "available": available, "availability_rate": available / len(group) if group else None,
        })
    return output


def r0_gate_summary(rows: Sequence[Dict[str, Any]], gate_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    selected = [
        row for row in rows
        if row.get("dimension_id") == "R0" and row.get("observation_kind") == "final"
        and row.get("split") in {"fit", "tune", "calibrate"}
    ]
    grouped: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in selected:
        grouped[(str(row.get("model_id")), str(row.get("checkpoint_stage")), str(row.get("level")))].append(row)
    preliminary = []
    checkpoint_rates: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(dict)
    direct_min = float(gate_config.get("known_direct_min", 0.70))
    loss_max = float(gate_config.get("direct_to_paraphrase_max_loss", 0.20))
    manual = dict(gate_config.get("manual_grading_agreement", {}))
    no_split_crossing = gate_config.get("no_split_crossing") is True
    for (model, stage, level), group in sorted(grouped.items()):
        outcome = "commit_correct" if level in {"known_direct", "known_paraphrase"} else "action_correct"
        successes = sum(int(row.get(outcome, 0)) for row in group)
        rate = successes / len(group) if group else None
        checkpoint_rates[(model, stage)][level] = rate
        preliminary.append({
            "model_id": model, "checkpoint_stage": stage,
            "split_scope": "fit+tune+calibrate development only", "level": level,
            "n": len(group), "successes": successes, "success_rate": rate,
            "minimum_required": direct_min if level == "known_direct" else None,
            "passed": int(rate > direct_min) if level == "known_direct" and rate is not None else None,
        })
    for row in preliminary:
        key = (row["model_id"], row["checkpoint_stage"])
        rates = checkpoint_rates[key]
        direct = rates.get("known_direct")
        paraphrase = rates.get("known_paraphrase")
        loss = None if direct is None or paraphrase is None else direct - paraphrase
        manual_value = manual.get(f"{key[0]}|{key[1]}")
        gate_passed = bool(
            len(rates) == 4 and direct is not None and direct > direct_min
            and loss is not None and loss < loss_max
            and manual_value is not None and float(manual_value) >= 0.98
            and no_split_crossing
        )
        row["direct_to_paraphrase_loss"] = loss
        row["direct_to_paraphrase_max_loss"] = loss_max
        row["manual_grading_agreement"] = manual_value
        row["no_split_crossing_attested"] = int(no_split_crossing)
        row["checkpoint_gate_passed"] = int(gate_passed)
    return preliminary


def auxiliary_metrics(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("observation_kind") == "final":
            continue
        grouped[(
            str(row.get("model_id")), str(row.get("dimension_id")), str(row.get("level")),
            str(row.get("split")), str(row.get("observation_kind")),
        )].append(row)
    output = []
    for (model, dimension, level, split, kind), group in sorted(grouped.items()):
        output.append({
            "model_id": model, "dimension_id": dimension, "level": level, "split": split,
            "observation_kind": kind, "n": len(group),
            "factual_accuracy": mean([float(row.get("factual_correct", 0)) for row in group]),
            "action_accuracy": mean([float(row.get("action_correct", 0)) for row in group]),
            "commit_accuracy": mean([float(row.get("commit_correct", 0)) for row in group]),
            "mean_confidence": mean([float(row.get("confidence_score") or 0) for row in group]),
        })
    return output


def clarification_recovery_summary(
    rows: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("observation_kind") == "clarification":
            grouped[(
                str(row.get("model_id")),
                str(row.get("level")),
                str(row.get("split")),
            )].append(row)
    output = []
    for (model, level, split), group in sorted(grouped.items()):
        forced = sum(int(row.get("forced_clarification_recovery") or 0) for row in group)
        end_to_end = sum(
            int(row.get("end_to_end_clarification_success") or 0)
            for row in group
        )
        output.append({
            "model_id": model,
            "level": level,
            "split": split,
            "n_forced_second_turns": len(group),
            "forced_recovery_successes": forced,
            "forced_clarification_recovery_rate": forced / len(group),
            "end_to_end_successes": end_to_end,
            "end_to_end_clarification_success_rate": end_to_end / len(group),
            "interpretation": (
                "forced recovery supplies a choice regardless of first action; "
                "end-to-end requires a valid first-turn CLARIFY"
            ),
        })
    return output


def error_taxonomy(
    rows: Sequence[Dict[str, Any]],
    links: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    scored = {(row.get("run_id"), row.get("observation_id")): row for row in rows}
    links_by_parent: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for link in links:
        links_by_parent[(link.get("run_id"), link.get("parent_testcase_id"))].append(link)
    counts: Dict[Tuple[str, str, str], int] = defaultdict(int)
    denominators: Dict[Tuple[str, str], int] = defaultdict(int)
    for row in rows:
        if row.get("observation_kind") != "final" or row.get("split") != "test":
            continue
        if row.get("commit_correct") or (not row.get("answer_attempted") and row.get("action_correct")):
            continue
        model, dimension = str(row.get("model_id")), str(row.get("dimension_id"))
        denominators[(model, dimension)] += 1
        code = _error_code(row, scored, links_by_parent)
        counts[(model, dimension, code)] += 1
    output = []
    for (model, dimension, code), count in sorted(counts.items()):
        denominator = denominators[(model, dimension)]
        output.append({
            "model_id": model, "dimension_id": dimension, "error_code": code,
            "count": count, "error_denominator": denominator,
            "fraction_of_errors": count / denominator if denominator else 0.0,
            "sampling_note": "automatic full-test taxonomy; validate with the frozen blinded audit",
        })
    return output


def cost_summary(raw_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in raw_rows:
        grouped[(
            str(row.get("model_requested")), str(row.get("analysis_role") or "primary"),
            str(row.get("checkpoint_stage") or "unspecified"), str(row.get("dimension_id")),
            str(row.get("split")),
        )].append(row)
    output = []
    for (model, role, stage, dimension, split), group in sorted(grouped.items()):
        success = [row for row in group if row.get("status") == "success"]
        output.append({
            "model_id": model, "analysis_role": role, "checkpoint_stage": stage,
            "dimension_id": dimension, "split": split,
            "requests": len(group), "successful_requests": len(success),
            "failed_requests": len(group) - len(success),
            "input_tokens": sum(_number(row.get("input_tokens")) for row in success),
            "output_tokens": sum(_number(row.get("output_tokens")) for row in success),
            "cost_credits": sum(_number(row.get("cost_credits")) for row in success),
            "mean_latency_ms": mean([_number(row.get("latency_ms")) for row in success]),
        })
    return output


def temporal_checkpoint_diagnostics(
    rows: Sequence[Dict[str, Any]],
    replicates: int,
    seed: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    temporal = [
        row for row in rows
        if row.get("observation_kind") == "final" and row.get("dimension_id") == "R3"
    ]
    grouped: Dict[Tuple[str, str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in temporal:
        outcome = _temporal_outcome(row)
        grouped[(
            str(row.get("model_id")), str(row.get("analysis_role")),
            str(row.get("checkpoint_stage")), str(row.get("level")), str(row.get("split")),
        )].append({**row, "_temporal_outcome": outcome})
    confusion = []
    outcomes = ("current", "stale", "abstain", "other_wrong_action_or_value")
    for key, group in sorted(grouped.items()):
        model, role, stage, level, split = key
        for outcome in outcomes:
            count = sum(row["_temporal_outcome"] == outcome for row in group)
            confusion.append({
                "model_id": model, "analysis_role": role, "checkpoint_stage": stage,
                "level": level, "split": split, "outcome": outcome,
                "count": count, "n": len(group), "rate": count / len(group) if group else None,
            })

    pair_groups: Dict[Tuple[str, str], Dict[str, Dict[str, Dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(dict))
    )
    for row in temporal:
        if row.get("level") != "current_after_update":
            continue
        stage = str(row.get("checkpoint_stage", "")).casefold()
        if stage not in {"checkpoint_t0", "checkpoint_t2", "t0", "t2"}:
            continue
        canonical_stage = "T0" if stage.endswith("t0") else "T2"
        pair_groups[(str(row.get("model_id")), str(row.get("split")))][str(row.get("world_id"))][canonical_stage] = row
    paired = []
    for (model, split), worlds in sorted(pair_groups.items()):
        pairs = [stages for stages in worlds.values() if {"T0", "T2"} <= set(stages)]
        if not pairs:
            continue
        current_t0 = [float(item["T0"].get("commit_correct", 0)) for item in pairs]
        current_t2 = [float(item["T2"].get("commit_correct", 0)) for item in pairs]
        stale_t0 = [float(item["T0"].get("stale_answer", 0)) for item in pairs]
        stale_t2 = [float(item["T2"].get("stale_answer", 0)) for item in pairs]
        differences = [right - left for left, right in zip(current_t0, current_t2)]
        stale_differences = [right - left for left, right in zip(stale_t0, stale_t2)]
        rng = random.Random(f"{seed}|{model}|{split}")
        boot = []
        stale_boot = []
        for _ in range(replicates):
            sampled = [rng.randrange(len(pairs)) for _ in pairs]
            boot.append(mean([differences[index] for index in sampled]))
            stale_boot.append(mean([stale_differences[index] for index in sampled]))
        paired.append({
            "model_id": model, "split": split, "n_pairs": len(pairs),
            "t0_current_accuracy": mean(current_t0), "t2_current_accuracy": mean(current_t2),
            "current_accuracy_gain": mean(differences),
            "current_gain_ci_low": _percentile(boot, 0.025), "current_gain_ci_high": _percentile(boot, 0.975),
            "t0_stale_rate": mean(stale_t0), "t2_stale_rate": mean(stale_t2),
            "stale_rate_change": mean(stale_differences),
            "stale_change_ci_low": _percentile(stale_boot, 0.025), "stale_change_ci_high": _percentile(stale_boot, 0.975),
            "estimand": "paired current_after_update worlds; T2 minus T0",
        })
    return confusion, paired


def repeatability_summary(raw_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in raw_rows:
        if row.get("status") == "success" and row.get("sample_kind") in {"greedy", "greedy_repeat"}:
            grouped[(
                str(row.get("model_requested")), str(row.get("analysis_role") or "primary"),
                str(row.get("checkpoint_stage") or "unspecified"), str(row.get("observation_id")),
            )].append(row)
    aggregate: Dict[Tuple[str, str, str, str], List[Tuple[int, int, int, int, int, float]]] = defaultdict(list)
    for (model, role, stage, _), group in grouped.items():
        baseline = next((row for row in group if row.get("sample_kind") == "greedy"), None)
        repeats = [row for row in group if row.get("sample_kind") == "greedy_repeat"]
        if baseline is None or not repeats:
            continue
        raw = str(baseline.get("raw_output", ""))
        parsed = _canonical_json(raw)
        exact_match = int(all(str(row.get("raw_output", "")) == raw for row in repeats))
        parsed_match = int(all(_canonical_json(str(row.get("raw_output", ""))) == parsed for row in repeats))
        frozen_fields = ("request_seed", "temperature", "top_p", "max_completion_tokens", "model_requested", "messages_sha256")
        identical_parameters = int(all(
            all(row.get(field) == baseline.get(field) for field in frozen_fields)
            for row in repeats
        ))
        backend_fields = ("model_returned", "provider_returned", "system_fingerprint")
        same_backend = int(all(
            all(row.get(field) == baseline.get(field) for field in backend_fields)
            for row in repeats
        ))
        fingerprint_available = int(bool(baseline.get("system_fingerprint")) and all(
            bool(row.get("system_fingerprint")) for row in repeats
        ))
        all_rows = [baseline, *repeats]
        pairs = list(combinations(all_rows, 2))
        pairwise_exact = mean([
            float(left.get("raw_output", "") == right.get("raw_output", ""))
            for left, right in pairs
        ]) if pairs else 1.0
        aggregate[(model, role, stage, str(baseline.get("dimension_id")))].append(
            (exact_match, parsed_match, identical_parameters, same_backend, fingerprint_available, pairwise_exact)
        )
    output = []
    for (model, role, stage, dimension), values in sorted(aggregate.items()):
        output.append({
            "model_id": model, "analysis_role": role, "checkpoint_stage": stage,
            "dimension_id": dimension, "n_observations": len(values),
            "all_repeats_exactly_identical_rate": mean([value[0] for value in values]),
            "parsed_repeatability_rate": mean([value[1] for value in values]),
            "identical_seed_and_parameters_rate": mean([value[2] for value in values]),
            "same_model_provider_fingerprint_rate": mean([value[3] for value in values]),
            "fingerprint_available_rate": mean([value[4] for value in values]),
            "pairwise_exact_agreement": mean([value[5] for value in values]),
        })
    return output


def _error_code(
    row: Dict[str, Any],
    scored: Dict[Tuple[Any, Any], Dict[str, Any]],
    links: Dict[Tuple[str, str], List[Dict[str, Any]]],
) -> str:
    if row.get("parser_status") != "ok":
        return "formatting_or_parser"
    if row.get("stale_answer"):
        return "stale_value"
    dimension = row.get("dimension_id")
    if dimension == "R4" and row.get("answer_attempted") and row.get("expected_action") == "CLARIFY":
        return "ambiguity_forced_answer"
    if dimension == "R2":
        return "precision_or_rounding"
    if dimension == "R5":
        parent_links = links.get((row.get("run_id"), row.get("testcase_id")), [])
        components = [scored.get((row.get("run_id"), link.get("component_observation_id"))) for link in parent_links]
        if components and all(component and component.get("commit_correct") for component in components):
            return "synthesis_composition_failure"
        return "component_fact_unavailable"
    if not row.get("answer_attempted") and row.get("expected_action") == "ANSWER":
        return "refusal_or_abstention_despite_known"
    if row.get("answer_attempted"):
        return "wrong_entity_or_value"
    return "wrong_action"


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _temporal_outcome(row: Dict[str, Any]) -> str:
    if row.get("stale_answer"):
        return "stale"
    if row.get("parsed_action") == "ANSWER" and row.get("commit_correct"):
        return "current"
    if row.get("parsed_action") == "ABSTAIN":
        return "abstain"
    return "other_wrong_action_or_value"


def _percentile(values: Sequence[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(len(ordered) - 1, lower + 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _canonical_json(text: str) -> str:
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return json.dumps({
                "action": value.get("action"), "answer": value.get("answer"),
                "clarification": value.get("clarification"),
            }, sort_keys=True, separators=(",", ":"))
    except json.JSONDecodeError:
        pass
    return text.strip()
