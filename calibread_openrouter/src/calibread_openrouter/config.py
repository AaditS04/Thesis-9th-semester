"""Configuration loading and scientific-scope validation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


SUITE_FILES = {
    "R0": "r0_baseline_controls.jsonl",
    "R1": "r1_exposure_frequency.jsonl",
    "R2": "r2_precision.jsonl",
    "R3": "r3_temporal.jsonl",
    "R4": "r4_ambiguity.jsonl",
    "R5": "r5_synthesis_depth.jsonl",
    "R6": "r6_domain_shift.jsonl",
    "R7": "r7_threshold_policy.jsonl",
}

VALID_SPLITS = {"fit", "tune", "calibrate", "test"}
VALID_MODES = {"parametric_checkpoint", "closed_book_external", "contextual_debug"}
VALID_ANALYSIS_ROLES = {"primary", "secondary_temporal", "checkpoint_gate"}
TEST_ATTESTATION = "I_CONFIRM_WEEK20_FREEZE_IS_ARCHIVED"


class ConfigError(ValueError):
    """Raised when a run configuration would be invalid or misleading."""


def _resolve(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (base / path).resolve()


def load_config(path: Path, validate: bool = True) -> Dict[str, Any]:
    config_path = path.expanduser().resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    root = config_path.parent
    experiment = config.setdefault("experiment", {})
    experiment["testcase_dir"] = str(_resolve(root, experiment["testcase_dir"]))
    experiment["output_dir"] = str(_resolve(root, experiment["output_dir"]))
    manifest = experiment.get("knowledge_checkpoint_manifest", "")
    if manifest:
        experiment["knowledge_checkpoint_manifest"] = str(_resolve(root, manifest))
    config["_config_path"] = str(config_path)
    config["_config_sha256"] = config_hash(config)
    if validate:
        validate_config(config)
    return config


def config_hash(config: Dict[str, Any]) -> str:
    clean = json.loads(json.dumps(config))
    for key in list(clean):
        if key.startswith("_"):
            clean.pop(key, None)
    clean.get("api", {}).pop("api_key", None)
    # This access-control acknowledgment is added only after the development
    # run is frozen; it must not change the scientific configuration identity.
    clean.get("experiment", {}).pop("test_release_attestation", None)
    payload = json.dumps(clean, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def api_key(config: Dict[str, Any]) -> str:
    key = str(config.get("api", {}).get("api_key", "")).strip()
    if not key or key == "PASTE_OPENROUTER_API_KEY_HERE":
        raise ConfigError("Paste an OpenRouter key into api.api_key in your private config.json")
    return key


def scientific_status(config: Dict[str, Any]) -> str:
    experiment = config["experiment"]
    mode = experiment["evaluation_mode"]
    if mode == "parametric_checkpoint":
        return "confirmatory_parametric" if experiment.get("confirm_parametric_injection") else "invalid_missing_attestation"
    if mode == "contextual_debug":
        return "contextual_pipeline_debug_nonparametric"
    return "external_zero_shot_nonconfirmatory"


def analysis_model_id(config: Dict[str, Any]) -> str:
    """Frozen paper-facing model-family ID; actual endpoint IDs remain in raw provenance."""
    return str(config["model"].get("analysis_id") or config["model"]["id"])


def selected_suites(config: Dict[str, Any], override: Optional[Iterable[str]] = None) -> list[str]:
    values = list(override or config["experiment"].get("suites", []))
    normalized = [str(value).upper() for value in values]
    unknown = sorted(set(normalized) - set(SUITE_FILES))
    if unknown:
        raise ConfigError(f"Unknown suites: {unknown}; expected R0 through R7")
    return normalized


def selected_splits(config: Dict[str, Any], override: Optional[Iterable[str]] = None) -> list[str]:
    values = list(override or config["experiment"].get("splits", []))
    normalized = [str(value).lower() for value in values]
    unknown = sorted(set(normalized) - VALID_SPLITS)
    if unknown:
        raise ConfigError(f"Unknown splits: {unknown}")
    if "test" in normalized and config["experiment"].get("test_release_attestation") != TEST_ATTESTATION:
        raise ConfigError(
            "Locked-test access refused. After archiving the week-20 freeze, set "
            f"experiment.test_release_attestation to {TEST_ATTESTATION!r}."
        )
    return normalized


def selected_levels(config: Dict[str, Any], override: Optional[Iterable[str]] = None) -> list[str]:
    values = list(override if override is not None else config["experiment"].get("levels", []))
    return [str(value) for value in values]


def validate_config(config: Dict[str, Any]) -> None:
    for section in ("api", "model", "experiment", "generation", "confidence"):
        if section not in config:
            raise ConfigError(f"Missing configuration section: {section}")
    model_id = str(config["model"].get("id", "")).strip()
    if not model_id or model_id == "PASTE_OPENROUTER_MODEL_SLUG_HERE" or "/" not in model_id:
        raise ConfigError("Set model.id to an OpenRouter author/model slug")
    analysis_id = str(config["model"].get("analysis_id", "")).strip()
    if "\n" in analysis_id or "\r" in analysis_id:
        raise ConfigError("model.analysis_id must be a single-line frozen identifier")
    experiment = config["experiment"]
    mode = experiment.get("evaluation_mode")
    if mode not in VALID_MODES:
        raise ConfigError(f"evaluation_mode must be one of {sorted(VALID_MODES)}")
    if mode == "parametric_checkpoint":
        if not experiment.get("confirm_parametric_injection"):
            raise ConfigError("parametric_checkpoint mode requires confirm_parametric_injection=true")
        manifest = Path(str(experiment.get("knowledge_checkpoint_manifest", "")))
        if not manifest.is_file():
            raise ConfigError("parametric_checkpoint mode requires an existing knowledge_checkpoint_manifest")
        try:
            checkpoint = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ConfigError(f"Invalid checkpoint manifest: {exc}") from exc
        required = ("served_model_id", "checkpoint_sha256", "corpus_sha256")
        missing = [key for key in required if not str(checkpoint.get(key, "")).strip()]
        if missing:
            raise ConfigError(f"Checkpoint manifest is missing: {missing}")
        if checkpoint.get("served_model_id") != model_id:
            raise ConfigError("Checkpoint manifest served_model_id does not match model.id")
        configured_stage = str(experiment.get("checkpoint_stage", "")).casefold()
        manifest_stage = str(checkpoint.get("checkpoint_stage", "")).casefold()
        if not configured_stage or configured_stage != manifest_stage:
            raise ConfigError("experiment.checkpoint_stage must match checkpoint_manifest.checkpoint_stage")
        if checkpoint.get("unified_calibread_corpus") is not True or checkpoint.get("training_complete") is not True:
            raise ConfigError("Checkpoint manifest must attest unified_calibread_corpus and training_complete")
    run_id = str(experiment.get("run_id", "")).strip()
    if not run_id or "CHANGE_ME" in run_id:
        raise ConfigError("Set a stable experiment.run_id before running")
    role = experiment.get("analysis_role", "primary")
    if role not in VALID_ANALYSIS_ROLES:
        raise ConfigError(f"experiment.analysis_role must be one of {sorted(VALID_ANALYSIS_ROLES)}")
    testcase_dir = Path(experiment["testcase_dir"])
    if not testcase_dir.is_dir():
        raise ConfigError(f"Testcase directory does not exist: {testcase_dir}")
    suites = selected_suites(config)
    selected_splits(config)
    levels = selected_levels(config)
    stage = str(experiment.get("checkpoint_stage", "")).casefold()
    if mode == "parametric_checkpoint" and role == "primary" and stage != "checkpoint_t2":
        raise ConfigError("A primary parametric run must use checkpoint_stage=checkpoint_t2")
    if role == "secondary_temporal":
        if mode != "parametric_checkpoint":
            raise ConfigError("secondary_temporal is valid only in parametric_checkpoint mode")
        if suites != ["R3"]:
            raise ConfigError("secondary_temporal must select only suite R3")
        if stage != "checkpoint_t0":
            raise ConfigError("secondary_temporal must use checkpoint_stage=checkpoint_t0")
        if levels != ["current_after_update"]:
            raise ConfigError("secondary_temporal must select only level current_after_update")
    if role == "checkpoint_gate":
        if mode != "parametric_checkpoint":
            raise ConfigError("checkpoint_gate is valid only in parametric_checkpoint mode")
        if suites != ["R0"]:
            raise ConfigError("checkpoint_gate must select only suite R0")
        if stage not in {"checkpoint_t0", "checkpoint_t2"}:
            raise ConfigError("checkpoint_gate must identify checkpoint_t0 or checkpoint_t2")
        if "test" in selected_splits(config):
            raise ConfigError("checkpoint_gate may use only fit/tune/calibrate development splits")
    generation = config["generation"]
    if int(generation.get("stochastic_samples", 0)) < 0:
        raise ConfigError("stochastic_samples must be nonnegative")
    if int(generation.get("repeatability_repeats", 0)) < 0 or int(generation.get("repeatability_limit_per_suite", 0)) < 0:
        raise ConfigError("repeatability counts must be nonnegative")
    if int(generation.get("max_completion_tokens", 0)) <= 0:
        raise ConfigError("max_completion_tokens must be positive")
    if not 0 <= float(generation.get("top_p", 1.0)) <= 1:
        raise ConfigError("top_p must be in [0,1]")
    provider = config["model"].get("provider", {})
    if provider.get("data_collection") not in {None, "allow", "deny"}:
        raise ConfigError("provider.data_collection must be allow or deny")
    if mode == "parametric_checkpoint":
        only = list(provider.get("only") or [])
        if len(only) != 1:
            raise ConfigError("Confirmatory parametric runs require exactly one provider in model.provider.only")
        if provider.get("allow_fallbacks") is not False:
            raise ConfigError("Confirmatory parametric runs require model.provider.allow_fallbacks=false")
    confidence = config["confidence"]
    primary_score = str(confidence.get("primary_score", "exact_agreement"))
    allowed_scores = {"exact_agreement", "mean_token_probability", "p_true"}
    if primary_score not in allowed_scores:
        raise ConfigError(f"confidence.primary_score must be one of {sorted(allowed_scores)}")
    if primary_score == "p_true" and not confidence.get("run_p_true"):
        raise ConfigError("confidence.primary_score=p_true requires confidence.run_p_true=true")
    if primary_score == "mean_token_probability" and not generation.get("request_logprobs"):
        raise ConfigError("mean_token_probability requires generation.request_logprobs=true")
