#!/usr/bin/env python3
"""Unit tests for unified and stage-aware corpus materialization."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from materialize_training_corpus import materialize_program, write_corpus


class MaterializerTests(unittest.TestCase):
    def test_non_temporal_program_is_initial_only(self) -> None:
        knowledge = [{"subject": "A", "relation": "r", "object": "B"}]
        spec = {"exposure_count": 2, "training_templates": ["A r B."]}
        self.assertEqual(len(list(materialize_program(knowledge, spec, "initial"))), 2)
        self.assertEqual(len(list(materialize_program(knowledge, spec, "all"))), 2)
        self.assertEqual(list(materialize_program(knowledge, spec, "update")), [])

    def test_temporal_schedule_is_separated_by_stage(self) -> None:
        knowledge = [
            {"subject": "A", "relation": "r", "object": "old"},
            {"subject": "A", "relation": "r", "object": "new"},
        ]
        spec = {
            "training_schedule": [
                {"time": "T0", "operation": "insert", "value": "old", "exposure": 2},
                {"time": "T2", "operation": "update", "value": "new", "exposure": 3},
            ],
            "training_templates": ["old-1", "old-2", "new-1", "new-2"],
        }
        initial = list(materialize_program(knowledge, spec, "initial"))
        update = list(materialize_program(knowledge, spec, "update"))
        self.assertEqual([item["time"] for item in initial], ["T0", "T0"])
        self.assertEqual([item["time"] for item in update], ["T2", "T2", "T2"])
        self.assertTrue(all(item["text"].startswith("old-") for item in initial))
        self.assertTrue(all(item["text"].startswith("new-") for item in update))

    def test_repeated_input_files_form_one_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [root / "r1.jsonl", root / "r2.jsonl"]
            for index, path in enumerate(paths, 1):
                record = {
                    "testcase_id": f"case-{index}",
                    "world_id": f"world-{index}",
                    "dimension_id": f"R{index}",
                    "level": "level",
                    "split": "fit",
                    "knowledge": [{"subject": "A", "relation": "r", "object": str(index)}],
                    "injection_spec": {
                        "exposure_count": 1,
                        "training_templates": [f"A r {index}."],
                    },
                }
                path.write_text(json.dumps(record) + "\n", encoding="utf-8")

            report = write_corpus(
                paths,
                root / "corpus.jsonl",
                limit_worlds=None,
                shuffle_seed=7,
                levels=None,
                stage="initial",
            )
            self.assertEqual(report["selected_worlds"], 2)
            self.assertEqual(report["emitted_worlds"], 2)
            self.assertEqual(report["documents"], 2)
            self.assertEqual(
                report["ordering_policy"],
                "ascending_sha256_shuffle_key_then_document_id_v1",
            )
            output = root / "corpus.jsonl"
            rows = [
                json.loads(line)
                for line in output.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(
                [(row["shuffle_key"], row["document_id"]) for row in rows],
                sorted((row["shuffle_key"], row["document_id"]) for row in rows),
            )
            second = write_corpus(
                list(reversed(paths)),
                root / "corpus-second.jsonl",
                limit_worlds=None,
                shuffle_seed=7,
                levels=None,
                stage="initial",
            )
            self.assertEqual(report["sha256"], second["sha256"])
            self.assertEqual(
                output.read_bytes(),
                (root / "corpus-second.jsonl").read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
