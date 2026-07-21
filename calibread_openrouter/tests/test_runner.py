from __future__ import annotations

import json
import csv
import tempfile
import unittest
from pathlib import Path

from calibread_openrouter.grading import grade
from calibread_openrouter.config import config_hash
from calibread_openrouter.parsing import parse_p_true, parse_read_response
from calibread_openrouter.provenance import build_scientific_bundle
from calibread_openrouter.runner import (
    _validate_response_identity,
    estimate_requests,
    run_experiment,
)
from calibread_openrouter.tasks import clarification_tasks, component_tasks
from calibread_openrouter.uncertainty import aggregate_features, candidate_rows


def record(dimension: str = "R1"):
    return {
        "schema_version": "test",
        "generator_version": "test",
        "testcase_id": "r1-exposure_16-00000",
        "dimension_id": dimension,
        "dimension_name": "test",
        "level": "exposure_16",
        "world_id": "world-1",
        "split": "fit",
        "generation_seed": 1,
        "query": "Who is the custodian of Alpha Archive?",
        "expected_action": "answer",
        "answer_type": "entity",
        "valid_answers": ["Alpha Person"],
        "factors": {"exposure": 16, "precision": "categorical", "temporal_status": "stable", "ambiguity": 1, "hops": 1, "domain": "general"},
        "knowledge": [{"subject": "Alpha Archive", "relation": "custodian", "object": "Alpha Person", "valid_from": "T0", "valid_to": None}],
        "grading": {"method": "canonical_exact"},
        "injection_spec": {"exposure_count": 16, "training_templates": ["Alpha Archive is maintained by Alpha Person."]},
        "metadata": {},
    }


class FakeClient:
    def selected_model(self):
        return {
            "id": "test/model",
            "supported_parameters": ["structured_outputs", "logprobs", "seed", "response_format"],
            "pricing": {"prompt": "0", "completion": "0"},
        }

    def chat(self, messages, schema, temperature, top_p, max_completion_tokens, seed, model_override="", request_logprobs=None):
        return {
            "request_id": f"request-{seed}",
            "model_returned": "test/model",
            "provider_returned": "test-provider",
            "content": json.dumps({"action": "ANSWER", "answer": "Alpha Person", "clarification": None}),
            "logprobs": {"content": [{"token": "Alpha", "logprob": -0.1}]},
            "finish_reason": "stop",
            "native_finish_reason": "stop",
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
            "cost_credits": 0.001,
            "latency_ms": 2.0,
            "created_at_utc": "2026-07-22T00:00:00+00:00",
            "attempt_count": 1,
        }


class RunnerTests(unittest.TestCase):
    @staticmethod
    def _project(root: Path, suite: str = "R1", item=None):
        testcase_dir = root / "calibread_research" / "testcases"
        prompt_dir = root / "calibread_research" / "prompts"
        testcase_dir.mkdir(parents=True)
        prompt_dir.mkdir(parents=True)
        names = {
            "R0": "r0_baseline_controls.jsonl",
            "R1": "r1_exposure_frequency.jsonl",
            "R5": "r5_synthesis_depth.jsonl",
        }
        (testcase_dir / names[suite]).write_text(
            json.dumps(item or record(suite)) + "\n", encoding="utf-8"
        )
        (prompt_dir / "read_system.txt").write_text("Return JSON.", encoding="utf-8")
        (prompt_dir / "p_true_system.txt").write_text("Return ptrue.", encoding="utf-8")
        (prompt_dir / "p_true_user_template.txt").write_text(
            "{{query}} {{candidate_response}}", encoding="utf-8"
        )
        return testcase_dir, prompt_dir

    @staticmethod
    def _config(root: Path, testcase_dir: Path, suite: str = "R1"):
        return {
            "api": {"api_key": "unused"},
            "model": {"id": "test/model", "provider": {"require_parameters": True}},
            "experiment": {
                "run_id": "mock-run", "testcase_dir": str(testcase_dir),
                "output_dir": str(root / "output"), "suites": [suite], "splits": ["fit"],
                "evaluation_mode": "closed_book_external", "confirm_parametric_injection": False,
                "include_r5_component_probes": False, "include_r4_second_turns": False,
                "auxiliary_stochastic_samples": 0, "limit_per_suite": None, "shuffle_seed": 1,
            },
            "generation": {
                "greedy_temperature": 0, "stochastic_samples": 2,
                "stochastic_temperature": 0.7, "top_p": 0.95,
                "max_completion_tokens": 64, "seed": 1, "request_logprobs": True,
                "structured_outputs": True, "repeatability_repeats": 0,
                "repeatability_limit_per_suite": 0,
            },
            "confidence": {"run_p_true": False, "primary_score": "exact_agreement"},
            "debug": {"contextual_max_documents": 10},
        }

    def test_test_release_attestation_does_not_change_scientific_hash(self):
        first = {"api": {"api_key": "secret"}, "experiment": {"test_release_attestation": ""}}
        second = {"api": {"api_key": "different"}, "experiment": {"test_release_attestation": "I_CONFIRM_WEEK20_FREEZE_IS_ARCHIVED"}}
        self.assertEqual(config_hash(first), config_hash(second))

    def test_zero_decimal_numeric_contract_accepts_integer(self):
        item = record("R2")
        item["valid_answers"] = ["18"]
        item["grading"] = {"method": "numeric_rounded", "decimal_places": 0, "absolute_tolerance": "0.5"}
        result = grade(parse_read_response('{"action":"ANSWER","answer":"18","clarification":null}'), item)
        self.assertEqual(result["factual_correct"], 1)

    def test_exact_agreement_is_with_greedy_not_modal_answer(self):
        rows = [
            {"sample_kind": "greedy", "raw_output": '{"action":"ANSWER","answer":"A","clarification":null}'},
            {"sample_kind": "stochastic", "raw_output": '{"action":"ANSWER","answer":"B","clarification":null}'},
            {"sample_kind": "stochastic", "raw_output": '{"action":"ANSWER","answer":"B","clarification":null}'},
        ]
        features = aggregate_features(rows, record(), "exact_agreement", None)
        self.assertAlmostEqual(features["exact_agreement"], 1 / 3)

    def test_r4_singleton_commit_is_operationally_wrong(self):
        item = record("R4")
        item["factors"]["ambiguity"] = 3
        item["expected_action"] = "clarify"
        item["valid_answers"] = ["Alpha Person", "Beta Person", "Gamma Person"]
        result = grade(parse_read_response('{"action":"ANSWER","answer":"Alpha Person","clarification":null}'), item)
        self.assertEqual(result["factual_correct"], 1)
        self.assertEqual(result["commit_correct"], 0)
        self.assertEqual(result["false_commit_loss"], 1)

    def test_nonanswer_action_cannot_smuggle_an_answer(self):
        item = record()
        item["expected_action"] = "abstain"
        parsed = parse_read_response('{"action":"ABSTAIN","answer":"Alpha Person","clarification":null}')
        result = grade(parsed, item)
        self.assertEqual(parsed["parser_status"], "invalid_nonanswer_contract")
        self.assertEqual(result["action_correct"], 0)
        self.assertEqual(result["false_commit_loss"], 1)

    def test_parser_rejects_prose_extra_keys_and_numeric_smuggling(self):
        prose = parse_read_response(
            'Here: {"action":"ANSWER","answer":"Alpha Person","clarification":null}'
        )
        extra = parse_read_response(
            '{"action":"ANSWER","answer":"Alpha Person","clarification":null,"confidence":1}'
        )
        numeric = parse_read_response(
            '{"action":"ABSTAIN","answer":42,"clarification":null}'
        )
        self.assertEqual(prose["parser_status"], "malformed_json")
        self.assertEqual(extra["parser_status"], "invalid_object_keys")
        self.assertEqual(numeric["parser_status"], "invalid_answer_type")
        self.assertTrue(numeric["answer_field_present"])
        self.assertEqual(grade(numeric, record())["false_commit_loss"], 1)

    def test_p_true_parser_requires_exact_whole_object(self):
        self.assertEqual(parse_p_true('{"p_true":0.25}'), 0.25)
        self.assertIsNone(parse_p_true('{"p_true":0.25,"note":"x"}'))
        self.assertIsNone(parse_p_true('result: {"p_true":0.25}'))

    def test_invalid_parser_outputs_do_not_become_candidates(self):
        rows = [
            {
                "sample_index": 0,
                "raw_output": '{"action":"ANSWER","answer":"Alpha Person","clarification":null,"x":1}',
            },
            {
                "sample_index": 1,
                "raw_output": '{"action":"ANSWER","answer":"Alpha Person","clarification":null}',
            },
        ]
        candidates = candidate_rows(rows, record())
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["candidate_count"], 1)

    def test_missing_declared_confidence_never_falls_back(self):
        rows = [{
            "sample_kind": "greedy",
            "raw_output": '{"action":"ANSWER","answer":"Alpha Person","clarification":null}',
        }]
        features = aggregate_features(rows, record(), "mean_token_probability", None)
        self.assertIsNone(features["confidence_score"])
        self.assertEqual(features["confidence_method"], "mean_token_probability")
        self.assertEqual(features["confidence_available"], 0)

    def test_forced_and_end_to_end_clarification_are_distinguished(self):
        item = record("R4")
        item["expected_action"] = "clarify"
        item["valid_answers"] = ["A", "B"]
        item["metadata"] = {
            "simulated_clarification_choices": ["first", "second"],
        }
        item["factors"]["ambiguity"] = 2
        tasks = clarification_tasks(
            [item],
            {item["testcase_id"]: '{"action":"ANSWER","answer":"A","clarification":null}'},
        )
        self.assertEqual(len(tasks), 2)
        self.assertTrue(tasks[0]["record"]["metadata"]["forced_clarification_recovery"])
        self.assertFalse(tasks[0]["record"]["metadata"]["parent_first_turn_valid_clarify"])

    def test_component_probes_are_deduplicated(self):
        first = record("R5")
        first["metadata"] = {"component_queries": [{"query": "Q?", "answer": "A"}]}
        second = json.loads(json.dumps(first))
        second["testcase_id"] = "r5-hops_2-00000"
        tasks, links = component_tasks([first, second])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(len(links), 2)

    def test_mock_run_writes_scored_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            testcase_dir = root / "calibread_research" / "testcases"
            prompt_dir = root / "calibread_research" / "prompts"
            testcase_dir.mkdir(parents=True)
            prompt_dir.mkdir(parents=True)
            (testcase_dir / "r1_exposure_frequency.jsonl").write_text(json.dumps(record()) + "\n", encoding="utf-8")
            (prompt_dir / "read_system.txt").write_text("Return JSON.", encoding="utf-8")
            (prompt_dir / "p_true_system.txt").write_text("Return ptrue.", encoding="utf-8")
            (prompt_dir / "p_true_user_template.txt").write_text("{{query}} {{candidate_response}}", encoding="utf-8")
            config = {
                "api": {"api_key": "unused"},
                "model": {"id": "test/model", "provider": {"require_parameters": True}},
                "experiment": {
                    "run_id": "mock-run", "testcase_dir": str(testcase_dir),
                    "output_dir": str(root / "output"), "suites": ["R1"], "splits": ["fit"],
                    "evaluation_mode": "closed_book_external", "confirm_parametric_injection": False,
                    "include_r5_component_probes": False, "include_r4_second_turns": False,
                    "auxiliary_stochastic_samples": 0, "limit_per_suite": None, "shuffle_seed": 1,
                },
                "generation": {
                    "greedy_temperature": 0, "stochastic_samples": 2, "stochastic_temperature": 0.7,
                    "top_p": 0.95, "max_completion_tokens": 64, "seed": 1,
                    "request_logprobs": True, "structured_outputs": True,
                },
                "confidence": {"run_p_true": False, "primary_score": "exact_agreement"},
                "debug": {"contextual_max_documents": 10},
                "_config_sha256": "abc",
            }
            result = run_experiment(config, client=FakeClient())
            self.assertEqual(result["observations_scored"], 1)
            scored = (root / "output" / "scored_results.csv").read_text(encoding="utf-8")
            self.assertIn("false_commit_loss", scored)
            self.assertIn("Alpha Person", scored)
            with (root / "output" / "raw_generations.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                raw_rows = list(csv.DictReader(handle))
            hashes = {row["scientific_bundle_sha256"] for row in raw_rows}
            self.assertEqual(hashes, {result["scientific_bundle_sha256"]})
            self.assertTrue((root / "output" / "scientific_bundle_manifest.json").is_file())

    def test_p_true_logs_actual_request_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            testcase_dir, _ = self._project(root)
            config = self._config(root, testcase_dir)
            config["generation"]["stochastic_samples"] = 1
            config["generation"]["repeatability_repeats"] = 1
            config["generation"]["repeatability_limit_per_suite"] = 1
            config["confidence"]["run_p_true"] = True
            run_experiment(config, client=FakeClient())
            with (root / "output" / "raw_generations.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                rows = list(csv.DictReader(handle))
            p_row = next(row for row in rows if row["sample_kind"] == "p_true")
            self.assertEqual(float(p_row["top_p"]), 1.0)
            self.assertEqual(int(p_row["max_completion_tokens"]), 24)
            self.assertEqual(p_row["model_requested"], "test/model")
            for kind in ("greedy", "stochastic", "greedy_repeat"):
                row = next(item for item in rows if item["sample_kind"] == kind)
                self.assertEqual(float(row["top_p"]), 0.95)
                self.assertEqual(int(row["max_completion_tokens"]), 64)

    def test_prompt_and_testcase_mutation_refuse_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            testcase_dir, prompt_dir = self._project(root)
            config = self._config(root, testcase_dir)
            run_experiment(config, client=FakeClient())
            (prompt_dir / "read_system.txt").write_text("Return strict JSON.", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "different scientific bundle"):
                run_experiment(config, client=FakeClient())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            testcase_dir, _ = self._project(root)
            config = self._config(root, testcase_dir)
            run_experiment(config, client=FakeClient())
            path = testcase_dir / "r1_exposure_frequency.jsonl"
            changed = record()
            changed["query"] += " Changed."
            path.write_text(json.dumps(changed) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "different scientific bundle"):
                run_experiment(config, client=FakeClient())

    def test_bundle_ignores_secret_but_hashes_checkpoint_manifest_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            testcase_dir, _ = self._project(root)
            first = self._config(root, testcase_dir)
            second = json.loads(json.dumps(first))
            second["api"]["api_key"] = "different-secret"
            self.assertEqual(
                build_scientific_bundle(first)["scientific_bundle_sha256"],
                build_scientific_bundle(second)["scientific_bundle_sha256"],
            )
            checkpoint = root / "checkpoint.json"
            checkpoint.write_text(
                json.dumps({"checkpoint_sha256": "a", "corpus_sha256": "b"}),
                encoding="utf-8",
            )
            first["experiment"]["knowledge_checkpoint_manifest"] = str(checkpoint)
            before = build_scientific_bundle(first)["scientific_bundle_sha256"]
            checkpoint.write_text(
                json.dumps({"checkpoint_sha256": "changed", "corpus_sha256": "b"}),
                encoding="utf-8",
            )
            after = build_scientific_bundle(first)["scientific_bundle_sha256"]
            self.assertNotEqual(before, after)

    def test_confirmatory_provider_or_model_drift_fails_closed(self):
        config = {
            "api": {},
            "model": {
                "id": "test/model",
                "provider": {"only": ["frozen-provider"], "allow_fallbacks": False},
            },
            "experiment": {
                "evaluation_mode": "parametric_checkpoint",
                "confirm_parametric_injection": True,
            },
        }
        with self.assertRaisesRegex(ValueError, "provider identity mismatch"):
            _validate_response_identity(
                config,
                {"model_returned": "test/model", "provider_returned": "fallback-provider"},
                "test/model",
            )
        with self.assertRaisesRegex(ValueError, "model identity mismatch"):
            _validate_response_identity(
                config,
                {"model_returned": "other/model", "provider_returned": "frozen-provider"},
                "test/model",
            )

    def test_frozen_full_plan_request_estimate_is_408700(self):
        config = {
            "generation": {
                "stochastic_samples": 5,
                "repeatability_repeats": 1,
            },
            "experiment": {
                "include_r4_second_turns": True,
                "auxiliary_stochastic_samples": 0,
            },
            "confidence": {"run_p_true": False},
        }
        final_tasks = [
            {
                "observation_kind": "final",
                "repeatability_selected": index < 700,
                "query": "Q",
            }
            for index in range(62000)
        ]
        components = [
            {"observation_kind": "component", "query": "Q"}
            for _ in range(18000)
        ]
        records = []
        for ambiguity in (2, 3, 4):
            records.extend({
                "dimension_id": "R4",
                "expected_action": "clarify",
                "metadata": {"simulated_clarification_choices": ["x"] * ambiguity},
            } for _ in range(2000))
        estimate = estimate_requests(config, records, final_tasks + components)
        self.assertEqual(estimate["final_observations"], 62000)
        self.assertEqual(estimate["component_observations"], 18000)
        self.assertEqual(estimate["clarification_observations"], 18000)
        self.assertEqual(estimate["repeatability_requests"], 700)
        self.assertEqual(estimate["total_requests"], 408700)

    def test_r0_can_run_and_is_materialized_in_its_own_suite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = record("R0")
            item["level"] = "known_direct"
            testcase_dir, _ = self._project(root, "R0", item)
            config = self._config(root, testcase_dir, "R0")
            result = run_experiment(config, client=FakeClient())
            self.assertEqual(result["observations_scored"], 1)
            self.assertTrue(
                (root / "output" / "by_suite" / "R0" / "scored_results.csv").is_file()
            )

    def test_every_nonempty_output_table_carries_one_bundle_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = record("R5")
            item["level"] = "hops_2"
            item["factors"]["hops"] = 2
            item["metadata"] = {
                "component_queries": [
                    {"query": "Who is the custodian?", "answer": "Alpha Person"}
                ]
            }
            testcase_dir, _ = self._project(root, "R5", item)
            config = self._config(root, testcase_dir, "R5")
            config["experiment"]["include_r5_component_probes"] = True
            config["experiment"]["auxiliary_stochastic_samples"] = 0
            result = run_experiment(config, client=FakeClient())
            expected = result["scientific_bundle_sha256"]
            for filename in (
                "raw_generations.csv", "scored_results.csv", "candidate_sets.csv",
                "component_links.csv", "run_summary.csv",
            ):
                with (root / "output" / filename).open(
                    newline="", encoding="utf-8"
                ) as handle:
                    rows = list(csv.DictReader(handle))
                self.assertTrue(rows, filename)
                self.assertEqual(
                    {row["scientific_bundle_sha256"] for row in rows},
                    {expected},
                    filename,
                )

    def test_separate_split_runs_merge_observation_specs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            testcase_dir = root / "calibread_research" / "testcases"
            prompt_dir = root / "calibread_research" / "prompts"
            testcase_dir.mkdir(parents=True)
            prompt_dir.mkdir(parents=True)
            fit = record()
            tune = json.loads(json.dumps(fit))
            tune["testcase_id"] = "r1-exposure_16-00001"
            tune["world_id"] = "world-2"
            tune["split"] = "tune"
            (testcase_dir / "r1_exposure_frequency.jsonl").write_text(
                json.dumps(fit) + "\n" + json.dumps(tune) + "\n", encoding="utf-8"
            )
            (prompt_dir / "read_system.txt").write_text("Return JSON.", encoding="utf-8")
            (prompt_dir / "p_true_system.txt").write_text("Return ptrue.", encoding="utf-8")
            (prompt_dir / "p_true_user_template.txt").write_text("{{query}} {{candidate_response}}", encoding="utf-8")
            config = {
                "api": {"api_key": "unused"},
                "model": {"id": "test/model", "provider": {"require_parameters": True}},
                "experiment": {
                    "run_id": "merge-run", "testcase_dir": str(testcase_dir),
                    "output_dir": str(root / "output"), "suites": ["R1"], "splits": ["fit", "tune"],
                    "evaluation_mode": "closed_book_external", "confirm_parametric_injection": False,
                    "include_r5_component_probes": False, "include_r4_second_turns": False,
                    "auxiliary_stochastic_samples": 0, "limit_per_suite": None, "shuffle_seed": 1,
                },
                "generation": {
                    "greedy_temperature": 0, "stochastic_samples": 0, "stochastic_temperature": 0.7,
                    "top_p": 0.95, "max_completion_tokens": 64, "seed": 1,
                    "request_logprobs": True, "structured_outputs": True,
                },
                "confidence": {"run_p_true": False, "primary_score": "exact_agreement"},
                "debug": {"contextual_max_documents": 10},
                "_config_sha256": "merge-abc",
            }
            run_experiment(config, splits=["fit"], client=FakeClient())
            result = run_experiment(config, splits=["tune"], client=FakeClient())
            self.assertEqual(result["observations_scored"], 2)
            with (root / "output" / "scored_results.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual({row["split"] for row in rows}, {"fit", "tune"})


if __name__ == "__main__":
    unittest.main()
