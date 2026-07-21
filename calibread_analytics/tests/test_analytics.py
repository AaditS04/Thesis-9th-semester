from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import tempfile
import unittest
from pathlib import Path

from calibread_analytics.analysis import run_analysis
from calibread_analytics.cpr import conformal_rank_cutoff, evaluate_cpr
from calibread_analytics.data import (
    AnalysisConfigError,
    normalize_scored,
    validate_config,
)
from calibread_analytics.diagnostics import (
    clarification_recovery_summary,
    repeatability_summary,
    temporal_checkpoint_diagnostics,
)
from calibread_analytics.hypotheses import (
    _mixture_bootstrap,
    validated_primary_p_values,
)
from calibread_analytics.metrics import confidence_quality
from calibread_analytics.policy import inference_profile, mixture_weights, risk_interval
from calibread_analytics.preflight import audit_inputs
from calibread_analytics.stats import clopper_pearson, holm_adjust, pava_increasing


class StatisticalPrimitiveTests(unittest.TestCase):
    def test_pava_is_monotone(self):
        fitted = pava_increasing([8, 2, 9], [10, 10, 10])
        self.assertLessEqual(fitted[0], fitted[1])
        self.assertLessEqual(fitted[1], fitted[2])

    def test_exact_interval_contains_rate(self):
        low, high = clopper_pearson(5, 100, 0.05)
        self.assertLess(low, 0.05)
        self.assertGreater(high, 0.05)

    def test_holm_is_monotone_in_rank(self):
        adjusted = holm_adjust({"H1": 0.001, "H2": 0.02, "H3": 0.5})
        self.assertLessEqual(adjusted["H1"], adjusted["H2"])
        self.assertLessEqual(adjusted["H2"], adjusted["H3"])

    def test_equal_suite_level_mixture_weights_sum_to_one(self):
        rows = [
            {"dimension_id": "R1", "level": "a"},
            {"dimension_id": "R1", "level": "b"},
            {"dimension_id": "R2", "level": "a"},
            {"dimension_id": "R2", "level": "a"},
        ]
        weights = mixture_weights(rows, "aggregate")
        self.assertAlmostEqual(sum(weights), 1.0)
        self.assertAlmostEqual(weights[0] + weights[1], 0.5)

    def test_cpr_rank_calibration(self):
        calibration = []
        for index, rank in enumerate([1, 1, 2, 1, 2]):
            calibration.append({
                "observation_id": f"c{index}", "testcase_id": f"c{index}", "world_id": f"w{index}",
                "dimension_id": "R1", "level": "x", "split": "calibrate", "candidate_rank": rank,
                "candidate_answer": "a", "is_correct_candidate": 1, "n_answer_samples": 3,
            })
        rule = conformal_rank_cutoff(calibration, 0.2, 3)
        self.assertIn(rule["rank_cutoff"], {1, 2, 4})
        self.assertEqual(rule["missing_rank"], 4)

    def test_temporal_update_is_paired_by_world(self):
        base = {
            "model_id": "family", "observation_kind": "final", "dimension_id": "R3",
            "level": "current_after_update", "split": "test", "world_id": "world-1",
            "parsed_action": "ANSWER",
        }
        t0 = {**base, "analysis_role": "secondary_temporal", "checkpoint_stage": "checkpoint_t0", "commit_correct": 0, "stale_answer": 1}
        t2 = {**base, "analysis_role": "primary", "checkpoint_stage": "checkpoint_t2", "commit_correct": 1, "stale_answer": 0}
        _, paired = temporal_checkpoint_diagnostics([t0, t2], 100, 1)
        self.assertEqual(len(paired), 1)
        self.assertEqual(paired[0]["current_accuracy_gain"], 1)
        self.assertEqual(paired[0]["stale_rate_change"], -1)

    def test_confidence_quality_perfect_ranking(self):
        rows = [
            {"observation_kind": "final", "split": "test", "model_id": "m", "dimension_id": "R1", "answer_attempted": 1, "commit_correct": 1, "confidence_score": 0.9},
            {"observation_kind": "final", "split": "test", "model_id": "m", "dimension_id": "R1", "answer_attempted": 1, "commit_correct": 0, "confidence_score": 0.1},
        ]
        result = confidence_quality(rows, "confidence_score", 5)
        aggregate = next(row for row in result if row["scope"] == "aggregate")
        self.assertEqual(aggregate["roc_auc_correctness"], 1.0)
        self.assertEqual(aggregate["average_precision_correctness"], 1.0)

    def test_cluster_bound_does_not_gain_effective_n_from_duplicate_level_row(self):
        base = [
            {"run_id": "r", "world_id": "w1", "dimension_id": "R2", "level": "a"},
            {"run_id": "r", "world_id": "w1", "dimension_id": "R2", "level": "b"},
            {"run_id": "r", "world_id": "w2", "dimension_id": "R2", "level": "a"},
            {"run_id": "r", "world_id": "w2", "dimension_id": "R2", "level": "b"},
        ]
        original = risk_interval(base, [1, 1, 0, 0], "aggregate", 0.05)
        duplicate = risk_interval(
            base + [{**base[0]}], [1, 1, 0, 0, 1], "aggregate", 0.05
        )
        self.assertLessEqual(duplicate[3], original[3])
        self.assertGreaterEqual(
            duplicate[2] - duplicate[1],
            original[2] - original[1],
        )
        self.assertEqual(original[5], 2)

    def test_cluster_bound_is_order_invariant_and_exact_for_one_row_worlds(self):
        rows = [
            {"run_id": "r", "world_id": f"w{i}", "dimension_id": "R1", "level": "a"}
            for i in range(10)
        ]
        losses = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        first = risk_interval(rows, losses, "aggregate", 0.05)
        permutation = list(reversed(list(zip(rows, losses))))
        second = risk_interval(
            [item[0] for item in permutation],
            [item[1] for item in permutation],
            "aggregate",
            0.05,
        )
        self.assertEqual(first, second)
        self.assertEqual(first[4], "independent_world_exact_binomial")
        self.assertEqual(first[3], 10.0)

    def test_cluster_hoeffding_covers_perfect_within_world_correlation(self):
        rng = random.Random(19)
        covered = 0
        repetitions = 300
        true_risk = 0.1
        for _ in range(repetitions):
            rows = []
            losses = []
            for world in range(100):
                loss = int(rng.random() < true_risk)
                for level in ("a", "b"):
                    rows.append({
                        "run_id": "r", "world_id": f"w{world}",
                        "dimension_id": "R2", "level": level,
                    })
                    losses.append(loss)
            _, _, upper, _, method, _ = risk_interval(
                rows, losses, "aggregate", 0.05
            )
            self.assertEqual(method, "independent_world_weighted_hoeffding")
            covered += int(upper >= true_risk)
        self.assertGreaterEqual(covered / repetitions, 0.95)

    def test_zero_p_value_is_preserved_and_invalid_values_fail(self):
        values = validated_primary_p_values([
            {"hypothesis_id": "H1", "p_value_raw": 0.0},
            {"hypothesis_id": "H2", "p_value_raw": None},
        ])
        self.assertEqual(values, {"H1": 0.0, "H2": 1.0})
        self.assertEqual(holm_adjust(values)["H1"], 0.0)
        for invalid in (math.nan, math.inf, -0.1, 1.1):
            with self.assertRaises(ValueError):
                validated_primary_p_values([
                    {"hypothesis_id": "H1", "p_value_raw": invalid}
                ])

    def test_paired_mixture_bootstrap_preserves_perfect_level_correlation(self):
        rows = []
        for world, value in (("w0", 0.0), ("w1", 1.0)):
            for level in ("a", "b"):
                rows.append(({
                    "run_id": "r", "world_id": world,
                    "dimension_id": "R2", "level": level,
                }, value))
        observed, draws = _mixture_bootstrap(rows, 200, 7)
        self.assertEqual(observed, 0.5)
        self.assertTrue(set(draws) <= {0.0, 0.5, 1.0})
        reordered = list(reversed(rows))
        self.assertEqual(
            _mixture_bootstrap(reordered, 200, 7),
            (observed, draws),
        )

    def test_profile_rules_cover_every_r2_query_form(self):
        expected = {
            "categorical": "ordinary",
            "year": "ordinary",
            "month_year": "ordinary",
            "exact_date": "precision",
            "integer": "precision",
            "decimal_1": "precision",
            "decimal_3": "precision",
            "decimal_5": "precision",
        }
        root = Path(__file__).resolve().parents[2]
        counts = {level: 0 for level in expected}
        with (
            root / "calibread_research" / "testcases" / "r2_precision.jsonl"
        ).open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                self.assertEqual(inference_profile(row["query"]), expected[row["level"]])
                counts[row["level"]] += 1
        self.assertEqual(counts["decimal_5"], 2000)
        self.assertTrue(all(value == 2000 for value in counts.values()))

    def test_cpr_keeps_runs_separate_and_support_is_frozen(self):
        rows = []
        for run in ("run-a", "run-b"):
            rows.append({
                "run_id": run, "model_id": "m", "observation_id": "same",
                "testcase_id": "same", "world_id": run, "dimension_id": "R1",
                "level": "x", "split": "calibrate", "candidate_rank": 1,
                "candidate_answer": "a", "is_correct_candidate": 1,
            })
        rule = conformal_rank_cutoff(rows, 0.1, 6)
        self.assertEqual(rule["calibration_n"], 2)
        self.assertEqual(rule["missing_rank"], 7)
        only_low_rank = [dict(item) for item in rows]
        self.assertEqual(
            conformal_rank_cutoff(only_low_rank, 0.1, 6)["missing_rank"],
            7,
        )

    def test_cpr_exchangeable_rank_simulation_attains_marginal_coverage(self):
        rng = random.Random(23)
        coverages = []
        for trial in range(80):
            candidates = []
            for split, total in (("calibrate", 80), ("test", 160)):
                for index in range(total):
                    true_rank = rng.randint(1, 6)
                    observation = f"{trial}-{split}-{index}"
                    for rank in range(1, 7):
                        candidates.append({
                            "run_id": f"run-{trial}", "model_id": "m",
                            "observation_id": observation, "testcase_id": observation,
                            "world_id": observation, "dimension_id": "R1", "level": "x",
                            "split": split, "candidate_rank": rank,
                            "candidate_answer": str(rank),
                            "is_correct_candidate": int(rank == true_rank),
                        })
            calibration = conformal_rank_cutoff(
                [row for row in candidates if row["split"] == "calibrate"],
                0.1,
                6,
            )
            _, summary = evaluate_cpr(
                [row for row in candidates if row["split"] == "test"],
                calibration,
                "m",
            )
            coverages.append(summary["empirical_coverage"])
        self.assertGreaterEqual(sum(coverages) / len(coverages), 0.88)

    def test_repeatability_metric_has_unambiguous_name(self):
        rows = [
            {
                "status": "success", "sample_kind": "greedy",
                "run_id": "r", "observation_id": "o", "model_returned": "m",
                "provider_returned": "p", "system_fingerprint": "f",
                "analysis_role": "primary", "checkpoint_stage": "checkpoint_t2",
                "dimension_id": "R1", "raw_output": "x", "request_seed": "1",
                "temperature": "0", "top_p": "1", "max_completion_tokens": "64",
            },
            {
                "status": "success", "sample_kind": "greedy_repeat",
                "run_id": "r", "observation_id": "o", "model_returned": "m",
                "provider_returned": "p", "system_fingerprint": "f",
                "analysis_role": "primary", "checkpoint_stage": "checkpoint_t2",
                "dimension_id": "R1", "raw_output": "x", "request_seed": "1",
                "temperature": "0", "top_p": "1", "max_completion_tokens": "64",
            },
        ]
        result = repeatability_summary(rows)[0]
        self.assertIn("all_repeats_exactly_identical_rate", result)
        self.assertIn("pairwise_exact_agreement", result)

    def test_clarification_report_separates_forced_from_end_to_end(self):
        rows = [
            {
                "model_id": "m", "level": "interpretations_2", "split": "test",
                "observation_kind": "clarification",
                "forced_clarification_recovery": 1,
                "end_to_end_clarification_success": 0,
            },
            {
                "model_id": "m", "level": "interpretations_2", "split": "test",
                "observation_kind": "clarification",
                "forced_clarification_recovery": 1,
                "end_to_end_clarification_success": 1,
            },
        ]
        result = clarification_recovery_summary(rows)[0]
        self.assertEqual(result["forced_clarification_recovery_rate"], 1.0)
        self.assertEqual(result["end_to_end_clarification_success_rate"], 0.5)


class ConfirmatoryPreflightTests(unittest.TestCase):
    @staticmethod
    def _write_csv(path: Path, rows, fields=None):
        fields = fields or sorted({key for row in rows for key in row})
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    @classmethod
    def _source(cls, root: Path, name: str, role: str, stage: str, rows):
        source = root / name
        source.mkdir()
        unsigned_bundle = {"bundle_version": "test", "source_name": name}
        bundle = hashlib.sha256(
            json.dumps(
                unsigned_bundle, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        config_hash = f"config-{name}"
        complete_rows = []
        raw = []
        candidates = []
        for index, row in enumerate(rows):
            observation = f"{name}-o{index}"
            full = {
                "run_id": name, "observation_id": observation,
                "testcase_id": observation, "parent_testcase_id": "",
                "world_id": f"{name}-w{index}", "dimension_id": row["dimension_id"],
                "level": row["level"], "split": row.get("split", "fit"),
                "observation_kind": "final", "model_id": "m",
                "model_returned": "endpoint", "provider_returned": "provider",
                "scientific_status": "confirmatory_parametric",
                "analysis_role": role, "checkpoint_stage": stage,
                "config_sha256": config_hash,
                "scientific_bundle_sha256": bundle,
                "confidence_method": "exact_agreement", "confidence_available": 1,
                "confidence_score": 0.9, "factual_correct": row.get("correct", 1),
                "action_correct": row.get("action_correct", 1),
                "commit_correct": row.get("correct", 1),
                "answer_attempted": 1, "false_commit_loss": 1 - row.get("correct", 1),
                "stale_answer": 0, "n_generation_samples": 6, "n_answer_samples": 6,
                "exact_agreement": 0.9, "exact_answer_entropy": 0.1,
                "query": "Question", "expected_action": "ANSWER",
                "greedy_answer": "A", "parsed_action": "ANSWER",
                "normalized_answer": "a", "parser_status": "ok",
                "valid_answers_json": '["A"]',
                "factors_json": json.dumps({
                    "exposure": 16, "precision": "categorical",
                    "temporal_status": "stable", "ambiguity": 1,
                    "hops": 1, "domain": "general",
                }),
            }
            complete_rows.append(full)
            raw.append({
                "run_id": name, "observation_id": observation,
                "sample_kind": "greedy", "sample_index": 0, "status": "success",
                "model_returned": "endpoint", "provider_returned": "provider",
                "scientific_bundle_sha256": bundle,
                "request_seed": 1, "temperature": 0, "top_p": 1,
                "max_completion_tokens": 64, "attempt_count": 1,
                "input_tokens": 1, "output_tokens": 1, "total_tokens": 2,
                "cost_credits": 0, "latency_ms": 1,
            })
            if (
                role == "primary"
                and full["dimension_id"] in {f"R{i}" for i in range(1, 7)}
                and full["split"] in {"calibrate", "test"}
            ):
                candidates.append({
                    "run_id": name, "model_id": "m",
                    "observation_id": observation,
                    "candidate_rank": 1, "candidate_count": 6,
                    "candidate_mass": 1.0, "is_greedy_candidate": 1,
                    "is_correct_candidate": 1, "n_answer_samples": 6,
                    "operationally_unique": 1, "split": full["split"],
                    "config_sha256": config_hash,
                    "scientific_bundle_sha256": bundle,
                })
        cls._write_csv(source / "scored_results.csv", complete_rows)
        cls._write_csv(source / "raw_generations.csv", raw)
        cls._write_csv(
            source / "candidate_sets.csv",
            candidates,
            fields=[
                "run_id", "model_id", "observation_id", "candidate_rank",
                "candidate_count", "candidate_mass", "is_greedy_candidate",
                "is_correct_candidate", "n_answer_samples",
                "operationally_unique", "split",
                "config_sha256", "scientific_bundle_sha256",
            ],
        )
        cls._write_csv(
            source / "component_links.csv", [],
            fields=[
                "run_id", "parent_testcase_id", "component_observation_id",
                "component_index",
            ],
        )
        cls._write_csv(source / "run_summary.csv", [{
            "observations_expected": len(rows),
            "observations_scored": len(rows),
            "config_sha256": config_hash,
            "scientific_bundle_sha256": bundle,
        }])
        (source / "resolved_config.redacted.json").write_text(
            json.dumps({
                "_config_sha256": config_hash,
                "model": {
                    "id": "endpoint",
                    "analysis_id": "m",
                    "provider": {
                        "only": ["provider"],
                        "allow_fallbacks": False,
                    },
                },
            }),
            encoding="utf-8",
        )
        (source / "model_metadata.json").write_text("{}", encoding="utf-8")
        (source / "scientific_bundle_manifest.json").write_text(
            json.dumps({
                **unsigned_bundle,
                "scientific_bundle_sha256": bundle,
            }),
            encoding="utf-8",
        )
        (source / "observation_specs.jsonl").write_text(
            "".join("{}\n" for _ in rows), encoding="utf-8"
        )
        return source

    @classmethod
    def _valid_config(cls, root: Path):
        primary = cls._source(root, "primary", "primary", "checkpoint_t2", [
            {"dimension_id": "R1", "level": "exposure_1", "split": "calibrate"},
            {"dimension_id": "R1", "level": "exposure_16", "split": "test"},
        ])
        temporal = cls._source(
            root, "temporal", "secondary_temporal", "checkpoint_t0",
            [{"dimension_id": "R3", "level": "current_after_update", "split": "calibrate"}],
        )
        gate_rows = [
            {"dimension_id": "R0", "level": level, "split": "fit"}
            for level in (
                "known_direct", "known_paraphrase",
                "unknown_entity", "false_premise",
            )
        ]
        gate_t2 = cls._source(
            root, "gate-t2", "checkpoint_gate", "checkpoint_t2", gate_rows
        )
        gate_t0 = cls._source(
            root, "gate-t0", "checkpoint_gate", "checkpoint_t0", gate_rows
        )
        return {
            "inputs": [str(primary), str(temporal), str(gate_t2), str(gate_t0)],
            "output_dir": str(root / "assets"),
            "analysis": {
                "r0_gate": {
                    "known_direct_min": 0.70,
                    "direct_to_paraphrase_max_loss": 0.20,
                    "manual_grading_agreement": {
                        "m|checkpoint_t2": 1.0,
                        "m|checkpoint_t0": 1.0,
                    },
                    "no_split_crossing": True,
                },
            },
            "confirmatory": {"allow_incomplete_exploratory": False},
        }

    def test_valid_primary_t2_secondary_t0_and_r0_gates_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            config = self._valid_config(Path(directory))
            artifacts, audit, _ = audit_inputs(config)
            self.assertTrue(audit["confirmatory_eligible"])
            self.assertEqual(
                len([row for row in artifacts["scored"] if row["analysis_role"] == "primary"]),
                2,
            )
            self.assertEqual(
                len([row for row in artifacts["scored"] if row["analysis_role"] == "secondary_temporal"]),
                1,
            )

    def test_missing_artifact_duplicate_row_t0_primary_and_bundle_mismatch_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = self._valid_config(root)
            (Path(config["inputs"][0]) / "candidate_sets.csv").unlink()
            with self.assertRaisesRegex(AnalysisConfigError, "missing required artifacts"):
                audit_inputs(config)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = self._valid_config(root)
            scored_path = Path(config["inputs"][0]) / "scored_results.csv"
            with scored_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self._write_csv(scored_path, rows + [rows[0]])
            with self.assertRaisesRegex(AnalysisConfigError, "duplicate scored observation"):
                audit_inputs(config)
            with self.assertRaises(AnalysisConfigError):
                run_analysis(config)
            self.assertFalse(Path(config["output_dir"]).exists())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = self._valid_config(root)
            scored_path = Path(config["inputs"][0]) / "scored_results.csv"
            with scored_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            for row in rows:
                row["checkpoint_stage"] = "checkpoint_t0"
            self._write_csv(scored_path, rows)
            with self.assertRaisesRegex(AnalysisConfigError, "not checkpoint_t2"):
                audit_inputs(config)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = self._valid_config(root)
            bundle_path = Path(config["inputs"][0]) / "scientific_bundle_manifest.json"
            bundle_path.write_text(
                json.dumps({"scientific_bundle_sha256": "wrong"}), encoding="utf-8"
            )
            with self.assertRaisesRegex(AnalysisConfigError, "bundle hash does not match"):
                audit_inputs(config)

    def test_duplicate_input_and_malformed_numeric_or_json_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "run"
            source.mkdir()
            (source / "scored_results.csv").write_text("x\n", encoding="utf-8")
            config = {
                "inputs": [str(source), str(source)],
                "analysis": {
                    "target_false_commit_risk": 0.05,
                    "calibration_confidence": 0.95,
                    "cpr_alpha": 0.1,
                    "candidate_draw_budget": 6,
                    "bootstrap_replicates": 100,
                },
            }
            with self.assertRaisesRegex(AnalysisConfigError, "Duplicate input"):
                validate_config(config)

        row = {
            "factual_correct": 1, "action_correct": 1, "commit_correct": 1,
            "answer_attempted": 1, "false_commit_loss": "corrupt",
            "stale_answer": 0, "n_generation_samples": 1, "n_answer_samples": 1,
            "confidence_available": 1, "factors_json": "{}",
            "valid_answers_json": "[]",
        }
        with self.assertRaisesRegex(AnalysisConfigError, "false_commit_loss"):
            normalize_scored([row], strict=True)
        row["false_commit_loss"] = 0
        row["factors_json"] = ""
        with self.assertRaisesRegex(AnalysisConfigError, "factors_json"):
            normalize_scored([row], strict=True)


class EndToEndAnalysisTests(unittest.TestCase):
    def test_mock_analysis_writes_paper_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "run"
            run.mkdir()
            scored = []
            candidates = []
            exposures = [0, 1, 2, 4, 8, 16, 32]
            for index, exposure in enumerate(exposures):
                for split in ("fit", "tune", "calibrate", "test"):
                    row = self._row(f"r1-{split}-{exposure}", "R1", f"exposure_{exposure}", split, {"exposure": exposure}, int(exposure >= 4))
                    scored.append(row)
                    if split in {"calibrate", "test"}:
                        candidates.append(self._candidate(row))
            for dimension, level, factors in (
                ("R2", "exact_date", {"precision": "exact_date"}),
                ("R3", "superseded_stale", {"temporal_status": "superseded_stale"}),
                ("R4", "interpretations_3", {"ambiguity": 3}),
                ("R5", "hops_4", {"hops": 4}),
                ("R6", "general", {"domain": "general"}),
                ("R7", "easy_known", {}),
            ):
                for split in ("fit", "tune", "calibrate", "test"):
                    row = self._row(f"{dimension}-{split}", dimension, level, split, factors, 1)
                    scored.append(row)
                    if split in {"calibrate", "test"}:
                        candidates.append(self._candidate(row))
            scored.append(self._row(
                "R0-fit", "R0", "known_direct", "fit", {}, 1
            ))
            self._write(run / "scored_results.csv", scored)
            self._write(run / "candidate_sets.csv", candidates)
            self._write(run / "component_links.csv", [])
            config = {
                "inputs": [str(run)], "output_dir": str(root / "assets"), "primary_model_id": "test/model",
                "analysis": {
                    "confidence_column": "confidence_score", "target_false_commit_risk": 0.05,
                    "calibration_confidence": 0.95, "cpr_alpha": 0.2,
                    "candidate_draw_budget": 6, "threshold_start": 0,
                    "threshold_stop": 1, "threshold_step": 0.5, "bootstrap_replicates": 100,
                    "permutation_replicates": 100, "random_seed": 1, "ece_bins": 5, "minimum_group_n": 1,
                },
                "confirmatory": {
                    "require_parametric_status": True,
                    "allowed_statuses": ["confirmatory_parametric"],
                    "allow_incomplete_exploratory": True,
                },
                "paper": {"title": "Test", "analysis_version": "test-v1"},
                "_config_sha256": "abc",
            }
            result = run_analysis(config)
            self.assertTrue((root / "assets" / "figures" / "fig_h_complexity.svg").is_file())
            self.assertTrue((root / "assets" / "tables" / "hypothesis_results.csv").is_file())
            self.assertEqual(result["hypothesis_decisions"]["H1"], "NOT_CONFIRMATORY")
            audit = json.loads((root / "assets" / "input_audit.json").read_text())
            self.assertEqual(audit["analysis_mode"], "EXPLORATORY_INCOMPLETE_ALLOWED")
            self.assertEqual(
                audit["analysis_output_status"],
                "NONCONFIRMATORY_INCOMPLETE_INPUT",
            )
            self.assertEqual(
                result["analysis_output_status"],
                "NONCONFIRMATORY_INCOMPLETE_INPUT",
            )
            with (root / "assets" / "tables" / "hallucination_index.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                self.assertNotIn("R0", {row["dimension_id"] for row in csv.DictReader(handle)})
            with self.assertRaisesRegex(ValueError, "must not already exist"):
                run_analysis(config)
            first_manifest = json.loads(
                (root / "assets" / "analysis_manifest.json").read_text()
            )
            for item in first_manifest["files"]:
                artifact = root / "assets" / item["path"]
                self.assertTrue(artifact.is_file())
                self.assertEqual(
                    hashlib.sha256(artifact.read_bytes()).hexdigest(),
                    item["sha256"],
                )
            scored_path = run / "scored_results.csv"
            scored_path.write_text(
                scored_path.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            second_config = json.loads(json.dumps(config))
            second_config["output_dir"] = str(root / "assets-second")
            run_analysis(second_config)
            second_manifest = json.loads(
                (root / "assets-second" / "analysis_manifest.json").read_text()
            )
            first_hash = first_manifest["source_artifacts"][0][
                "source_files_sha256"
            ]["scored_results.csv"]
            second_hash = second_manifest["source_artifacts"][0][
                "source_files_sha256"
            ]["scored_results.csv"]
            self.assertNotEqual(first_hash, second_hash)

    @staticmethod
    def _row(testcase_id, dimension, level, split, factors, correct):
        complete = {"exposure": 16, "precision": "categorical", "temporal_status": "stable", "ambiguity": 1, "hops": 1, "domain": "general"}
        complete.update(factors)
        return {
            "run_id": "run1", "observation_id": testcase_id, "testcase_id": testcase_id,
            "parent_testcase_id": "", "world_id": testcase_id, "dimension_id": dimension,
            "level": level, "split": split, "observation_kind": "final", "model_id": "test/model",
            "scientific_status": "external_zero_shot_nonconfirmatory", "query": f"Question {dimension} {level}",
            "analysis_role": "primary", "checkpoint_stage": "unspecified",
            "config_sha256": "config", "scientific_bundle_sha256": "bundle",
            "provider_returned": "provider",
            "expected_action": "ANSWER", "greedy_answer": "A", "parsed_action": "ANSWER",
            "factual_correct": correct, "action_correct": 1, "commit_correct": correct,
            "answer_attempted": 1, "false_commit_loss": 1 - correct, "stale_answer": 0,
            "n_generation_samples": 6, "n_answer_samples": 6, "exact_agreement": 0.8,
            "exact_answer_entropy": 0.2, "confidence_score": 0.8,
            "confidence_method": "exact_agreement", "confidence_available": 1,
            "latency_ms_total": 1,
            "input_tokens_total": 10, "output_tokens_total": 5, "cost_credits_total": 0.001,
            "factors_json": json.dumps(complete), "valid_answers_json": '["A"]',
        }

    @staticmethod
    def _candidate(row):
        return {
            "run_id": row["run_id"], "observation_id": row["observation_id"],
            "testcase_id": row["testcase_id"], "world_id": row["world_id"],
            "dimension_id": row["dimension_id"], "level": row["level"], "split": row["split"],
            "observation_kind": "final", "model_id": row["model_id"],
            "scientific_status": row["scientific_status"], "candidate_rank": 1,
            "analysis_role": row["analysis_role"],
            "checkpoint_stage": row["checkpoint_stage"],
            "config_sha256": row["config_sha256"],
            "scientific_bundle_sha256": row["scientific_bundle_sha256"],
            "operationally_unique": 1,
            "candidate_answer": "A", "normalized_candidate": "a", "candidate_count": 6,
            "candidate_mass": 1, "is_greedy_candidate": 1,
            "is_correct_candidate": row["factual_correct"], "n_answer_samples": 6,
        }

    @staticmethod
    def _write(path, rows):
        fields = sorted({key for row in rows for key in row}) if rows else ["run_id"]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
