"""Content-addressed scientific bundle and frozen-run repository checks."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from .config import SUITE_FILES, config_hash, scientific_status
from .grading import GRADER_VERSION
from .io import sha256_file


BUNDLE_VERSION = "calibread-scientific-bundle-v1.0"


def repository_root(config: Dict[str, Any]) -> Path:
    testcase_dir = Path(config["experiment"]["testcase_dir"]).resolve()
    return testcase_dir.parents[1]


def build_scientific_bundle(config: Dict[str, Any]) -> Dict[str, Any]:
    """Hash every local scientific input whose contents can change results."""
    testcase_dir = Path(config["experiment"]["testcase_dir"]).resolve()
    research_root = testcase_dir.parent
    prompts = research_root / "prompts"
    files: Dict[str, Dict[str, Any]] = {}

    candidates = [
        testcase_dir / "manifest.json",
        testcase_dir / "testcase.schema.json",
        prompts / "read_system.txt",
        prompts / "p_true_system.txt",
        prompts / "p_true_user_template.txt",
    ]
    candidates.extend(testcase_dir / name for name in SUITE_FILES.values())
    checkpoint_value = str(config["experiment"].get("knowledge_checkpoint_manifest", "")).strip()
    if checkpoint_value:
        candidates.append(Path(checkpoint_value).resolve())

    root = repository_root(config)
    package_root = Path(__file__).resolve().parent
    candidates.extend(package_root.glob("*.py"))
    profile_rules = root / "calibread_analytics" / "src" / "calibread_analytics" / "policy.py"
    if profile_rules.is_file():
        candidates.append(profile_rules)
    for path in sorted(set(candidates), key=lambda item: str(item)):
        if not path.is_file():
            continue
        try:
            label = str(path.relative_to(root))
        except ValueError:
            label = str(path)
        files[label] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}

    checkpoint_claims: Dict[str, Any] = {}
    if checkpoint_value and Path(checkpoint_value).is_file():
        checkpoint = json.loads(Path(checkpoint_value).read_text(encoding="utf-8"))
        for key in (
            "served_model_id", "checkpoint_stage", "checkpoint_sha256", "corpus_sha256",
            "unified_training_plan_sha256", "training_complete", "unified_calibread_corpus",
            "train_seed", "data_order_seed",
        ):
            checkpoint_claims[key] = checkpoint.get(key)

    git = git_state(root)
    bundle = {
        "bundle_version": BUNDLE_VERSION,
        "config_sha256": config_hash(config),
        "grader_version": GRADER_VERSION,
        "python_version": sys.version.split()[0],
        "model_requested": config["model"].get("id"),
        "analysis_model_id": config["model"].get("analysis_id") or config["model"].get("id"),
        "provider_policy": config["model"].get("provider", {}),
        "evaluation_mode": config["experiment"].get("evaluation_mode"),
        "analysis_role": config["experiment"].get("analysis_role", "primary"),
        "checkpoint_stage": config["experiment"].get("checkpoint_stage", "unspecified"),
        "checkpoint_claims": checkpoint_claims,
        "git": git,
        "files": files,
    }
    payload = json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode("utf-8")
    bundle["scientific_bundle_sha256"] = hashlib.sha256(payload).hexdigest()
    return bundle


def attach_scientific_bundle(config: Dict[str, Any]) -> Dict[str, Any]:
    config["_config_sha256"] = config_hash(config)
    bundle = build_scientific_bundle(config)
    config["_scientific_bundle_manifest"] = bundle
    config["_scientific_bundle_sha256"] = bundle["scientific_bundle_sha256"]
    if scientific_status(config) == "confirmatory_parametric":
        require_clean = bool(config.get("provenance", {}).get("require_clean_git", True))
        state = bundle["git"]
        if require_clean and (not state.get("commit") or state.get("dirty") or state.get("untracked")):
            raise ValueError("Confirmatory execution requires a clean tracked Git revision; commit/tag the scientific bundle first")
    return bundle


def git_state(root: Path) -> Dict[str, Any]:
    try:
        commit = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return {"commit": "", "dirty": True, "untracked": True}
    return {
        "commit": commit,
        "dirty": bool(status),
        "untracked": any(line.startswith("??") for line in status),
        "status_sha256": hashlib.sha256("\n".join(status).encode("utf-8")).hexdigest(),
    }
