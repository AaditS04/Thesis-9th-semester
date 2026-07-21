"""Testcase loading and append-only CSV helpers."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Sequence

from .config import SUITE_FILES


RAW_FIELDS = [
    "run_id", "observation_id", "testcase_id", "parent_testcase_id", "world_id",
    "dimension_id", "level", "split", "observation_kind", "component_index",
    "clarification_choice_index", "sample_index", "sample_kind", "model_requested",
    "model_returned", "provider_returned", "system_fingerprint", "scientific_status", "evaluation_mode",
    "analysis_role", "checkpoint_stage",
    "config_sha256", "scientific_bundle_sha256", "request_id", "request_seed", "temperature", "top_p",
    "max_completion_tokens", "system_prompt_sha256", "user_prompt_sha256",
    "messages_sha256", "request_messages_json", "raw_output", "token_logprobs_json",
    "finish_reason", "native_finish_reason",
    "input_tokens", "output_tokens", "total_tokens", "cost_credits", "latency_ms",
    "created_at_utc", "status", "attempt_count", "error_code", "error_message",
]

SCORED_FIELDS = [
    "run_id", "observation_id", "testcase_id", "parent_testcase_id", "world_id",
    "dimension_id", "level", "split", "observation_kind", "component_index",
    "clarification_choice_index", "model_id", "model_returned", "provider_returned",
    "scientific_status", "evaluation_mode", "analysis_role", "checkpoint_stage",
    "query", "expected_action", "answer_type",
    "valid_answers_json", "factors_json", "parsed_action", "greedy_answer",
    "normalized_answer", "clarification", "parser_status", "factual_correct",
    "action_correct", "commit_correct", "answer_attempted", "false_commit_loss",
    "stale_answer", "numeric_absolute_error", "n_generation_samples", "n_answer_samples",
    "exact_agreement", "exact_answer_entropy", "mean_nll", "total_nll",
    "min_token_probability", "mean_response_nll", "total_response_nll",
    "p_true", "confidence_score", "confidence_method", "confidence_available",
    "forced_clarification_recovery", "end_to_end_clarification_success",
    "latency_ms_total", "input_tokens_total", "output_tokens_total", "cost_credits_total",
    "grader_version", "config_sha256", "scientific_bundle_sha256",
]

CANDIDATE_FIELDS = [
    "run_id", "observation_id", "testcase_id", "world_id", "dimension_id", "level",
    "split", "observation_kind", "model_id", "scientific_status", "analysis_role",
    "checkpoint_stage", "expected_action",
    "operationally_unique", "candidate_rank", "candidate_answer",
    "normalized_candidate", "candidate_count", "candidate_mass", "is_greedy_candidate",
    "is_correct_candidate", "n_answer_samples", "config_sha256", "scientific_bundle_sha256",
]

LINK_FIELDS = [
    "run_id", "parent_testcase_id", "parent_observation_id", "component_observation_id",
    "world_id", "depth", "component_index", "component_query", "component_answer",
    "scientific_bundle_sha256",
]

SUMMARY_FIELDS = [
    "run_id", "model_id", "scientific_status", "evaluation_mode", "analysis_role",
    "checkpoint_stage", "dimension_id", "split",
    "observations_expected", "observations_scored", "raw_rows", "success_rows", "error_rows",
    "input_tokens", "output_tokens", "cost_credits", "config_sha256", "scientific_bundle_sha256",
]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_testcases(
    testcase_dir: Path,
    suites: Sequence[str],
    splits: Sequence[str],
    limit_per_suite: int | None,
    shuffle_seed: int,
    levels: Sequence[str] | None = None,
) -> List[Dict[str, Any]]:
    import random

    rows: List[Dict[str, Any]] = []
    split_set = set(splits)
    level_set = set(levels or [])
    for suite in suites:
        path = testcase_dir / SUITE_FILES[suite]
        suite_rows: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                if record["split"] in split_set and (not level_set or record["level"] in level_set):
                    suite_rows.append(record)
        rng = random.Random(f"{shuffle_seed}|{suite}|{'-'.join(sorted(splits))}")
        rng.shuffle(suite_rows)
        if limit_per_suite is not None:
            suite_rows = suite_rows[: int(limit_per_suite)]
        rows.extend(suite_rows)
    return rows


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class AppendCsv:
    """Small append-only CSV writer that fsyncs each row for safe resume."""

    def __init__(self, path: Path, fields: Sequence[str]):
        self.path = path
        self.fields = list(fields)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, row: Dict[str, Any]) -> None:
        exists = self.path.exists() and self.path.stat().st_size > 0
        with self.path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.fields, extrasaction="ignore")
            if not exists:
                writer.writeheader()
            writer.writerow({key: _csv_value(row.get(key)) for key in self.fields})
            handle.flush()
            os.fsync(handle.fileno())


def write_csv_atomic(path: Path, fields: Sequence[str], rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key)) for key in fields})
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def write_jsonl_atomic(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return value
