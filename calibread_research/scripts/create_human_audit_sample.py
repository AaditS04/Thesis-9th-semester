#!/usr/bin/env python3
"""Create a deterministic, level-stratified testcase audit sheet."""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any


FIELDS = [
    "source_file", "testcase_id", "dimension_id", "level", "world_id", "split",
    "query", "expected_action", "valid_answers_json", "knowledge_json",
    "injection_spec_json", "query_grammatical_yes_no",
    "label_follows_from_world_yes_no", "expected_action_correct_yes_no",
    "no_unintended_interpretation_yes_no", "no_answer_leakage_yes_no", "reviewer",
    "review_status_accept_reject", "issue_code", "notes",
]


def allocate(total: int, levels: list[str]) -> dict[str, int]:
    base, remainder = divmod(total, len(levels))
    return {
        level: base + (1 if index < remainder else 0)
        for index, level in enumerate(levels)
    }


def sample_file(
    path: Path,
    per_file: int,
    seed: int,
    splits: set[str],
) -> list[dict[str, Any]]:
    by_level: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record["split"] not in splits:
                continue
            by_level[record["level"]].append(record)
    levels = sorted(by_level)
    selected = []
    for level, count in allocate(per_file, levels).items():
        rng = random.Random(f"{seed}|{path.name}|{level}")
        if count > len(by_level[level]):
            raise ValueError(f"{path.name}/{level}: requested {count}, available {len(by_level[level])}")
        selected.extend(rng.sample(by_level[level], count))
    return sorted(selected, key=lambda item: (item["level"], item["testcase_id"]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--testcase-dir", type=Path,
        default=Path(__file__).resolve().parents[1] / "testcases",
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parents[1] / "testcases" / "human_audit_sample.csv",
    )
    parser.add_argument("--per-file", type=int, default=25)
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument(
        "--split",
        action="append",
        choices=("fit", "tune", "calibrate", "test"),
        help="eligible split; repeat as needed (default: fit and tune only)",
    )
    args = parser.parse_args()
    if args.per_file <= 0:
        parser.error("--per-file must be positive")

    selected_splits = set(args.split or ("fit", "tune"))
    testcase_files = sorted(args.testcase_dir.glob("r[0-7]_*.jsonl"))
    if len(testcase_files) != 8:
        raise ValueError(f"expected eight R0-R7 files, found {len(testcase_files)}")
    rows = []
    for path in testcase_files:
        for record in sample_file(path, args.per_file, args.seed, selected_splits):
            rows.append({
                "source_file": path.name,
                "testcase_id": record["testcase_id"],
                "dimension_id": record["dimension_id"],
                "level": record["level"],
                "world_id": record["world_id"],
                "split": record["split"],
                "query": record["query"],
                "expected_action": record["expected_action"],
                "valid_answers_json": json.dumps(record["valid_answers"], ensure_ascii=False),
                "knowledge_json": json.dumps(record["knowledge"], ensure_ascii=False, sort_keys=True),
                "injection_spec_json": json.dumps(record["injection_spec"], ensure_ascii=False, sort_keys=True),
            })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=args.output.parent,
        prefix=f".{args.output.name}.", delete=False,
    ) as handle:
        temp_path = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, args.output)
    os.chmod(args.output, 0o644)
    print(json.dumps({
        "output": str(args.output),
        "rows": len(rows),
        "eligible_splits": sorted(selected_splits),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
