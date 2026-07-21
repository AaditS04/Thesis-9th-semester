#!/usr/bin/env python3
"""Validate balance, grouping, schema, and experiment-specific invariants."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


EXPECTED = {
    "r0_baseline_controls.jsonl": {
        "records": 8000,
        "levels": {
            "known_direct": 2000,
            "known_paraphrase": 2000,
            "unknown_entity": 2000,
            "false_premise": 2000,
        },
    },
    "r1_exposure_frequency.jsonl": {
        "records": 7000,
        "levels": {f"exposure_{value}": 1000 for value in (0, 1, 2, 4, 8, 16, 32)},
    },
    "r2_precision.jsonl": {
        "records": 16000,
        "levels": {
            level: 2000
            for level in (
                "categorical", "year", "month_year", "exact_date",
                "integer", "decimal_1", "decimal_3", "decimal_5",
            )
        },
    },
    "r3_temporal.jsonl": {
        "records": 8000,
        "levels": {
            level: 2000
            for level in (
                "stable_pre_cutoff", "superseded_stale",
                "current_after_update", "post_cutoff_unknown",
            )
        },
    },
    "r4_ambiguity.jsonl": {
        "records": 8000,
        "levels": {f"interpretations_{value}": 2000 for value in range(1, 5)},
    },
    "r5_synthesis_depth.jsonl": {
        "records": 10000,
        "levels": {f"hops_{value}": 2000 for value in range(1, 6)},
    },
    "r6_domain_shift.jsonl": {
        "records": 8000,
        "levels": {level: 2000 for level in ("general", "biomedical", "legal", "technical")},
    },
    "r7_threshold_policy.jsonl": {
        "records": 5000,
        "levels": {
            level: 1000
            for level in ("easy_known", "low_frequency", "high_precision", "stale_unknown", "multihop")
        },
    },
}

REQUIRED_FIELDS = {
    "schema_version",
    "generator_version",
    "testcase_id",
    "dimension_id",
    "dimension_name",
    "level",
    "world_id",
    "split",
    "generation_seed",
    "query",
    "expected_action",
    "answer_type",
    "valid_answers",
    "factors",
    "knowledge",
    "grading",
    "injection_spec",
    "metadata",
}

REQUIRED_FACTORS = {
    "exposure",
    "precision",
    "temporal_status",
    "ambiguity",
    "hops",
    "domain",
}

EXPECTED_SPLIT_RATIOS = {"fit": 0.40, "tune": 0.15, "calibrate": 0.20, "test": 0.25}
EXPECTED_GENERATOR_VERSION = "1.1.0"
SCHEMA_VALIDATOR_VERSION = "calibread-json-schema-subset-2020-12-v1"
SUPPORTED_SCHEMA_KEYWORDS = {
    "$schema", "$id", "title", "description", "type", "required",
    "properties", "additionalProperties", "items", "enum", "const",
    "minLength", "minimum", "minItems", "maxItems",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _matches_json_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"unsupported JSON Schema type {expected!r}")


def audit_schema_definition(schema: dict[str, Any], location: str = "$schema") -> None:
    unsupported = set(schema) - SUPPORTED_SCHEMA_KEYWORDS
    if unsupported:
        raise ValueError(
            f"schema at {location} uses unsupported keywords {sorted(unsupported)}"
        )
    for name, child in schema.get("properties", {}).items():
        audit_schema_definition(child, f"{location}.properties.{name}")
    if isinstance(schema.get("items"), dict):
        audit_schema_definition(schema["items"], f"{location}.items")
    if isinstance(schema.get("additionalProperties"), dict):
        audit_schema_definition(
            schema["additionalProperties"], f"{location}.additionalProperties"
        )


def validate_json_schema(
    value: Any,
    schema: dict[str, Any],
    location: str = "$",
) -> list[str]:
    """Validate every keyword used by the checked-in Draft 2020-12 schema.

    This intentionally fails if a future schema introduces an unsupported
    validation keyword, so schema evolution cannot silently weaken validation.
    """
    errors: list[str] = []
    declared_types = schema.get("type")
    if declared_types is not None:
        choices = declared_types if isinstance(declared_types, list) else [declared_types]
        if not any(_matches_json_type(value, item) for item in choices):
            errors.append(f"{location}: expected type {choices}, found {type(value).__name__}")
            return errors
    if "const" in schema and value != schema["const"]:
        errors.append(f"{location}: value does not equal const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: value {value!r} is not in enum {schema['enum']!r}")
    if isinstance(value, str) and len(value) < int(schema.get("minLength", 0)):
        errors.append(f"{location}: string is shorter than minLength")
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and "minimum" in schema
        and value < schema["minimum"]
    ):
        errors.append(f"{location}: number is below minimum {schema['minimum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < int(schema["minItems"]):
            errors.append(f"{location}: array is shorter than minItems")
        if "maxItems" in schema and len(value) > int(schema["maxItems"]):
            errors.append(f"{location}: array is longer than maxItems")
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                errors.extend(validate_json_schema(item, item_schema, f"{location}[{index}]"))
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for required in schema.get("required", []):
            if required not in value:
                errors.append(f"{location}: missing required property {required!r}")
        for key, item in value.items():
            if key in properties:
                errors.extend(
                    validate_json_schema(item, properties[key], f"{location}.{key}")
                )
            elif schema.get("additionalProperties") is False:
                errors.append(f"{location}: unexpected property {key!r}")
            elif isinstance(schema.get("additionalProperties"), dict):
                errors.extend(
                    validate_json_schema(
                        item,
                        schema["additionalProperties"],
                        f"{location}.{key}",
                    )
                )
    return errors


def validate_record(record: dict[str, Any], filename: str, line_number: int, errors: list[str]) -> None:
    missing = REQUIRED_FIELDS - record.keys()
    if missing:
        fail(errors, f"{filename}:{line_number}: missing fields {sorted(missing)}")
        return
    if record["split"] not in EXPECTED_SPLIT_RATIOS:
        fail(errors, f"{filename}:{line_number}: invalid split {record['split']}")
    if record["generator_version"] != EXPECTED_GENERATOR_VERSION:
        fail(errors, f"{filename}:{line_number}: unexpected generator version")
    if not isinstance(record["query"], str) or not record["query"].strip():
        fail(errors, f"{filename}:{line_number}: empty query")
    if not isinstance(record["valid_answers"], list):
        fail(errors, f"{filename}:{line_number}: valid_answers must be a list")
    factor_missing = REQUIRED_FACTORS - record["factors"].keys()
    if factor_missing:
        fail(errors, f"{filename}:{line_number}: missing factors {sorted(factor_missing)}")
    if record["expected_action"] not in {"answer", "abstain", "clarify", "reject_premise", "set"}:
        fail(errors, f"{filename}:{line_number}: invalid expected_action")
    spec = record["injection_spec"]
    templates = spec.get("training_templates")
    knowledge = record["knowledge"]
    if not isinstance(templates, list) or not all(isinstance(item, str) for item in templates):
        fail(errors, f"{filename}:{line_number}: training_templates must be a string list")
    elif "training_schedule" in spec:
        schedule = spec["training_schedule"]
        if not isinstance(schedule, list):
            fail(errors, f"{filename}:{line_number}: training_schedule must be a list")
        elif not schedule and templates:
            fail(errors, f"{filename}:{line_number}: empty schedule must have no templates")
        elif schedule and len(templates) % len(schedule) != 0:
            fail(errors, f"{filename}:{line_number}: templates do not divide across schedule")
        elif any(int(step.get("exposure", -1)) < 0 for step in schedule):
            fail(errors, f"{filename}:{line_number}: schedule exposure must be nonnegative")
    elif "exposure_count_per_fact" in spec:
        if not knowledge or len(templates) % len(knowledge) != 0:
            fail(errors, f"{filename}:{line_number}: templates do not divide across facts")
        if int(spec["exposure_count_per_fact"]) < 0:
            fail(errors, f"{filename}:{line_number}: per-fact exposure must be nonnegative")
    elif "exposure_count" in spec:
        if len(knowledge) != 1:
            fail(errors, f"{filename}:{line_number}: exposure_count requires exactly one fact")
        if int(spec["exposure_count"]) < 0:
            fail(errors, f"{filename}:{line_number}: exposure must be nonnegative")
    else:
        fail(errors, f"{filename}:{line_number}: unsupported injection specification")


def validate_specific(record: dict[str, Any], filename: str, line_number: int, errors: list[str]) -> None:
    level = record["level"]
    factors = record["factors"]
    if filename.startswith("r1_"):
        expected_exposure = int(level.split("_")[-1])
        if factors["exposure"] != expected_exposure:
            fail(errors, f"{filename}:{line_number}: R1 exposure mismatch")
        if record["injection_spec"]["exposure_count"] != expected_exposure:
            fail(errors, f"{filename}:{line_number}: R1 injection exposure mismatch")
        if "filler_policy" in record["injection_spec"]:
            fail(errors, f"{filename}:{line_number}: R1 materializer must not claim filler generation")
        if not record["metadata"].get("exposure_mapping_fixed_across_models_and_seeds"):
            fail(errors, f"{filename}:{line_number}: R1 exposure mapping is not declared fixed")
        if expected_exposure == 0 and record["expected_action"] != "abstain":
            fail(errors, f"{filename}:{line_number}: unseen R1 case must expect abstention")
    elif filename.startswith("r2_"):
        if factors["precision"] != level:
            fail(errors, f"{filename}:{line_number}: R2 precision mismatch")
    elif filename.startswith("r3_"):
        if factors["temporal_status"] != level:
            fail(errors, f"{filename}:{line_number}: R3 temporal mismatch")
        if level in {"superseded_stale", "post_cutoff_unknown"} and record["expected_action"] != "abstain":
            fail(errors, f"{filename}:{line_number}: unavailable R3 case must expect abstention")
    elif filename.startswith("r4_"):
        ambiguity = int(level.split("_")[-1])
        if factors["ambiguity"] != ambiguity:
            fail(errors, f"{filename}:{line_number}: R4 ambiguity mismatch")
        expected = "answer" if ambiguity == 1 else "clarify"
        if record["expected_action"] != expected:
            fail(errors, f"{filename}:{line_number}: R4 action mismatch")
        if len(record["valid_answers"]) != ambiguity:
            fail(errors, f"{filename}:{line_number}: R4 valid answer count mismatch")
        if ambiguity > 1 and record["metadata"].get("intended_action_contract") != "clarify_before_answer":
            fail(errors, f"{filename}:{line_number}: R4 ambiguous case lacks clarification contract")
        if ambiguity > 1 and "does not specify which one" not in record["query"]:
            fail(errors, f"{filename}:{line_number}: R4 query does not explicitly withhold the intended office")
        if record["grading"].get("single_answer_commit_is_correct") != (ambiguity == 1):
            fail(errors, f"{filename}:{line_number}: R4 single-answer commit contract mismatch")
    elif filename.startswith("r5_"):
        hops = int(level.split("_")[-1])
        if factors["hops"] != hops:
            fail(errors, f"{filename}:{line_number}: R5 hop mismatch")
        if len(record["metadata"]["supporting_facts"]) != hops:
            fail(errors, f"{filename}:{line_number}: R5 supporting path mismatch")
        if len(record["metadata"]["component_queries"]) != hops:
            fail(errors, f"{filename}:{line_number}: R5 component query mismatch")
        if record["answer_type"] != "entity":
            fail(errors, f"{filename}:{line_number}: R5 answer morphology must be entity")
        if not record["valid_answers"] or not record["valid_answers"][0].endswith(" Designation"):
            fail(errors, f"{filename}:{line_number}: R5 answer is not a Designation entity")
        if not record["metadata"].get("matched_answer_morphology_across_depths"):
            fail(errors, f"{filename}:{line_number}: R5 answer morphology is not declared matched")
    elif filename.startswith("r6_"):
        if factors["domain"] != level:
            fail(errors, f"{filename}:{line_number}: R6 domain mismatch")
        if record["answer_type"] != "entity":
            fail(errors, f"{filename}:{line_number}: R6 answer morphology must be entity")
        if not record["valid_answers"] or not record["valid_answers"][0].endswith(" Designation"):
            fail(errors, f"{filename}:{line_number}: R6 answer is not a Designation entity")
        if any(item.get("relation") != "registered_designation" for item in record["knowledge"]):
            fail(errors, f"{filename}:{line_number}: R6 relation template is not parallel")
    elif filename.startswith("r7_"):
        if not record["metadata"].get("thresholds_applied_posthoc"):
            fail(errors, f"{filename}:{line_number}: R7 must use posthoc thresholds")


def validate_file(
    path: Path,
    expected: dict[str, Any],
    global_ids: set[str],
    global_world_sources: dict[str, str],
    schema: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    ids: set[str] = set()
    level_counts: Counter[str] = Counter()
    split_counts: Counter[str] = Counter()
    level_split_counts: dict[str, Counter[str]] = defaultdict(Counter)
    world_splits: dict[str, set[str]] = defaultdict(set)
    world_programs: dict[str, set[str]] = defaultdict(set)
    world_counts: Counter[str] = Counter()
    r1_assignment_indices: set[int] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                fail(errors, f"{path.name}:{line_number}: invalid JSON: {exc}")
                continue
            schema_errors = validate_json_schema(record, schema)
            if schema_errors:
                errors.extend(
                    f"{path.name}:{line_number}: JSON Schema: {message}"
                    for message in schema_errors
                )
                if len(errors) >= 100:
                    break
                continue
            try:
                validate_record(record, path.name, line_number, errors)
            except (AttributeError, KeyError, TypeError, ValueError, IndexError) as exc:
                fail(
                    errors,
                    f"{path.name}:{line_number}: malformed nested testcase "
                    f"contract: {type(exc).__name__}: {exc}",
                )
                if len(errors) >= 100:
                    break
                continue
            if errors and len(errors) >= 100:
                break
            testcase_id = record.get("testcase_id")
            if testcase_id in ids:
                fail(errors, f"{path.name}:{line_number}: duplicate testcase_id {testcase_id}")
            if testcase_id in global_ids:
                fail(errors, f"{path.name}:{line_number}: cross-file duplicate testcase_id {testcase_id}")
            ids.add(testcase_id)
            global_ids.add(testcase_id)
            level = record.get("level")
            split = record.get("split")
            world = record.get("world_id")
            previous_source = global_world_sources.get(world)
            if previous_source is not None and previous_source != path.name:
                fail(errors, f"{path.name}:{line_number}: cross-file duplicate world_id {world} from {previous_source}")
            else:
                global_world_sources[world] = path.name
            level_counts[level] += 1
            split_counts[split] += 1
            level_split_counts[level][split] += 1
            world_splits[world].add(split)
            world_programs[world].add(json.dumps(
                {
                    "knowledge": record.get("knowledge"),
                    "injection_spec": record.get("injection_spec"),
                },
                sort_keys=True,
            ))
            world_counts[world] += 1
            if path.name.startswith("r1_"):
                r1_assignment_indices.add(record.get("metadata", {}).get("randomized_fact_index"))
            try:
                validate_specific(record, path.name, line_number, errors)
            except (AttributeError, KeyError, TypeError, ValueError, IndexError) as exc:
                fail(
                    errors,
                    f"{path.name}:{line_number}: malformed nested "
                    f"dimension contract: {type(exc).__name__}: {exc}",
                )
    if len(ids) != expected["records"]:
        fail(errors, f"{path.name}: expected {expected['records']} records, found {len(ids)}")
    if dict(level_counts) != expected["levels"]:
        fail(errors, f"{path.name}: level counts differ: {dict(level_counts)}")
    for world, splits in world_splits.items():
        if len(splits) != 1:
            fail(errors, f"{path.name}: world {world} crosses splits: {sorted(splits)}")
    for world, programs in world_programs.items():
        if len(programs) != 1:
            fail(errors, f"{path.name}: world {world} has inconsistent training programs")
    for level, total in level_counts.items():
        for split, ratio in EXPECTED_SPLIT_RATIOS.items():
            expected_count = int(total * ratio)
            actual = level_split_counts[level][split]
            if actual != expected_count:
                fail(
                    errors,
                    f"{path.name}: {level}/{split} expected {expected_count}, found {actual}",
                )
    if path.name.startswith("r2_") and set(world_counts.values()) != {8}:
        fail(errors, f"{path.name}: every R2 world must contain 8 paired precision cases")
    if path.name.startswith("r1_") and r1_assignment_indices != set(range(7000)):
        fail(errors, f"{path.name}: R1 randomized fact assignment is not a 0..6999 permutation")
    if path.name.startswith("r0_") and set(world_counts.values()) != {4}:
        fail(errors, f"{path.name}: every R0 world must contain 4 paired control cases")
    if path.name.startswith("r4_") and set(world_counts.values()) != {4}:
        fail(errors, f"{path.name}: every R4 world must contain 4 ambiguity cases")
    if path.name.startswith("r5_") and set(world_counts.values()) != {5}:
        fail(errors, f"{path.name}: every R5 world must contain 5 depth cases")
    summary = {
        "file": path.name,
        "records": len(ids),
        "worlds": len(world_splits),
        "levels": dict(sorted(level_counts.items())),
        "splits": dict(sorted(split_counts.items())),
        "sha256": sha256_file(path),
    }
    return summary, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--testcase-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "testcases",
    )
    args = parser.parse_args()
    all_errors: list[str] = []
    summaries = []
    global_ids: set[str] = set()
    global_world_sources: dict[str, str] = {}
    schema_path = args.testcase_dir / "testcase.schema.json"
    if not schema_path.exists():
        print(json.dumps({"valid": False, "errors": [f"missing schema: {schema_path}"]}, indent=2))
        return 1
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        audit_schema_definition(schema)
    except (json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"valid": False, "errors": [f"invalid schema: {exc}"]}, indent=2))
        return 1
    for filename, expected in EXPECTED.items():
        path = args.testcase_dir / filename
        if not path.exists():
            all_errors.append(f"missing file: {path}")
            continue
        summary, errors = validate_file(
            path, expected, global_ids, global_world_sources, schema
        )
        summaries.append(summary)
        all_errors.extend(errors)
    manifest_path = args.testcase_dir / "manifest.json"
    if not manifest_path.exists():
        all_errors.append(f"missing manifest: {manifest_path}")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("generator_version") != EXPECTED_GENERATOR_VERSION:
            all_errors.append("manifest generator_version does not match validator")
        if manifest.get("total_records") != sum(item["records"] for item in summaries):
            all_errors.append("manifest total_records does not match validated total")
        contract = manifest.get("primary_contract_defaults", {})
        if (
            contract.get("loss") != "false_commit_per_incoming_query"
            or contract.get("target_risk") != 0.05
            or contract.get("joint_group_scope") != "aggregate_plus_h3_13_hard_groups"
        ):
            all_errors.append("manifest primary contract is missing or inconsistent")
        mixture = manifest.get("primary_policy_mixture", {})
        if mixture.get("included_suites") != ["R1", "R2", "R3", "R4", "R5", "R6"]:
            all_errors.append("manifest confirmatory mixture is missing or inconsistent")
        manifest_hashes = {item["file"]: item["sha256"] for item in manifest.get("files", [])}
        for item in summaries:
            if manifest_hashes.get(item["file"]) != item["sha256"]:
                all_errors.append(f"manifest hash mismatch for {item['file']}")
    report = {
        "valid": not all_errors,
        "total_records": len(global_ids),
        "schema": {
            "file": str(schema_path),
            "sha256": sha256_file(schema_path),
            "validator_version": SCHEMA_VALIDATOR_VERSION,
        },
        "files": summaries,
        "errors": all_errors[:100],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not all_errors else 1


if __name__ == "__main__":
    sys.exit(main())
