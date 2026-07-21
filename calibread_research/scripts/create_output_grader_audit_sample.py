#!/usr/bin/env python3
"""Create the frozen 100-R0/200-R1–R7 blinded grader-audit sample."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


BLINDED_FIELDS = [
    "blinding_id", "dimension_id", "level", "query", "expected_action",
    "valid_answers_json", "raw_output", "human_parser_status", "human_action",
    "human_normalized_answer", "human_factual_correct", "human_action_correct",
    "human_commit_correct", "human_false_commit_loss", "reviewer", "issue_code",
    "adjudication", "adjudicator", "rubric_version", "notes",
]

KEY_FIELDS = [
    "blinding_id", "source_dir", "run_id", "observation_id", "testcase_id",
    "world_id", "dimension_id", "level", "split", "automated_parser_status",
    "automated_action", "automated_normalized_answer", "automated_factual_correct",
    "automated_action_correct", "automated_commit_correct",
    "automated_false_commit_loss", "grader_version", "config_sha256",
    "scientific_bundle_sha256",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"missing required grader-audit input: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_development_rows(run_dirs: Iterable[Path]) -> list[dict[str, Any]]:
    combined: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for source in run_dirs:
        source = source.resolve()
        scored = read_csv(source / "scored_results.csv")
        raw = read_csv(source / "raw_generations.csv")
        greedy: dict[tuple[str, str], dict[str, str]] = {}
        for row in raw:
            if row.get("status") == "success" and row.get("sample_kind") == "greedy":
                key = (row.get("run_id", ""), row.get("observation_id", ""))
                if key in greedy:
                    raise ValueError(f"duplicate greedy raw row in {source}: {key}")
                greedy[key] = row
        for row in scored:
            if row.get("split") not in {"fit", "tune", "calibrate"}:
                continue
            if row.get("observation_kind") != "final":
                continue
            identity = (str(source), row.get("run_id", ""), row.get("observation_id", ""))
            if identity in seen:
                raise ValueError(f"duplicate audit population row: {identity}")
            seen.add(identity)
            raw_row = greedy.get((row.get("run_id", ""), row.get("observation_id", "")))
            if raw_row is None:
                raise ValueError(f"missing greedy generation for audit population row {identity}")
            combined.append({**row, "source_dir": str(source), "raw_output": raw_row.get("raw_output", "")})
    return combined


def stratified_sample(
    rows: list[dict[str, Any]],
    total: int,
    seed: int,
    label: str,
) -> list[dict[str, Any]]:
    strata: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        strata[(row["dimension_id"], row["level"], row["expected_action"])].append(row)
    if len(rows) < total:
        raise ValueError(f"{label}: requested {total} audit rows, only {len(rows)} available")
    queues: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for stratum, items in strata.items():
        rng = random.Random(f"{seed}|{label}|{stratum}")
        queues[stratum] = sorted(items, key=lambda row: row["observation_id"])
        rng.shuffle(queues[stratum])
    selected: list[dict[str, Any]] = []
    ordered = sorted(queues)
    while len(selected) < total:
        made_progress = False
        for stratum in ordered:
            if queues[stratum] and len(selected) < total:
                selected.append(queues[stratum].pop())
                made_progress = True
        if not made_progress:
            raise ValueError(f"{label}: exhausted strata before reaching {total}")
    return selected


def blinding_id(seed: int, row: dict[str, Any]) -> str:
    payload = f"{seed}|{row['source_dir']}|{row['run_id']}|{row['observation_id']}"
    return "AUD-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def write_csv_atomic(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent,
        prefix=f".{path.name}.", delete=False,
    ) as handle:
        temp_path = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--r0-count", type=int, default=100)
    parser.add_argument("--r1-r7-count", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260722)
    args = parser.parse_args()
    if args.r0_count <= 0 or args.r1_r7_count <= 0:
        parser.error("audit counts must be positive")
    population = load_development_rows(args.run_dir)
    selected = stratified_sample(
        [row for row in population if row["dimension_id"] == "R0"],
        args.r0_count, args.seed, "R0",
    ) + stratified_sample(
        [row for row in population if row["dimension_id"] in {f"R{i}" for i in range(1, 8)}],
        args.r1_r7_count, args.seed, "R1-R7",
    )
    blinded_rows = []
    key_rows = []
    for row in selected:
        blind_id = blinding_id(args.seed, row)
        blinded_rows.append({
            "blinding_id": blind_id,
            "dimension_id": row["dimension_id"],
            "level": row["level"],
            "query": row["query"],
            "expected_action": row["expected_action"],
            "valid_answers_json": row["valid_answers_json"],
            "raw_output": row["raw_output"],
        })
        key_rows.append({
            "blinding_id": blind_id,
            "source_dir": row["source_dir"],
            "run_id": row["run_id"],
            "observation_id": row["observation_id"],
            "testcase_id": row["testcase_id"],
            "world_id": row["world_id"],
            "dimension_id": row["dimension_id"],
            "level": row["level"],
            "split": row["split"],
            "automated_parser_status": row["parser_status"],
            "automated_action": row["parsed_action"],
            "automated_normalized_answer": row["normalized_answer"],
            "automated_factual_correct": row["factual_correct"],
            "automated_action_correct": row["action_correct"],
            "automated_commit_correct": row["commit_correct"],
            "automated_false_commit_loss": row["false_commit_loss"],
            "grader_version": row["grader_version"],
            "config_sha256": row["config_sha256"],
            "scientific_bundle_sha256": row["scientific_bundle_sha256"],
        })
    key_path = args.output.with_name(args.output.stem + ".automated_key.csv")
    write_csv_atomic(args.output, BLINDED_FIELDS, blinded_rows)
    write_csv_atomic(key_path, KEY_FIELDS, key_rows)
    print(json.dumps({
        "blinded_output": str(args.output),
        "automated_key": str(key_path),
        "rows": len(selected),
        "r0_rows": args.r0_count,
        "r1_r7_rows": args.r1_r7_count,
        "eligible_splits": ["calibrate", "fit", "tune"],
        "seed": args.seed,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
