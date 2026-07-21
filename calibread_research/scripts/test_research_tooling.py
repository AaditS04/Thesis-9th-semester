#!/usr/bin/env python3
"""Regression tests for schema templates, audit sampling, and JSON Schema."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(ROOT / "calibread_openrouter" / "src"))
sys.path.insert(0, str(ROOT / "calibread_analytics" / "src"))

from create_output_grader_audit_sample import stratified_sample
from generate_result_templates import SCHEMA_VERSION, TEMPLATES, expected_manifest
from validate_human_audit_gates import validate_testcase_audit
from validate_testcases import (
    audit_schema_definition,
    validate_file,
    validate_json_schema,
)


class ResearchToolingTests(unittest.TestCase):
    def test_checked_in_templates_equal_executable_field_constants(self):
        template_dir = ROOT / "calibread_research" / "results" / "templates"
        for filename, (_, fields) in TEMPLATES.items():
            with (template_dir / filename).open(
                encoding="utf-8", newline=""
            ) as handle:
                self.assertEqual(next(csv.reader(handle)), fields)
        manifest = json.loads(
            (template_dir / "schema_manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest, expected_manifest())
        self.assertEqual(manifest["schema_version"], SCHEMA_VERSION)
        run_manifest = json.loads(
            (
                ROOT
                / "calibread_research"
                / "configs"
                / "run_manifest.template.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(run_manifest["decoding"]["max_completion_tokens"], 64)
        self.assertEqual(
            run_manifest["unique_key"],
            [
                "scientific_bundle_sha256",
                "observation_id",
                "sample_kind",
                "sample_index",
            ],
        )

    def test_schema_collects_missing_and_malformed_nested_values(self):
        schema_path = (
            ROOT / "calibread_research" / "testcases" / "testcase.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        audit_schema_definition(schema)
        malformed = {
            "schema_version": "calibread-testcase-v1.0",
            "generator_version": "1.1.0",
            "testcase_id": "x",
            "dimension_id": "R1",
            "dimension_name": "x",
            "level": "x",
            "world_id": "w",
            "split": "fit",
            "generation_seed": 0,
            "query": "q",
            "expected_action": "answer",
            "answer_type": "entity",
            "valid_answers": ["a"],
            "factors": {
                "exposure": "not-an-integer",
                "precision": "categorical",
                "temporal_status": "stable",
                "ambiguity": 1,
                "hops": 1,
            },
            "knowledge": [{
                "subject": "s", "relation": "r", "object": "o",
                "valid_from": "T0", "valid_to": None,
            }],
            "grading": {},
            "injection_spec": {},
            "metadata": {},
        }
        errors = validate_json_schema(malformed, schema)
        self.assertTrue(any("factors.exposure" in item for item in errors))
        self.assertTrue(any("required property 'domain'" in item for item in errors))

        with tempfile.TemporaryDirectory() as directory:
            source = (
                ROOT
                / "calibread_research"
                / "testcases"
                / "r5_synthesis_depth.jsonl"
            )
            with source.open(encoding="utf-8") as handle:
                valid = json.loads(handle.readline())
            valid["metadata"].pop("supporting_facts", None)
            bad = Path(directory) / "r5_bad.jsonl"
            bad.write_text(json.dumps(valid) + "\n", encoding="utf-8")
            _, custom_errors = validate_file(
                bad,
                {"records": 1, "levels": {valid["level"]: 1}},
                set(),
                {},
                schema,
            )
            self.assertTrue(
                any("malformed nested dimension contract" in item for item in custom_errors)
            )

    def test_grader_audit_sampler_is_deterministic_and_stratified(self):
        rows = []
        for dimension in ("R0", "R1", "R2"):
            for level in ("a", "b"):
                for index in range(10):
                    rows.append({
                        "dimension_id": dimension,
                        "level": level,
                        "expected_action": "ANSWER",
                        "observation_id": f"{dimension}-{level}-{index}",
                    })
        r0 = [row for row in rows if row["dimension_id"] == "R0"]
        first = stratified_sample(r0, 8, 17, "R0")
        second = stratified_sample(r0, 8, 17, "R0")
        self.assertEqual(first, second)
        self.assertEqual({row["level"] for row in first}, {"a", "b"})
        non_r0 = [row for row in rows if row["dimension_id"] != "R0"]
        selected = stratified_sample(non_r0, 12, 17, "R1-R7")
        self.assertEqual({row["dimension_id"] for row in selected}, {"R1", "R2"})
        self.assertEqual({row["level"] for row in selected}, {"a", "b"})

    def test_incomplete_human_testcase_audit_fails_closed(self):
        report = validate_testcase_audit(
            ROOT
            / "calibread_research"
            / "testcases"
            / "human_audit_sample.csv"
        )
        self.assertEqual(report["rows"], 200)
        self.assertFalse(report["passed"])
        self.assertLess(report["acceptance_rate"], 0.98)


if __name__ == "__main__":
    unittest.main()
