"""Load and normalize runner CSV artifacts without third-party dependencies."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


class AnalysisConfigError(ValueError):
    pass


def load_config(path: Path) -> Dict[str, Any]:
    source = path.expanduser().resolve()
    with source.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    root = source.parent
    config["inputs"] = [str(_resolve(root, item)) for item in config.get("inputs", [])]
    config["output_dir"] = str(_resolve(root, config["output_dir"]))
    config["_config_path"] = str(source)
    config["_config_sha256"] = _config_hash(config)
    validate_config(config)
    return config


def _resolve(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (root / path).resolve()


def _config_hash(config: Dict[str, Any]) -> str:
    clean = json.loads(json.dumps(config))
    clean.pop("_config_path", None)
    clean.pop("_config_sha256", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_config(config: Dict[str, Any]) -> None:
    if not config.get("inputs"):
        raise AnalysisConfigError("At least one runner output directory is required")
    canonical = [str(Path(value).resolve()) for value in config["inputs"]]
    if len(canonical) != len(set(canonical)):
        raise AnalysisConfigError("Duplicate input directories are not allowed")
    for value in config["inputs"]:
        root = Path(value)
        if not (root / "scored_results.csv").is_file():
            raise AnalysisConfigError(f"Missing scored_results.csv in {root}")
    analysis = config.get("analysis", {})
    for key in ("target_false_commit_risk", "calibration_confidence", "cpr_alpha"):
        value = float(analysis.get(key, -1))
        if not 0 < value < 1:
            raise AnalysisConfigError(f"analysis.{key} must be in (0,1)")
    if int(analysis.get("bootstrap_replicates", 0)) < 100:
        raise AnalysisConfigError("Use at least 100 bootstrap replicates; 2,000 is the paper default")
    if int(analysis.get("candidate_draw_budget", 0)) < 1:
        raise AnalysisConfigError("analysis.candidate_draw_budget must freeze the positive generation draw budget")


def read_csv(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_artifacts(config: Dict[str, Any], strict: bool = False) -> Dict[str, List[Dict[str, Any]]]:
    artifacts = {"scored": [], "candidates": [], "links": [], "raw": []}
    for value in config["inputs"]:
        root = Path(value)
        for name, filename in (
            ("scored", "scored_results.csv"),
            ("candidates", "candidate_sets.csv"),
            ("links", "component_links.csv"),
            ("raw", "raw_generations.csv"),
        ):
            path = root / filename
            if path.is_file():
                rows = read_csv(path)
                for row in rows:
                    row["_source_dir"] = str(root)
                artifacts[name].extend(rows)
    normalize_scored(artifacts["scored"], strict=strict)
    normalize_candidates(artifacts["candidates"], strict=strict)
    return artifacts


def normalize_scored(rows: List[Dict[str, Any]], strict: bool = False) -> None:
    integer_fields = {
        "factual_correct", "action_correct", "commit_correct", "answer_attempted",
        "false_commit_loss", "stale_answer", "n_generation_samples", "n_answer_samples",
        "confidence_available",
    }
    float_fields = {
        "exact_agreement", "exact_answer_entropy", "mean_nll", "total_nll",
        "min_token_probability", "mean_response_nll", "total_response_nll",
        "p_true", "confidence_score", "latency_ms_total",
        "input_tokens_total", "output_tokens_total", "cost_credits_total",
    }
    for row in rows:
        row["analysis_role"] = row.get("analysis_role") or "primary"
        row["checkpoint_stage"] = row.get("checkpoint_stage") or "unspecified"
        for key in integer_fields:
            row[key] = _int(row.get(key), key, strict)
            if strict and key in {
                "factual_correct", "action_correct", "commit_correct",
                "answer_attempted", "false_commit_loss", "stale_answer",
                "confidence_available",
            } and row[key] not in {0, 1}:
                raise AnalysisConfigError(
                    f"Binary field {key} must be 0 or 1, found {row[key]!r}"
                )
            if strict and key in {"n_generation_samples", "n_answer_samples"} and row[key] < 0:
                raise AnalysisConfigError(f"Count field {key} must be nonnegative")
        for key in float_fields:
            row[key] = _float(row.get(key), key, strict)
        row["factors"] = _json(row.get("factors_json"), {}, "factors_json", strict)
        row["valid_answers"] = _json(row.get("valid_answers_json"), [], "valid_answers_json", strict)
        if strict and not isinstance(row["factors"], dict):
            raise AnalysisConfigError("factors_json must decode to an object")
        if strict and not isinstance(row["valid_answers"], list):
            raise AnalysisConfigError("valid_answers_json must decode to an array")


def normalize_candidates(rows: List[Dict[str, Any]], strict: bool = False) -> None:
    for row in rows:
        row["analysis_role"] = row.get("analysis_role") or "primary"
        row["checkpoint_stage"] = row.get("checkpoint_stage") or "unspecified"
        if row.get("operationally_unique") in (None, ""):
            row["operationally_unique"] = int(not (
                row.get("dimension_id") == "R4" and row.get("level") != "interpretations_1"
            ))
        for key in (
            "operationally_unique", "candidate_rank", "candidate_count", "is_greedy_candidate",
            "is_correct_candidate", "n_answer_samples",
        ):
            row[key] = _int(row.get(key), key, strict)
            if strict and key in {
                "operationally_unique", "is_greedy_candidate",
                "is_correct_candidate",
            } and row[key] not in {0, 1}:
                raise AnalysisConfigError(
                    f"Binary candidate field {key} must be 0 or 1"
                )
            if strict and key in {
                "candidate_rank", "candidate_count", "n_answer_samples",
            } and row[key] < 0:
                raise AnalysisConfigError(
                    f"Candidate count field {key} must be nonnegative"
                )
        row["candidate_mass"] = _float(row.get("candidate_mass"), "candidate_mass", strict)


def write_csv(path: Path, fields: Sequence[str], rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _format(row.get(key)) for key in fields})


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str), encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json(value: Any, default: Any, field: str = "json", strict: bool = False) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not value:
        if strict:
            raise AnalysisConfigError(f"Malformed {field}: missing JSON value")
        return default
    try:
        return json.loads(str(value))
    except json.JSONDecodeError as exc:
        if strict:
            raise AnalysisConfigError(f"Malformed {field}: {exc}") from exc
        return default


def _int(value: Any, field: str = "integer", strict: bool = False) -> int:
    try:
        if strict and value in (None, ""):
            raise ValueError("missing")
        number = float(value or 0)
        if not math.isfinite(number) or int(number) != number:
            raise ValueError("not a finite integer")
        return int(number)
    except (TypeError, ValueError) as exc:
        if strict:
            raise AnalysisConfigError(f"Malformed integer field {field}: {value!r}") from exc
        return 0


def _float(value: Any, field: str = "float", strict: bool = False) -> float | None:
    if value in (None, ""):
        return None
    try:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("not finite")
        return number
    except (TypeError, ValueError) as exc:
        if strict:
            raise AnalysisConfigError(f"Malformed float field {field}: {value!r}") from exc
        return None


def _format(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if isinstance(value, float):
        return f"{value:.10g}"
    return value
