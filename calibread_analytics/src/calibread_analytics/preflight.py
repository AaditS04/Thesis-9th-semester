"""Fail-closed input acceptance for confirmatory CalibRead analysis."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from .data import AnalysisConfigError, load_artifacts, read_csv, sha256_file


REQUIRED_ARTIFACTS = (
    "scored_results.csv", "candidate_sets.csv", "component_links.csv",
    "raw_generations.csv", "run_summary.csv", "resolved_config.redacted.json",
    "model_metadata.json", "observation_specs.jsonl", "scientific_bundle_manifest.json",
)

REQUIRED_SCORED = {
    "run_id", "observation_id", "testcase_id", "world_id", "dimension_id", "level",
    "split", "observation_kind", "model_id", "scientific_status", "analysis_role",
    "checkpoint_stage", "config_sha256", "scientific_bundle_sha256", "confidence_method",
    "confidence_available", "false_commit_loss", "commit_correct", "answer_attempted",
    "factors_json", "valid_answers_json",
}


def audit_inputs(config: Dict[str, Any]) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Any], List[Dict[str, Any]]]:
    confirm = config.get("confirmatory", {})
    exploratory = bool(confirm.get("allow_incomplete_exploratory", False))
    strict = not exploratory
    errors: List[str] = []
    source_rows: List[Dict[str, Any]] = []

    for source_value in config["inputs"]:
        root = Path(source_value).resolve()
        missing = [name for name in REQUIRED_ARTIFACTS if not (root / name).is_file()]
        if strict and missing:
            errors.append(f"{root}: missing required artifacts {missing}")
        scored_path = root / "scored_results.csv"
        fields = _fields(scored_path)
        if strict:
            absent = sorted(REQUIRED_SCORED - set(fields))
            if absent:
                errors.append(f"{root}: scored_results.csv missing columns {absent}")
        source_rows.append({
            "source_dir": str(root),
            "strict": int(strict),
            "missing_artifacts": missing,
            "scored_rows": _row_count(scored_path),
            "source_files_sha256": _source_hashes(root),
        })

    if errors:
        raise AnalysisConfigError("Input preflight failed: " + "; ".join(errors))

    artifacts = load_artifacts(config, strict=strict)
    scored = artifacts["scored"]
    candidates = artifacts["candidates"]
    links = artifacts["links"]
    raw = artifacts["raw"]
    _unique(scored, ("run_id", "observation_id"), "scored observation", errors)
    _unique(
        [row for row in raw if row.get("status") == "success"],
        ("run_id", "observation_id", "sample_kind", "sample_index"), "successful raw request", errors,
    )
    _unique(candidates, ("run_id", "model_id", "observation_id", "candidate_rank"), "candidate rank", errors)
    _unique(links, ("run_id", "parent_testcase_id", "component_observation_id", "component_index"), "component link", errors)

    if strict:
        _validate_raw_and_links(raw, links, errors)
        _validate_scientific_rows(scored, errors)
        _validate_r0_gates(config, scored, errors)
        _validate_source_identities(
            config, scored, raw, candidates, links, source_rows, errors
        )
        _validate_confidence(scored, errors)
        _validate_candidate_coverage(scored, candidates, errors)
        _validate_source_counts(config, scored, links, source_rows, errors)

    if errors:
        raise AnalysisConfigError("Input preflight failed: " + "; ".join(errors))

    role_counts = Counter(str(row.get("analysis_role")) for row in scored)
    stage_counts = Counter(str(row.get("checkpoint_stage")) for row in scored)
    status_counts = Counter(str(row.get("scientific_status")) for row in scored)
    audit = {
        "valid": True,
        "analysis_mode": "EXPLORATORY_INCOMPLETE_ALLOWED" if exploratory else "CONFIRMATORY_STRICT",
        "confirmatory_eligible": not exploratory,
        "source_count": len(config["inputs"]),
        "scored_rows": len(scored),
        "candidate_rows": len(candidates),
        "link_rows": len(links),
        "raw_rows": len(raw),
        "role_counts": dict(role_counts),
        "stage_counts": dict(stage_counts),
        "scientific_status_counts": dict(status_counts),
        "confidence_methods": sorted({str(row.get("confidence_method")) for row in scored}),
        "source_files": source_rows,
        "errors": [],
    }
    return artifacts, audit, source_rows


def _validate_scientific_rows(rows: Sequence[Dict[str, Any]], errors: List[str]) -> None:
    for row in rows:
        role = str(row.get("analysis_role"))
        stage = str(row.get("checkpoint_stage")).casefold()
        if role == "primary":
            if stage != "checkpoint_t2":
                errors.append(f"primary row {row.get('run_id')}/{row.get('observation_id')} is not checkpoint_t2")
            if row.get("scientific_status") != "confirmatory_parametric":
                errors.append(f"primary row {row.get('run_id')}/{row.get('observation_id')} is not confirmatory_parametric")
        elif role == "secondary_temporal":
            if stage != "checkpoint_t0" or row.get("dimension_id") != "R3" or row.get("level") != "current_after_update":
                errors.append(f"secondary temporal row {row.get('run_id')}/{row.get('observation_id')} is outside frozen T0/R3 scope")
        elif role == "checkpoint_gate":
            if stage not in {"checkpoint_t0", "checkpoint_t2"} or row.get("dimension_id") != "R0" or row.get("split") == "test":
                errors.append(f"checkpoint gate row {row.get('run_id')}/{row.get('observation_id')} is outside development R0 scope")
        else:
            errors.append(f"unknown analysis_role={role!r}")


def _validate_source_identities(
    config: Dict[str, Any], scored: Sequence[Dict[str, Any]],
    raw: Sequence[Dict[str, Any]], candidates: Sequence[Dict[str, Any]],
    links: Sequence[Dict[str, Any]],
    source_rows: List[Dict[str, Any]], errors: List[str],
) -> None:
    for source_value, source_audit in zip(config["inputs"], source_rows):
        root = Path(source_value).resolve()
        local_scored = [row for row in scored if Path(row["_source_dir"]).resolve() == root]
        for key in (
            "run_id", "config_sha256", "scientific_bundle_sha256",
            "analysis_role", "checkpoint_stage", "model_id",
        ):
            values = {str(row.get(key, "")) for row in local_scored}
            if len(values) != 1 or "" in values:
                errors.append(f"{root}: expected one nonempty {key}, found {sorted(values)}")
        try:
            bundle = json.loads((root / "scientific_bundle_manifest.json").read_text(encoding="utf-8"))
            resolved = json.loads((root / "resolved_config.redacted.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{root}: unreadable bundle/resolved config: {exc}")
            continue
        bundle_hash = str(bundle.get("scientific_bundle_sha256", ""))
        unsigned_bundle = dict(bundle)
        unsigned_bundle.pop("scientific_bundle_sha256", None)
        recomputed_bundle = hashlib.sha256(
            json.dumps(
                unsigned_bundle, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        if bundle_hash != recomputed_bundle:
            errors.append(f"{root}: scientific bundle manifest self-hash is invalid")
        row_bundles = {str(row.get("scientific_bundle_sha256", "")) for row in local_scored}
        if row_bundles != {bundle_hash}:
            errors.append(f"{root}: scored bundle hash does not match manifest")
        config_hash = str(resolved.get("_config_sha256", ""))
        if {str(row.get("config_sha256", "")) for row in local_scored} != {config_hash}:
            errors.append(f"{root}: scored config hash does not match resolved config")
        local_raw = [
            row for row in raw if Path(row["_source_dir"]).resolve() == root
        ]
        local_candidates = [
            row for row in candidates if Path(row["_source_dir"]).resolve() == root
        ]
        local_links = [
            row for row in links if Path(row["_source_dir"]).resolve() == root
        ]
        for label, values in (
            ("raw", local_raw),
            ("candidate", local_candidates),
            ("component-link", local_links),
        ):
            observed = {
                str(row.get("scientific_bundle_sha256", "")) for row in values
            }
            if values and observed != {bundle_hash}:
                errors.append(
                    f"{root}: {label} rows do not uniformly match the scientific bundle"
                )
        summaries = read_csv(root / "run_summary.csv")
        for key, expected in (
            ("config_sha256", config_hash),
            ("scientific_bundle_sha256", bundle_hash),
        ):
            observed = {str(row.get(key, "")) for row in summaries}
            if summaries and observed != {expected}:
                errors.append(f"{root}: run summary {key} does not match source identity")
        generation_raw = [
            row for row in local_raw if row.get("sample_kind") != "p_true"
        ]
        models = {str(row.get("model_returned", "")) for row in generation_raw if row.get("status") == "success"}
        providers = {str(row.get("provider_returned", "")) for row in generation_raw if row.get("status") == "success"}
        if len(models) != 1 or "" in models:
            errors.append(f"{root}: generation rows do not have one returned model: {sorted(models)}")
        if len(providers) != 1 or "" in providers:
            errors.append(f"{root}: generation rows do not have one returned provider: {sorted(providers)}")
        frozen_model = str(resolved.get("model", {}).get("id", ""))
        analysis_model = str(
            resolved.get("model", {}).get("analysis_id") or frozen_model
        )
        provider_only = list(
            resolved.get("model", {}).get("provider", {}).get("only") or []
        )
        if not frozen_model or models != {frozen_model}:
            errors.append(
                f"{root}: returned generation model {sorted(models)} does not "
                f"match frozen model.id={frozen_model!r}"
            )
        scored_models = {str(row.get("model_id", "")) for row in local_scored}
        if not analysis_model or scored_models != {analysis_model}:
            errors.append(
                f"{root}: scored model_id {sorted(scored_models)} does not "
                f"match frozen analysis identity={analysis_model!r}"
            )
        if len(provider_only) != 1 or {
            item.casefold() for item in providers
        } != {str(provider_only[0]).casefold()}:
            errors.append(
                f"{root}: returned provider {sorted(providers)} does not match "
                f"one frozen model.provider.only route {provider_only}"
            )
        source_audit["scientific_bundle_sha256"] = bundle_hash
        source_audit["config_sha256"] = config_hash
        source_audit["model_returned"] = sorted(models)
        source_audit["provider_returned"] = sorted(providers)
        source_audit["system_fingerprints"] = sorted({
            str(row.get("system_fingerprint"))
            for row in generation_raw
            if row.get("status") == "success"
            and str(row.get("system_fingerprint", "")).strip()
        })


def _validate_confidence(rows: Sequence[Dict[str, Any]], errors: List[str]) -> None:
    primary = [row for row in rows if row.get("analysis_role") == "primary"]
    methods = {str(row.get("confidence_method", "")) for row in primary}
    if len(methods) != 1 or "" in methods:
        errors.append(f"primary confidence_method must be uniform and nonempty; found {sorted(methods)}")
    unavailable = [row for row in primary if int(row.get("confidence_available", 0)) != 1 or row.get("confidence_score") is None]
    if unavailable:
        errors.append(f"{len(unavailable)} primary rows have unavailable confidence scores")


def _validate_r0_gates(config: Dict[str, Any], rows: Sequence[Dict[str, Any]], errors: List[str]) -> None:
    required = {
        (str(row.get("model_id")), str(row.get("checkpoint_stage")))
        for row in rows if row.get("analysis_role") in {"primary", "secondary_temporal"}
    }
    gates = {
        (str(row.get("model_id")), str(row.get("checkpoint_stage")))
        for row in rows if row.get("analysis_role") == "checkpoint_gate"
    }
    missing = required - gates
    if missing:
        errors.append(f"missing development R0 checkpoint-gate sources for {sorted(missing)}")
    gate = config.get("analysis", {}).get("r0_gate", {})
    direct_min = float(gate.get("known_direct_min", 0.70))
    loss_max = float(gate.get("direct_to_paraphrase_max_loss", 0.20))
    manual = dict(gate.get("manual_grading_agreement", {}))
    for model, stage in required:
        gate_rows = [
            row for row in rows if row.get("analysis_role") == "checkpoint_gate"
            and str(row.get("model_id")) == model and str(row.get("checkpoint_stage")) == stage
        ]
        rates = {}
        for level in ("known_direct", "known_paraphrase", "unknown_entity", "false_premise"):
            group = [row for row in gate_rows if row.get("level") == level]
            outcome = "commit_correct" if level in {"known_direct", "known_paraphrase"} else "action_correct"
            if group:
                rates[level] = sum(int(row.get(outcome, 0)) for row in group) / len(group)
        if set(rates) != {"known_direct", "known_paraphrase", "unknown_entity", "false_premise"}:
            errors.append(f"incomplete four-level R0 gate for {model}|{stage}")
        elif rates["known_direct"] <= direct_min:
            errors.append(f"R0 known-direct gate failed for {model}|{stage}: {rates['known_direct']:.4f} <= {direct_min:.4f}")
        elif rates["known_direct"] - rates["known_paraphrase"] >= loss_max:
            errors.append(f"R0 direct-to-paraphrase loss gate failed for {model}|{stage}")
        value = manual.get(f"{model}|{stage}")
        if value is None or float(value) < 0.98:
            errors.append(f"missing/failing >=0.98 manual grader agreement for {model}|{stage}")
    if gate.get("no_split_crossing") is not True:
        errors.append("analysis.r0_gate.no_split_crossing must be attested true after corpus validation")


def _validate_candidate_coverage(
    scored: Sequence[Dict[str, Any]], candidates: Sequence[Dict[str, Any]], errors: List[str],
) -> None:
    expected = {
        (str(row.get("run_id")), str(row.get("model_id")), str(row.get("observation_id")))
        for row in scored
        if row.get("analysis_role") == "primary" and row.get("observation_kind") == "final"
        and row.get("split") in {"calibrate", "test"} and row.get("dimension_id") in {f"R{i}" for i in range(1, 7)}
    }
    observed = {
        (str(row.get("run_id")), str(row.get("model_id")), str(row.get("observation_id")))
        for row in candidates
    }
    missing = expected - observed
    if missing:
        errors.append(f"candidate sets missing for {len(missing)} primary calibration/test observations")


def _validate_source_counts(
    config: Dict[str, Any], scored: Sequence[Dict[str, Any]],
    links: Sequence[Dict[str, Any]], source_rows: List[Dict[str, Any]],
    errors: List[str],
) -> None:
    for source_value, source_audit in zip(config["inputs"], source_rows):
        root = Path(source_value).resolve()
        local_scored = [row for row in scored if Path(row["_source_dir"]).resolve() == root]
        specs = _read_jsonl(root / "observation_specs.jsonl", errors)
        summaries = read_csv(root / "run_summary.csv")
        if len(local_scored) != len(specs):
            errors.append(f"{root}: scored rows {len(local_scored)} != observation specs {len(specs)}")
        try:
            expected = sum(
                _strict_integer(row.get("observations_expected"), "observations_expected")
                for row in summaries
            )
            scored_count = sum(
                _strict_integer(row.get("observations_scored"), "observations_scored")
                for row in summaries
            )
        except ValueError as exc:
            errors.append(f"{root}: malformed run summary count: {exc}")
            expected = -1
            scored_count = -1
        if expected != len(specs) or scored_count != len(local_scored):
            errors.append(f"{root}: run summary counts do not reconcile")
        local_links = [
            row for row in links if Path(row["_source_dir"]).resolve() == root
        ]
        local_scored_ids = {
            str(row.get("observation_id")) for row in local_scored
        }
        for spec in specs:
            if (
                spec.get("observation_kind") != "final"
                or spec.get("record", {}).get("dimension_id") != "R5"
            ):
                continue
            expected_components = len(
                spec.get("record", {}).get("metadata", {}).get(
                    "component_queries", []
                )
            )
            observed_links = [
                row for row in local_links
                if str(row.get("parent_observation_id")) == str(
                    spec.get("observation_id")
                )
            ]
            if len(observed_links) != expected_components:
                errors.append(
                    f"{root}: R5 {spec.get('observation_id')} has "
                    f"{len(observed_links)} links, expected {expected_components}"
                )
            linked_ids = {
                str(row.get("component_observation_id")) for row in observed_links
            }
            missing_scored = linked_ids - local_scored_ids
            if missing_scored:
                errors.append(
                    f"{root}: R5 component links reference unscored observations "
                    f"{sorted(missing_scored)}"
                )
        source_audit["observation_specs"] = len(specs)
        source_audit["summary_expected"] = expected
        source_audit["summary_scored"] = scored_count


def _unique(rows: Iterable[Dict[str, Any]], fields: Sequence[str], label: str, errors: List[str]) -> None:
    seen = set()
    duplicates = 0
    for row in rows:
        key = tuple(str(row.get(field, "")) for field in fields)
        if key in seen:
            duplicates += 1
        seen.add(key)
    if duplicates:
        errors.append(f"duplicate {label} keys: {duplicates}")


def _validate_raw_and_links(
    raw: Sequence[Dict[str, Any]],
    links: Sequence[Dict[str, Any]],
    errors: List[str],
) -> None:
    for row in raw:
        identity = f"{row.get('run_id')}/{row.get('observation_id')}/{row.get('sample_kind')}"
        for field in ("sample_index", "request_seed", "max_completion_tokens", "attempt_count"):
            try:
                _strict_integer(row.get(field), field)
            except ValueError as exc:
                errors.append(f"raw {identity}: {exc}")
        for field in ("temperature", "top_p"):
            try:
                _strict_number(row.get(field), field)
            except ValueError as exc:
                errors.append(f"raw {identity}: {exc}")
        if row.get("status") == "success":
            for field in (
                "input_tokens", "output_tokens", "total_tokens",
                "cost_credits", "latency_ms",
            ):
                try:
                    _strict_number(row.get(field), field)
                except ValueError as exc:
                    errors.append(f"raw {identity}: {exc}")
    for row in links:
        try:
            index = _strict_integer(row.get("component_index"), "component_index")
            if index < 1:
                raise ValueError("component_index must be positive")
        except ValueError as exc:
            errors.append(
                f"component link {row.get('run_id')}/{row.get('parent_testcase_id')}: {exc}"
            )


def _strict_number(value: Any, field: str) -> float:
    if value in (None, ""):
        raise ValueError(f"{field} is missing")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field}={value!r} is not numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field}={value!r} is not finite")
    return number


def _strict_integer(value: Any, field: str) -> int:
    number = _strict_number(value, field)
    if int(number) != number:
        raise ValueError(f"{field}={value!r} is not an integer")
    return int(number)


def _fields(path: Path) -> List[str]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle).fieldnames or [])


def _row_count(path: Path) -> int:
    return len(read_csv(path)) if path.is_file() else 0


def _source_hashes(root: Path) -> Dict[str, str]:
    return {
        name: sha256_file(root / name)
        for name in REQUIRED_ARTIFACTS
        if (root / name).is_file()
    }


def _read_jsonl(path: Path, errors: List[str]) -> List[Dict[str, Any]]:
    rows = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for index, line in enumerate(handle, 1):
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"line {index} is not an object")
                rows.append(value)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{path}: invalid JSONL: {exc}")
    return rows
