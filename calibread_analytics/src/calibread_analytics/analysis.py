"""End-to-end paper analysis orchestration."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .cpr import (
    IsotonicCalibrator, calibrated_read_pairs, conformal_rank_cutoff,
    cpr_subgroup_summary, evaluate_cpr,
)
from .data import sha256_file, write_csv, write_json
from .diagnostics import (
    auxiliary_metrics,
    clarification_recovery_summary,
    cost_summary,
    error_taxonomy,
    repeatability_summary,
    r0_gate_summary,
    confidence_feature_availability,
    temporal_checkpoint_diagnostics,
)
from .hypotheses import run_hypotheses
from .metrics import (
    aggregate_metrics,
    calibration_summary,
    confidence_quality,
    final_rows,
    hallucination_index,
    reliability_table,
    risk_coverage_curve,
    thresholds_from_config,
)
from .plots import (
    calibration_figure,
    cpr_figure,
    domain_transfer_figure,
    error_taxonomy_figure,
    h_complexity_figure,
    hard_group_figure,
    hypothesis_figure,
    risk_coverage_figure,
    temporal_update_figure,
)
from .policy import PROFILE_RULE_VERSION, inference_profile
from .preflight import audit_inputs
from .report import write_h_methodology, write_latex_table, write_report


H_FIELDS = [
    "model_id", "dimension_id", "level", "theta_factor", "theta_value", "theta_json",
    "n_queries", "n_worlds", "n_commits", "n_false_commits", "H_false_commit",
    "H_ci_low", "H_ci_high", "H_selective", "H_factual_per_query", "answer_coverage",
    "factual_accuracy", "definition",
]

AGG_FIELDS = [
    "model_id", "dimension_id", "level", "split", "n_queries", "n_worlds", "n_commits",
    "n_false_commits", "factual_accuracy", "action_accuracy", "answer_coverage",
    "false_commit_risk", "selective_risk", "mean_confidence", "mean_latency_ms", "total_cost_credits",
]

HYPOTHESIS_FIELDS = [
    "hypothesis_id", "confirmatory", "primary_endpoint", "preregistered_margin",
    "effect_definition", "effect_estimate", "ci_low", "ci_high", "p_value_raw",
    "p_value_holm", "decision", "success_condition_met", "model_formula", "n_worlds",
    "n_queries", "scientific_status_note", "notes",
]

CONTRACT_FIELDS = [
    "policy_id", "group_id", "n", "n_clusters", "effective_n", "commits", "losses", "answer_coverage",
    "false_commit_risk", "risk_lcb", "risk_ucb", "bound_method", "simultaneous_alpha",
]


def run_analysis(config: Dict[str, Any]) -> Dict[str, Any]:
    """Build into an isolated staging directory and publish atomically."""
    final_output = Path(config["output_dir"])
    if final_output.exists():
        raise ValueError(f"Analysis output must not already exist: {final_output}")
    final_output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{final_output.name}.staging-", dir=final_output.parent))
    staged = deepcopy(config)
    staged["output_dir"] = str(staging)
    staged["_published_output_dir"] = str(final_output)
    try:
        result = _run_analysis(staged)
        os.replace(staging, final_output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    result["output_dir"] = str(final_output)
    return result


def _run_analysis(config: Dict[str, Any]) -> Dict[str, Any]:
    artifacts, input_audit, source_audit = audit_inputs(config)
    all_rows = artifacts["scored"]
    exploratory = bool(config.get("confirmatory", {}).get("allow_incomplete_exploratory", False))
    analysis_output_status = (
        "NONCONFIRMATORY_INCOMPLETE_INPUT"
        if exploratory else "CONFIRMATORY_STRICT_INPUT_ACCEPTED"
    )
    input_audit["analysis_output_status"] = analysis_output_status
    rows = [
        row for row in all_rows
        if row.get("analysis_role") == "primary"
        and (exploratory or str(row.get("checkpoint_stage", "")).casefold() == "checkpoint_t2")
        and row.get("dimension_id") in {f"R{i}" for i in range(1, 8)}
    ]
    models = sorted({str(row.get("model_id")) for row in rows})
    if not models:
        raise ValueError("No scored model rows were found")
    primary_model = config.get("primary_model_id") or models[0]
    if primary_model not in models:
        raise ValueError(f"primary_model_id {primary_model!r} is not present; found {models}")
    primary_rows = [row for row in rows if row.get("model_id") == primary_model]
    analysis = config["analysis"]
    output = Path(config["output_dir"])
    tables, figures, suites = output / "tables", output / "figures", output / "suites"
    for directory in (tables, figures, suites):
        directory.mkdir(parents=True, exist_ok=True)
    write_json(output / "input_audit.json", input_audit)
    write_json(output / "analysis_status.json", {
        "analysis_output_status": analysis_output_status,
        "confirmatory_decisions_enabled": not exploratory,
    })
    write_csv(tables / "input_audit_sources.csv", [
        "source_dir", "strict", "scored_rows", "observation_specs", "summary_expected",
        "summary_scored", "config_sha256", "scientific_bundle_sha256",
        "model_returned", "provider_returned", "system_fingerprints",
        "missing_artifacts", "source_files_sha256",
    ], source_audit)

    thresholds = thresholds_from_config(analysis)
    bootstrap = int(analysis["bootstrap_replicates"])
    seed = int(analysis["random_seed"])
    score = str(analysis.get("confidence_column", "confidence_score"))
    h_rows = hallucination_index(rows, bootstrap, seed)
    aggregate = aggregate_metrics(rows)
    risk = risk_coverage_curve(primary_rows, thresholds, score, "test")
    reliability = reliability_table(primary_rows, score, int(analysis.get("ece_bins", 10)), "test")
    calibration = calibration_summary(reliability)
    confidence = confidence_quality(primary_rows, score, int(analysis.get("ece_bins", 10)), "test")
    auxiliary = auxiliary_metrics(rows)
    clarification_recovery = clarification_recovery_summary(rows)
    errors = error_taxonomy(rows, artifacts["links"])
    costs = cost_summary(artifacts["raw"])
    repeatability = repeatability_summary(artifacts["raw"])
    feature_availability = confidence_feature_availability(rows)
    r0_gates = r0_gate_summary(
        all_rows, config.get("analysis", {}).get("r0_gate", {})
    )
    temporal_confusion, temporal_pairs = temporal_checkpoint_diagnostics(all_rows, bootstrap, seed + 5000)
    hypothesis = run_hypotheses(primary_rows, artifacts["links"], primary_model, config)
    profile_audit = _profile_assignment_audit(primary_rows, hypothesis)

    write_csv(tables / "hallucination_index.csv", H_FIELDS, h_rows)
    write_csv(tables / "aggregate_metrics.csv", AGG_FIELDS, aggregate)
    write_csv(tables / "risk_coverage.csv", [
        "model_id", "dimension_id", "split", "threshold", "n_queries", "n_commits",
        "n_false_commits", "answer_coverage", "false_commit_risk", "selective_risk",
    ], risk)
    write_csv(tables / "reliability_bins.csv", [
        "model_id", "split", "bin_index", "bin_low", "bin_high", "n", "mean_confidence",
        "empirical_correctness", "calibration_gap",
    ], reliability)
    write_csv(tables / "calibration_summary.csv", ["model_id", "n", "ece", "signed_calibration_error"], calibration)
    write_csv(tables / "confidence_quality.csv", [
        "model_id", "scope", "split", "n_commits", "accuracy", "mean_confidence",
        "brier_score", "log_loss", "ece", "mce", "roc_auc_correctness",
        "average_precision_correctness", "aurc_selective_error", "excess_aurc", "score_column",
    ], confidence)
    write_csv(tables / "auxiliary_observation_metrics.csv", [
        "model_id", "dimension_id", "level", "split", "observation_kind", "n",
        "factual_accuracy", "action_accuracy", "commit_accuracy", "mean_confidence",
    ], auxiliary)
    write_csv(tables / "clarification_recovery.csv", [
        "model_id", "level", "split", "n_forced_second_turns",
        "forced_recovery_successes", "forced_clarification_recovery_rate",
        "end_to_end_successes", "end_to_end_clarification_success_rate",
        "interpretation",
    ], clarification_recovery)
    write_csv(tables / "error_taxonomy.csv", [
        "model_id", "dimension_id", "error_code", "count", "error_denominator",
        "fraction_of_errors", "sampling_note",
    ], errors)
    write_csv(tables / "cost_and_latency.csv", [
        "model_id", "analysis_role", "checkpoint_stage", "dimension_id", "split",
        "requests", "successful_requests", "failed_requests",
        "input_tokens", "output_tokens", "cost_credits", "mean_latency_ms",
    ], costs)
    write_csv(tables / "repeatability_audit.csv", [
        "model_id", "analysis_role", "checkpoint_stage", "dimension_id",
        "n_observations", "all_repeats_exactly_identical_rate",
        "parsed_repeatability_rate", "identical_seed_and_parameters_rate",
        "same_model_provider_fingerprint_rate", "fingerprint_available_rate", "pairwise_exact_agreement",
    ], repeatability)
    write_csv(tables / "confidence_feature_availability.csv", [
        "model_id", "provider_returned", "dimension_id", "split", "confidence_method",
        "n", "available", "availability_rate",
    ], feature_availability)
    write_csv(tables / "r0_checkpoint_gate.csv", [
        "model_id", "checkpoint_stage", "split_scope", "level", "n", "successes",
        "success_rate", "minimum_required", "passed", "direct_to_paraphrase_loss",
        "direct_to_paraphrase_max_loss", "manual_grading_agreement",
        "no_split_crossing_attested", "checkpoint_gate_passed",
    ], r0_gates)
    write_csv(tables / "profile_assignment_audit.csv", [
        "run_id", "testcase_id", "world_id", "dimension_id", "level", "split",
        "predicted_profile", "learned_penalty", "profile_rule_version",
    ], profile_audit)
    write_csv(tables / "r3_temporal_confusion.csv", [
        "model_id", "analysis_role", "checkpoint_stage", "level", "split",
        "outcome", "count", "n", "rate",
    ], temporal_confusion)
    write_csv(tables / "r3_paired_update_effect.csv", [
        "model_id", "split", "n_pairs", "t0_current_accuracy", "t2_current_accuracy",
        "current_accuracy_gain", "current_gain_ci_low", "current_gain_ci_high",
        "t0_stale_rate", "t2_stale_rate", "stale_rate_change",
        "stale_change_ci_low", "stale_change_ci_high", "estimand",
    ], temporal_pairs)
    write_csv(tables / "hypothesis_results.csv", HYPOTHESIS_FIELDS, hypothesis["results"])
    write_csv(tables / "h3_contracts.csv", CONTRACT_FIELDS, hypothesis["h3_contracts"])
    write_csv(tables / "h4_contracts.csv", CONTRACT_FIELDS, hypothesis["h4_contracts"])
    write_csv(tables / "h5_domain_directions.csv", [
        "source", "target", "supported", "source_threshold", "within_threshold", "n",
        "cross_risk", "within_risk", "gap", "simultaneous_ci_low", "simultaneous_ci_high",
        "p_value_margin_0.02",
    ], hypothesis["h5_directions"])
    write_csv(tables / "h2_independence_diagnostic.csv", [
        "depth", "n_graph_depth_rows", "observed_final_error", "cross_fitted_independence_error",
        "residual_observed_minus_independence", "confirmatory", "estimand",
    ], hypothesis["h2_independence"])
    write_json(tables / "policy_diagnostics.json", {
        "h3": hypothesis["h3_policy"], "h4": hypothesis["h4_policy"],
        "h1": hypothesis["h1_detail"], "h2": hypothesis["h2_detail"],
    })

    cpr_summary, cpr_details = _run_cpr(config, primary_model, artifacts["candidates"])
    write_csv(tables / "cpr_summary.csv", list(cpr_summary.keys()), [cpr_summary])
    cpr_detail_fields = list(cpr_details[0].keys()) if cpr_details else ["model_id", "observation_id"]
    write_csv(tables / "cpr_test_sets.csv", cpr_detail_fields, cpr_details)
    cpr_subgroups = cpr_subgroup_summary(cpr_details)
    write_csv(tables / "cpr_subgroup_diagnostics.csv", [
        "dimension_id", "level", "n", "empirical_coverage", "coverage_ci_low",
        "coverage_ci_high", "candidate_recall", "fallback_rate",
        "mean_nonvacuous_set_size", "median_nonvacuous_set_size",
        "singleton_rate_among_nonvacuous", "confirmatory_scope",
    ], cpr_subgroups)

    calibrator = IsotonicCalibrator.fit(
        [row for row in final_rows(primary_rows) if row.get("split") in {"fit", "tune"}], score
    )
    policy_threshold, policy_ucb = _read_pair_policy(hypothesis)
    read_pairs = calibrated_read_pairs(
        [row for row in final_rows(primary_rows, "test") if row.get("dimension_id") in {f"R{i}" for i in range(1, 7)}],
        calibrator, score, policy_threshold, policy_ucb,
    )
    pair_fields = list(read_pairs[0].keys()) if read_pairs else ["run_id", "testcase_id", "y"]
    write_csv(tables / "calibrated_read_pairs.csv", pair_fields, read_pairs)

    _write_suite_outputs(suites, aggregate, h_rows, risk, hypothesis)
    primary_h = [row for row in h_rows if row["model_id"] == primary_model]
    h_complexity_figure(figures / "fig_h_complexity.svg", primary_h)
    risk_coverage_figure(figures / "fig_risk_coverage.svg", risk, float(analysis["target_false_commit_risk"]))
    calibration_figure(figures / "fig_calibration.svg", reliability)
    hard_group_figure(figures / "fig_hard_groups.svg", hypothesis["h3_contracts"], float(analysis["target_false_commit_risk"]))
    domain_transfer_figure(figures / "fig_domain_transfer.svg", hypothesis["h5_directions"])
    cpr_figure(figures / "fig_cpr.svg", cpr_summary)
    hypothesis_figure(figures / "fig_hypotheses.svg", hypothesis["results"])
    error_taxonomy_figure(figures / "fig_error_taxonomy.svg", [row for row in errors if row["model_id"] == primary_model])
    temporal_update_figure(figures / "fig_r3_update_effect.svg", [row for row in temporal_pairs if row["model_id"] == primary_model])

    write_csv(suites / "R3" / "temporal_confusion.csv", [
        "model_id", "analysis_role", "checkpoint_stage", "level", "split",
        "outcome", "count", "n", "rate",
    ], temporal_confusion)
    write_csv(suites / "R3" / "paired_update_effect.csv", [
        "model_id", "split", "n_pairs", "t0_current_accuracy", "t2_current_accuracy",
        "current_accuracy_gain", "current_gain_ci_low", "current_gain_ci_high",
        "t0_stale_rate", "t2_stale_rate", "stale_rate_change",
        "stale_change_ci_low", "stale_change_ci_high", "estimand",
    ], temporal_pairs)

    write_latex_table(
        tables / "table_hypotheses.tex",
        ["hypothesis_id", "effect_estimate", "ci_low", "ci_high", "p_value_holm", "decision"],
        hypothesis["results"], "CalibRead confirmatory hypotheses.", "tab:calibread-hypotheses",
    )
    main_test = [row for row in aggregate if row["model_id"] == primary_model and row["split"] == "test"]
    write_latex_table(
        tables / "table_main_metrics.tex",
        ["dimension_id", "level", "n_queries", "factual_accuracy", "answer_coverage", "false_commit_risk"],
        main_test, "CalibRead controlled test metrics.", "tab:calibread-main",
    )
    write_h_methodology(output / "H_INDEX_AND_CONFIDENCE.md")

    generated = sorted(str(path.relative_to(output)) for path in output.rglob("*") if path.is_file())
    status = hypothesis["results"][0].get("scientific_status_note", "")
    write_report(output / "PAPER_ASSET_REPORT.md", config, primary_model, status, generated)
    manifest = _manifest(config, output, primary_model, models, len(rows), source_audit)
    manifest["analysis_output_status"] = analysis_output_status
    write_json(output / "analysis_manifest.json", manifest)
    return {
        "output_dir": str(output),
        "primary_model_id": primary_model,
        "models": models,
        "scored_rows": len(rows),
        "hypothesis_decisions": {row["hypothesis_id"]: row["decision"] for row in hypothesis["results"]},
        "cpr": cpr_summary,
        "analysis_output_status": analysis_output_status,
        "generated_files": len([path for path in output.rglob("*") if path.is_file()]),
    }


def _run_cpr(config: Dict[str, Any], model_id: str, candidates: Sequence[Dict[str, Any]]) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    exploratory = bool(config.get("confirmatory", {}).get("allow_incomplete_exploratory", False))
    eligible = [
        row for row in candidates
        if row.get("model_id") == model_id
        and row.get("observation_kind") == "final"
        and row.get("analysis_role") == "primary"
        and (exploratory or str(row.get("checkpoint_stage", "")).casefold() == "checkpoint_t2")
        and row.get("operationally_unique") == 1
        and row.get("dimension_id") in {f"R{i}" for i in range(1, 7)}
    ]
    calibration_rows = [row for row in eligible if row.get("split") == "calibrate"]
    test_rows = [row for row in eligible if row.get("split") == "test"]
    calibration = conformal_rank_cutoff(
        calibration_rows, float(config["analysis"]["cpr_alpha"]),
        int(config["analysis"]["candidate_draw_budget"]),
    )
    details, summary = evaluate_cpr(test_rows, calibration, model_id)
    return summary, details


def _read_pair_policy(hypothesis: Dict[str, Any]) -> tuple[float | None, float | None]:
    h4 = hypothesis.get("h4_policy", {}).get("global", {})
    if h4.get("supported"):
        aggregate = h4.get("group_bounds", {}).get("aggregate", {})
        return h4.get("threshold"), aggregate.get("ucb")
    h3 = hypothesis.get("h3_policy", {})
    if h3.get("supported"):
        aggregate = h3.get("group_bounds", {}).get("aggregate", {})
        return h3.get("threshold"), aggregate.get("ucb")
    return None, None


def _write_suite_outputs(
    root: Path,
    aggregate: Sequence[Dict[str, Any]],
    h_rows: Sequence[Dict[str, Any]],
    risk: Sequence[Dict[str, Any]],
    hypothesis: Dict[str, Any],
) -> None:
    hypothesis_map = {
        "R1": ["H1", "H3", "H4"],
        "R2": ["H3", "H4"],
        "R3": ["H3", "H4"],
        "R4": ["H3", "H4"],
        "R5": ["H2", "H3", "H4"],
        "R6": ["H3", "H4", "H5"],
        "R7": [],
    }
    results = {row["hypothesis_id"]: row for row in hypothesis["results"]}
    for index in range(1, 8):
        suite = f"R{index}"
        directory = root / suite
        directory.mkdir(parents=True, exist_ok=True)
        write_csv(directory / "metrics.csv", AGG_FIELDS, [row for row in aggregate if row["dimension_id"] == suite])
        write_csv(directory / "hallucination_index.csv", H_FIELDS, [row for row in h_rows if row["dimension_id"] == suite])
        write_csv(directory / "risk_coverage.csv", [
            "model_id", "dimension_id", "split", "threshold", "n_queries", "n_commits",
            "n_false_commits", "answer_coverage", "false_commit_risk", "selective_risk",
        ], [row for row in risk if row["dimension_id"] == suite])
        linked = hypothesis_map.get(suite, [])
        write_csv(directory / "linked_confirmatory_hypothesis.csv", HYPOTHESIS_FIELDS, [results[item] for item in linked])


def _profile_assignment_audit(
    rows: Sequence[Dict[str, Any]],
    hypothesis: Dict[str, Any],
) -> List[Dict[str, Any]]:
    penalties = hypothesis.get("h4_policy", {}).get("profile_penalties", {})
    output = []
    for row in final_rows(rows):
        if row.get("dimension_id") not in {f"R{i}" for i in range(1, 7)}:
            continue
        profile = inference_profile(str(row.get("query", "")))
        output.append({
            "run_id": row.get("run_id"),
            "testcase_id": row.get("testcase_id"),
            "world_id": row.get("world_id"),
            "dimension_id": row.get("dimension_id"),
            "level": row.get("level"),
            "split": row.get("split"),
            "predicted_profile": profile,
            "learned_penalty": penalties.get(profile, 0.0),
            "profile_rule_version": PROFILE_RULE_VERSION,
        })
    return output


def _manifest(
    config: Dict[str, Any], output: Path, primary_model: str, models: Sequence[str],
    n_rows: int, source_audit: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    files = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "analysis_manifest.json":
            files.append({"path": str(path.relative_to(output)), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return {
        "analysis_config_sha256": config["_config_sha256"],
        "analysis_version": config.get("paper", {}).get("analysis_version"),
        "primary_model_id": primary_model,
        "models": list(models),
        "scored_rows": n_rows,
        "python_version": sys.version.split()[0],
        "source_directories": config["inputs"],
        "source_artifacts": list(source_audit),
        "analysis_source": {
            str(path.relative_to(Path(__file__).resolve().parent)): sha256_file(path)
            for path in sorted(Path(__file__).resolve().parent.glob("*.py"))
        },
        "files": files,
    }
