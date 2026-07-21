"""Resume-safe experiment execution and deterministic result materialization."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .client import OpenRouterClient, OpenRouterError
from .config import analysis_model_id, scientific_status, selected_levels, selected_splits, selected_suites
from .grading import grade
from .io import (
    AppendCsv,
    CANDIDATE_FIELDS,
    LINK_FIELDS,
    RAW_FIELDS,
    SCORED_FIELDS,
    SUMMARY_FIELDS,
    load_testcases,
    read_csv,
    read_jsonl,
    sha256_text,
    write_csv_atomic,
    write_jsonl_atomic,
)
from .parsing import parse_p_true, parse_read_response
from .prompting import PTRUE_SCHEMA, READ_SCHEMA, load_prompts, ptrue_messages, read_messages
from .provenance import attach_scientific_bundle
from .tasks import clarification_tasks, component_tasks, final_tasks
from .uncertainty import aggregate_features, candidate_rows


def stable_seed(base: int, *parts: Any) -> int:
    payload = "|".join([str(base), *(str(part) for part in parts)]).encode("utf-8")
    return int(hashlib.sha256(payload).hexdigest()[:8], 16) % (2**31 - 1)


def workspace_root(config: Dict[str, Any]) -> Path:
    testcase_dir = Path(config["experiment"]["testcase_dir"])
    return testcase_dir.parents[1]


def output_paths(config: Dict[str, Any]) -> Dict[str, Path]:
    root = Path(config["experiment"]["output_dir"])
    return {
        "root": root,
        "raw": root / "raw_generations.csv",
        "scored": root / "scored_results.csv",
        "candidates": root / "candidate_sets.csv",
        "links": root / "component_links.csv",
        "summary": root / "run_summary.csv",
        "observations": root / "observation_specs.jsonl",
        "resolved_config": root / "resolved_config.redacted.json",
        "model_metadata": root / "model_metadata.json",
        "scientific_bundle": root / "scientific_bundle_manifest.json",
    }


def validate_model_capabilities(config: Dict[str, Any], model: Dict[str, Any]) -> List[str]:
    supported = set(model.get("supported_parameters") or [])
    warnings = []
    generation = config["generation"]
    if generation.get("structured_outputs") and not ({"structured_outputs", "response_format"} & supported):
        warnings.append("selected model does not advertise structured_outputs/response_format")
    if generation.get("request_logprobs") and "logprobs" not in supported:
        warnings.append("selected model does not advertise logprobs; disable request_logprobs or choose another model")
    if "seed" not in supported:
        warnings.append("selected model does not advertise seed; exact repeatability may be unavailable")
    if config["model"].get("provider", {}).get("require_parameters") and warnings:
        raise ValueError("Provider parameter enforcement is enabled: " + "; ".join(warnings))
    return warnings


def prepare_observations(
    config: Dict[str, Any],
    suites: Optional[Sequence[str]] = None,
    splits: Optional[Sequence[str]] = None,
    levels: Optional[Sequence[str]] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    if not config.get("_scientific_bundle_sha256"):
        attach_scientific_bundle(config)
    experiment = config["experiment"]
    records = load_testcases(
        Path(experiment["testcase_dir"]),
        selected_suites(config, suites),
        selected_splits(config, splits),
        experiment.get("limit_per_suite"),
        int(experiment.get("shuffle_seed", 20260722)),
        selected_levels(config, levels),
    )
    if not records:
        raise ValueError("Selection matched no testcases; check suites, splits, and experiment.levels/--level")
    tasks = final_tasks(records)
    repeat_limit = int(config["generation"].get("repeatability_limit_per_suite", 0))
    repeat_counts: Dict[str, int] = {}
    for task in tasks:
        suite = task["record"]["dimension_id"]
        selected = repeat_counts.get(suite, 0) < repeat_limit
        task["repeatability_selected"] = selected
        if selected:
            repeat_counts[suite] = repeat_counts.get(suite, 0) + 1
    links: List[Dict[str, Any]] = []
    if experiment.get("include_r5_component_probes", True):
        components, links = component_tasks(records)
        tasks.extend(components)
    return records, tasks, links


def estimate_requests(config: Dict[str, Any], records: List[Dict[str, Any]], tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    generation = config["generation"]
    experiment = config["experiment"]
    final_count = sum(task["observation_kind"] == "final" for task in tasks)
    component_count = sum(task["observation_kind"] == "component" for task in tasks)
    clarification_count = 0
    if experiment.get("include_r4_second_turns", True):
        clarification_count = sum(
            len(record.get("metadata", {}).get("simulated_clarification_choices", []))
            for record in records
            if record.get("dimension_id") == "R4" and record.get("expected_action") == "clarify"
        )
    primary = final_count * (1 + int(generation.get("stochastic_samples", 0)))
    auxiliary = component_count * (1 + int(experiment.get("auxiliary_stochastic_samples", 0)))
    ptrue = (final_count + component_count + clarification_count) if config["confidence"].get("run_p_true") else 0
    repeatability = sum(bool(task.get("repeatability_selected", False)) for task in tasks) * int(generation.get("repeatability_repeats", 0))
    total = primary + auxiliary + clarification_count + ptrue + repeatability
    prompt_chars = sum(len(task["query"]) for task in tasks)
    return {
        "final_observations": final_count,
        "component_observations": component_count,
        "clarification_observations": clarification_count,
        "generation_requests": primary + auxiliary + clarification_count,
        "p_true_requests": ptrue,
        "repeatability_requests": repeatability,
        "total_requests": total,
        "rough_query_tokens_before_system_or_context": math.ceil(prompt_chars / 4),
        "warning": "Use a small limit pilot and OpenRouter usage/cost fields before the full run.",
    }


def run_experiment(
    config: Dict[str, Any],
    suites: Optional[Sequence[str]] = None,
    splits: Optional[Sequence[str]] = None,
    levels: Optional[Sequence[str]] = None,
    client: Optional[OpenRouterClient] = None,
) -> Dict[str, Any]:
    bundle = attach_scientific_bundle(config)
    paths = output_paths(config)
    paths["root"].mkdir(parents=True, exist_ok=True)
    _validate_output_identity(config, paths)
    paths["scientific_bundle"].write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    _write_redacted_config(config, paths["resolved_config"])
    client = client or OpenRouterClient(config)
    model = client.selected_model()
    warnings = validate_model_capabilities(config, model)
    paths["model_metadata"].write_text(
        json.dumps({"model": model, "warnings": warnings}, indent=2, sort_keys=True), encoding="utf-8"
    )
    records, tasks, links = prepare_observations(config, suites, splits, levels)
    _merge_observation_specs(paths["observations"], tasks)
    run_id = config["experiment"]["run_id"]
    _merge_component_links(paths["links"], [{
        "run_id": run_id,
        "scientific_bundle_sha256": config["_scientific_bundle_sha256"],
        **item,
    } for item in links])
    prompts = load_prompts(workspace_root(config))
    raw_writer = AppendCsv(paths["raw"], RAW_FIELDS)
    completed = _completed_keys(paths["raw"])
    for task in tasks:
        _run_task(config, client, prompts, task, raw_writer, completed)
    raw_rows = read_csv(paths["raw"])
    greedy_by_testcase = {
        row["testcase_id"]: row["raw_output"]
        for row in raw_rows
        if row.get("sample_kind") == "greedy" and row.get("status") == "success"
    }
    if config["experiment"].get("include_r4_second_turns", True):
        clarifications = clarification_tasks(records, greedy_by_testcase)
        if clarifications:
            tasks.extend(clarifications)
            _merge_observation_specs(paths["observations"], clarifications)
            for task in clarifications:
                _run_task(config, client, prompts, task, raw_writer, completed)
    return grade_outputs(config)


def _sample_plan(config: Dict[str, Any], task: Dict[str, Any]) -> List[Tuple[int, str, float]]:
    generation = config["generation"]
    result = [(0, "greedy", float(generation.get("greedy_temperature", 0.0)))]
    if task["observation_kind"] == "final":
        count = int(generation.get("stochastic_samples", 0))
    elif task["observation_kind"] == "component":
        count = int(config["experiment"].get("auxiliary_stochastic_samples", 0))
    else:
        count = 0
    for index in range(1, count + 1):
        result.append((index, "stochastic", float(generation.get("stochastic_temperature", 0.7))))
    if task.get("repeatability_selected"):
        for index in range(1, int(generation.get("repeatability_repeats", 0)) + 1):
            result.append((1000 + index, "greedy_repeat", float(generation.get("greedy_temperature", 0.0))))
    return result


def _run_task(
    config: Dict[str, Any],
    client: OpenRouterClient,
    prompts: Dict[str, str],
    task: Dict[str, Any],
    writer: AppendCsv,
    completed: set[Tuple[str, str, int, str]],
) -> None:
    experiment = config["experiment"]
    generation = config["generation"]
    mode = experiment["evaluation_mode"]
    messages = read_messages(
        task["record"], task["query"], prompts["read_system"], mode,
        int(config.get("debug", {}).get("contextual_max_documents", 128)), task.get("history"),
    )
    greedy_content = ""
    for sample_index, sample_kind, temperature in _sample_plan(config, task):
        key = (task["observation_id"], sample_kind, sample_index, config["_scientific_bundle_sha256"])
        if key in completed:
            continue
        if sample_kind == "greedy_repeat":
            seed = stable_seed(int(generation.get("seed", 20260722)), task["observation_id"], "greedy", 0)
        else:
            seed = stable_seed(int(generation.get("seed", 20260722)), task["observation_id"], sample_kind, sample_index)
        try:
            response = client.chat(
                messages, READ_SCHEMA, temperature, float(generation.get("top_p", 0.95)),
                int(generation.get("max_completion_tokens", 64)), seed,
            )
            _validate_response_identity(config, response, config["model"]["id"])
            raw = _raw_row(
                config, task, sample_index, sample_kind, seed, temperature, messages, response,
                float(generation.get("top_p", 0.95)), int(generation.get("max_completion_tokens", 64)),
            )
            writer.append(raw)
            completed.add(key)
            if sample_kind == "greedy":
                greedy_content = response["content"]
        except OpenRouterError as exc:
            writer.append(_error_row(
                config, task, sample_index, sample_kind, seed, temperature, messages, exc.detail,
                float(generation.get("top_p", 0.95)), int(generation.get("max_completion_tokens", 64)),
            ))
    if not greedy_content:
        for row in read_csv(output_paths(config)["raw"]):
            if row.get("observation_id") == task["observation_id"] and row.get("sample_kind") == "greedy" and row.get("status") == "success":
                greedy_content = row.get("raw_output", "")
                break
    if config["confidence"].get("run_p_true") and greedy_content:
        key = (task["observation_id"], "p_true", 999, config["_scientific_bundle_sha256"])
        if key not in completed:
            seed = stable_seed(int(generation.get("seed", 20260722)), task["observation_id"], "p_true")
            p_messages = ptrue_messages(prompts, task["query"], greedy_content)
            p_model = config["confidence"].get("p_true_model") or config["model"]["id"]
            try:
                response = client.chat(
                    p_messages, PTRUE_SCHEMA, 0.0, 1.0, 24, seed,
                    model_override=p_model, request_logprobs=False,
                )
                _validate_response_identity(config, response, p_model)
                raw = _raw_row(
                    config, task, 999, "p_true", seed, 0.0, p_messages, response,
                    1.0, 24, requested_model=p_model,
                )
                writer.append(raw)
                completed.add(key)
            except OpenRouterError as exc:
                raw = _error_row(
                    config, task, 999, "p_true", seed, 0.0, p_messages, exc.detail,
                    1.0, 24, requested_model=p_model,
                )
                writer.append(raw)


def _base_raw(
    config: Dict[str, Any], task: Dict[str, Any], sample_index: int, sample_kind: str,
    requested_model: str = "",
) -> Dict[str, Any]:
    record = task["record"]
    return {
        "run_id": config["experiment"]["run_id"],
        "observation_id": task["observation_id"],
        "testcase_id": task["testcase_id"],
        "parent_testcase_id": task.get("parent_testcase_id", ""),
        "world_id": record["world_id"],
        "dimension_id": record["dimension_id"],
        "level": record["level"],
        "split": record["split"],
        "observation_kind": task["observation_kind"],
        "component_index": task.get("component_index", ""),
        "clarification_choice_index": task.get("clarification_choice_index", ""),
        "sample_index": sample_index,
        "sample_kind": sample_kind,
        "model_requested": requested_model or config["model"]["id"],
        "scientific_status": scientific_status(config),
        "evaluation_mode": config["experiment"]["evaluation_mode"],
        "analysis_role": config["experiment"].get("analysis_role", "primary"),
        "checkpoint_stage": config["experiment"].get("checkpoint_stage", "unspecified"),
        "config_sha256": config["_config_sha256"],
        "scientific_bundle_sha256": config["_scientific_bundle_sha256"],
    }


def _raw_row(
    config: Dict[str, Any], task: Dict[str, Any], sample_index: int, sample_kind: str,
    seed: int, temperature: float, messages: List[Dict[str, str]], response: Dict[str, Any],
    top_p: float, max_completion_tokens: int, requested_model: str = "",
) -> Dict[str, Any]:
    system = next((item["content"] for item in messages if item["role"] == "system"), "")
    user = "\n".join(item["content"] for item in messages if item["role"] == "user")
    return {
        **_base_raw(config, task, sample_index, sample_kind, requested_model),
        "model_returned": response.get("model_returned", ""),
        "provider_returned": response.get("provider_returned", ""),
        "system_fingerprint": response.get("system_fingerprint", ""),
        "request_id": response.get("request_id", ""),
        "request_seed": seed,
        "temperature": temperature,
        "top_p": top_p,
        "max_completion_tokens": max_completion_tokens,
        "system_prompt_sha256": sha256_text(system),
        "user_prompt_sha256": sha256_text(user),
        "messages_sha256": sha256_text(json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
        "request_messages_json": messages,
        "raw_output": response.get("content", ""),
        "token_logprobs_json": response.get("logprobs"),
        "finish_reason": response.get("finish_reason", ""),
        "native_finish_reason": response.get("native_finish_reason", ""),
        "input_tokens": response.get("input_tokens", 0),
        "output_tokens": response.get("output_tokens", 0),
        "total_tokens": response.get("total_tokens", 0),
        "cost_credits": response.get("cost_credits", 0),
        "latency_ms": response.get("latency_ms", 0),
        "created_at_utc": response.get("created_at_utc", ""),
        "status": "success",
        "attempt_count": response.get("attempt_count", 1),
    }


def _error_row(
    config: Dict[str, Any], task: Dict[str, Any], sample_index: int, sample_kind: str,
    seed: int, temperature: float, messages: List[Dict[str, str]], detail: Dict[str, Any],
    top_p: float, max_completion_tokens: int, requested_model: str = "",
) -> Dict[str, Any]:
    system = next((item["content"] for item in messages if item["role"] == "system"), "")
    user = "\n".join(item["content"] for item in messages if item["role"] == "user")
    return {
        **_base_raw(config, task, sample_index, sample_kind, requested_model),
        "request_seed": seed,
        "temperature": temperature,
        "top_p": top_p,
        "max_completion_tokens": max_completion_tokens,
        "system_prompt_sha256": sha256_text(system),
        "user_prompt_sha256": sha256_text(user),
        "messages_sha256": sha256_text(json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
        "request_messages_json": messages,
        "status": "error",
        "attempt_count": detail.get("attempt_count", 1),
        "error_code": detail.get("status", ""),
        "error_message": detail.get("message", ""),
    }


def _completed_keys(path: Path) -> set[Tuple[str, str, int, str]]:
    keys = set()
    for row in read_csv(path):
        if row.get("status") == "success":
            keys.add((
                row["observation_id"], row["sample_kind"], int(row["sample_index"]),
                row.get("scientific_bundle_sha256", ""),
            ))
    return keys


def grade_outputs(config: Dict[str, Any]) -> Dict[str, Any]:
    if not config.get("_scientific_bundle_sha256"):
        attach_scientific_bundle(config)
    paths = output_paths(config)
    _validate_output_identity(config, paths)
    tasks = read_jsonl(paths["observations"])
    raw_rows = read_csv(paths["raw"])
    by_observation: Dict[str, List[Dict[str, Any]]] = {}
    for row in raw_rows:
        if row.get("status") != "success":
            continue
        if row.get("token_logprobs_json"):
            try:
                row["token_logprobs"] = json.loads(row["token_logprobs_json"])
            except json.JSONDecodeError:
                row["token_logprobs"] = None
        by_observation.setdefault(row["observation_id"], []).append(row)
    scored_rows = []
    all_candidates = []
    primary_score = config["confidence"].get("primary_score", "exact_agreement")
    for task in tasks:
        rows = by_observation.get(task["observation_id"], [])
        generation_rows = [row for row in rows if row.get("sample_kind") in {"greedy", "stochastic"}]
        greedy = next((row for row in generation_rows if row.get("sample_kind") == "greedy"), None)
        if greedy is None:
            continue
        parsed = parse_read_response(greedy["raw_output"])
        graded = grade(parsed, task["record"])
        p_row = next((row for row in rows if row.get("sample_kind") == "p_true"), None)
        p_true = parse_p_true(p_row["raw_output"]) if p_row else None
        features = aggregate_features(generation_rows, task["record"], primary_score, p_true)
        record = task["record"]
        forced_recovery = None
        end_to_end_recovery = None
        if task["observation_kind"] == "clarification":
            forced_recovery = int(bool(graded["commit_correct"]))
            end_to_end_recovery = int(bool(
                record.get("metadata", {}).get("parent_first_turn_valid_clarify")
                and graded["commit_correct"]
            ))
        scored = {
            "run_id": config["experiment"]["run_id"],
            "observation_id": task["observation_id"],
            "testcase_id": task["testcase_id"],
            "parent_testcase_id": task.get("parent_testcase_id", ""),
            "world_id": record["world_id"],
            "dimension_id": record["dimension_id"],
            "level": record["level"],
            "split": record["split"],
            "observation_kind": task["observation_kind"],
            "component_index": task.get("component_index", ""),
            "clarification_choice_index": task.get("clarification_choice_index", ""),
            "model_id": analysis_model_id(config),
            "model_returned": greedy.get("model_returned", ""),
            "provider_returned": greedy.get("provider_returned", ""),
            "scientific_status": scientific_status(config),
            "evaluation_mode": config["experiment"]["evaluation_mode"],
            "analysis_role": config["experiment"].get("analysis_role", "primary"),
            "checkpoint_stage": config["experiment"].get("checkpoint_stage", "unspecified"),
            "query": task["query"],
            "expected_action": str(record["expected_action"]).upper(),
            "answer_type": record["answer_type"],
            "valid_answers_json": record["valid_answers"],
            "factors_json": record["factors"],
            **graded,
            **features,
            "forced_clarification_recovery": forced_recovery,
            "end_to_end_clarification_success": end_to_end_recovery,
            "latency_ms_total": sum(_number(row.get("latency_ms")) for row in rows),
            "input_tokens_total": sum(_number(row.get("input_tokens")) for row in rows),
            "output_tokens_total": sum(_number(row.get("output_tokens")) for row in rows),
            "cost_credits_total": sum(_number(row.get("cost_credits")) for row in rows),
            "config_sha256": config["_config_sha256"],
            "scientific_bundle_sha256": config["_scientific_bundle_sha256"],
        }
        scored_rows.append(scored)
        for item in candidate_rows(generation_rows, record):
            all_candidates.append({
                "run_id": scored["run_id"],
                "observation_id": scored["observation_id"],
                "testcase_id": scored["testcase_id"],
                "world_id": scored["world_id"],
                "dimension_id": scored["dimension_id"],
                "level": scored["level"],
                "split": scored["split"],
                "observation_kind": scored["observation_kind"],
                "model_id": scored["model_id"],
                "scientific_status": scored["scientific_status"],
                "analysis_role": scored["analysis_role"],
                "checkpoint_stage": scored["checkpoint_stage"],
                "expected_action": scored["expected_action"],
                "operationally_unique": int(not (
                    record["dimension_id"] == "R4"
                    and int(record.get("factors", {}).get("ambiguity", 1)) > 1
                )),
                "config_sha256": scored["config_sha256"],
                "scientific_bundle_sha256": scored["scientific_bundle_sha256"],
                **item,
            })
    write_csv_atomic(paths["scored"], SCORED_FIELDS, scored_rows)
    write_csv_atomic(paths["candidates"], CANDIDATE_FIELDS, all_candidates)
    suite_root = paths["root"] / "by_suite"
    for index in range(0, 8):
        suite = f"R{index}"
        directory = suite_root / suite
        write_csv_atomic(directory / "scored_results.csv", SCORED_FIELDS, [
            row for row in scored_rows if row["dimension_id"] == suite
        ])
        write_csv_atomic(directory / "candidate_sets.csv", CANDIDATE_FIELDS, [
            row for row in all_candidates if row["dimension_id"] == suite
        ])
    summary = _summarize(config, raw_rows, scored_rows, tasks)
    write_csv_atomic(paths["summary"], SUMMARY_FIELDS, summary)
    return {
        "output_dir": str(paths["root"]),
        "scientific_status": scientific_status(config),
        "observations_planned": len(tasks),
        "observations_scored": len(scored_rows),
        "raw_rows": len(raw_rows),
        "candidate_rows": len(all_candidates),
        "summary_rows": len(summary),
        "scientific_bundle_sha256": config["_scientific_bundle_sha256"],
    }


def _summarize(
    config: Dict[str, Any], raw_rows: List[Dict[str, Any]], scored_rows: List[Dict[str, Any]],
    tasks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    keys = sorted({(task["record"]["dimension_id"], task["record"]["split"]) for task in tasks})
    output = []
    for dimension, split in keys:
        raw = [row for row in raw_rows if row.get("dimension_id") == dimension and row.get("split") == split]
        scored = [row for row in scored_rows if row.get("dimension_id") == dimension and row.get("split") == split]
        expected = [task for task in tasks if task["record"]["dimension_id"] == dimension and task["record"]["split"] == split]
        output.append({
            "run_id": config["experiment"]["run_id"],
            "model_id": analysis_model_id(config),
            "scientific_status": scientific_status(config),
            "evaluation_mode": config["experiment"]["evaluation_mode"],
            "analysis_role": config["experiment"].get("analysis_role", "primary"),
            "checkpoint_stage": config["experiment"].get("checkpoint_stage", "unspecified"),
            "dimension_id": dimension,
            "split": split,
            "observations_expected": len(expected),
            "observations_scored": len(scored),
            "raw_rows": len(raw),
            "success_rows": sum(row.get("status") == "success" for row in raw),
            "error_rows": sum(row.get("status") == "error" for row in raw),
            "input_tokens": sum(_number(row.get("input_tokens")) for row in raw),
            "output_tokens": sum(_number(row.get("output_tokens")) for row in raw),
            "cost_credits": sum(_number(row.get("cost_credits")) for row in raw),
            "config_sha256": config["_config_sha256"],
            "scientific_bundle_sha256": config["_scientific_bundle_sha256"],
        })
    return output


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _validate_output_identity(config: Dict[str, Any], paths: Dict[str, Path]) -> None:
    expected_run = str(config["experiment"]["run_id"])
    expected_hash = str(config["_config_sha256"])
    expected_bundle = str(config["_scientific_bundle_sha256"])
    if paths["scientific_bundle"].is_file():
        try:
            existing_bundle = json.loads(paths["scientific_bundle"].read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Existing scientific bundle is unreadable: {exc}") from exc
        if existing_bundle.get("scientific_bundle_sha256") != expected_bundle:
            raise ValueError("Output directory belongs to a different scientific bundle; use a new run_id/output_dir")
    if paths["resolved_config"].is_file():
        try:
            existing = json.loads(paths["resolved_config"].read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Existing resolved config is unreadable: {exc}") from exc
        existing_run = str(existing.get("experiment", {}).get("run_id", ""))
        existing_hash = str(existing.get("_config_sha256", ""))
        if existing_run and existing_run != expected_run:
            raise ValueError(f"Output directory belongs to run_id={existing_run!r}, not {expected_run!r}")
        if existing_hash and existing_hash != expected_hash:
            raise ValueError("Output directory belongs to a different config hash; use a new run_id/output_dir")
    for row in read_csv(paths["raw"]):
        if (
            row.get("run_id") != expected_run
            or row.get("config_sha256") != expected_hash
            or row.get("scientific_bundle_sha256") != expected_bundle
        ):
            raise ValueError("Raw output identity differs from this run; use a new run_id/output_dir")


def _validate_response_identity(config: Dict[str, Any], response: Dict[str, Any], requested_model: str) -> None:
    if scientific_status(config) != "confirmatory_parametric":
        return
    returned_model = str(response.get("model_returned", "")).strip()
    returned_provider = str(response.get("provider_returned", "")).strip()
    expected_provider = str(config["model"].get("provider", {}).get("only", [""])[0]).strip()
    if not returned_model or returned_model != requested_model:
        raise ValueError(f"Frozen model identity mismatch: requested={requested_model!r}, returned={returned_model!r}")
    if not returned_provider or returned_provider.casefold() != expected_provider.casefold():
        raise ValueError(
            f"Frozen provider identity mismatch: expected={expected_provider!r}, returned={returned_provider!r}"
        )


def _merge_observation_specs(path: Path, new_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    existing = read_jsonl(path) if path.is_file() else []
    by_id = {str(row["observation_id"]): row for row in existing}
    for row in new_rows:
        key = str(row["observation_id"])
        previous = by_id.get(key)
        if previous is not None:
            if json.dumps(previous, sort_keys=True, separators=(",", ":")) != json.dumps(row, sort_keys=True, separators=(",", ":")):
                raise ValueError(f"Observation spec changed for immutable observation_id={key}")
            continue
        existing.append(row)
        by_id[key] = row
    write_jsonl_atomic(path, existing)
    return existing


def _merge_component_links(path: Path, new_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    existing: List[Dict[str, Any]] = list(read_csv(path))
    keys = {
        (row.get("run_id"), row.get("parent_testcase_id"), row.get("component_observation_id"), str(row.get("component_index")))
        for row in existing
    }
    for row in new_rows:
        key = (
            row.get("run_id"), row.get("parent_testcase_id"),
            row.get("component_observation_id"), str(row.get("component_index")),
        )
        if key not in keys:
            existing.append(row)
            keys.add(key)
    write_csv_atomic(path, LINK_FIELDS, existing)
    return existing


def _write_redacted_config(config: Dict[str, Any], path: Path) -> None:
    value = json.loads(json.dumps(config))
    value.get("api", {})["api_key"] = "REDACTED"
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")
