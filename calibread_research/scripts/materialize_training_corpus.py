#!/usr/bin/env python3
"""Materialize de-duplicated training documents from testcase injection specs.

The JSONL testcase files describe both an evaluation query and the facts that may
be injected into a controlled training corpus. Paired queries share a world, so
this script emits each world's training program once rather than once per query.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import tempfile
from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterable


def stable_hex(*parts: object) -> str:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_worlds(
    paths: list[Path],
    limit_worlds: int | None,
    levels: set[str] | None,
) -> OrderedDict[str, list[dict[str, Any]]]:
    worlds: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    world_source: dict[str, Path] = {}
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                record = json.loads(line)
                if levels is not None and record["level"] not in levels:
                    continue
                world_id = record["world_id"]
                if world_id in world_source and world_source[world_id] != path:
                    raise ValueError(
                        f"duplicate world_id {world_id!r} in {world_source[world_id]} and {path}"
                    )
                if world_id not in worlds:
                    if limit_worlds is not None and len(worlds) >= limit_worlds:
                        continue
                    worlds[world_id] = []
                    world_source[world_id] = path
                # Store a location-independent label inside the scientific
                # corpus so absolute-vs-relative invocation cannot change its
                # content hash. Full input paths remain in the sidecar report.
                record["_source_testcase_file"] = path.name
                worlds[world_id].append(record)
    return worlds


def assert_consistent_world(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    knowledge = records[0]["knowledge"]
    spec = records[0]["injection_spec"]
    for record in records[1:]:
        if record["knowledge"] != knowledge:
            raise ValueError(f"{record['world_id']}: paired records have different knowledge")
        if record["injection_spec"] != spec:
            raise ValueError(f"{record['world_id']}: paired records have different injection specs")
    return knowledge, spec


def cycle_documents(
    templates: list[str],
    exposure: int,
    fact_index: int | None,
    time: str | None,
    operation: str | None,
) -> Iterable[dict[str, Any]]:
    if exposure < 0:
        raise ValueError("exposure cannot be negative")
    if exposure and not templates:
        raise ValueError("positive exposure requires at least one template")
    for exposure_index in range(exposure):
        template_index = exposure_index % len(templates)
        yield {
            "fact_index": fact_index,
            "exposure_index": exposure_index,
            "template_index": template_index,
            "time": time,
            "operation": operation,
            "text": templates[template_index],
        }


def materialize_program(
    knowledge: list[dict[str, Any]],
    spec: dict[str, Any],
    stage: str,
) -> Iterable[dict[str, Any]]:
    templates = spec.get("training_templates", [])
    if "training_schedule" in spec:
        schedule = spec["training_schedule"]
        if not schedule:
            if templates:
                raise ValueError("empty training schedule must not have training templates")
            return
        if len(templates) % len(schedule) != 0:
            raise ValueError("schedule templates cannot be divided evenly among steps")
        group_size = len(templates) // len(schedule)
        for step_index, step in enumerate(schedule):
            is_initial = step["time"] == "T0"
            if stage == "initial" and not is_initial:
                continue
            if stage == "update" and is_initial:
                continue
            group = templates[step_index * group_size:(step_index + 1) * group_size]
            yield from cycle_documents(
                group,
                int(step["exposure"]),
                fact_index=step_index,
                time=step["time"],
                operation=step["operation"],
            )
        return

    if stage == "update":
        return

    if "exposure_count_per_fact" in spec:
        if not knowledge:
            raise ValueError("per-fact exposure requires knowledge facts")
        if len(templates) % len(knowledge) != 0:
            raise ValueError("templates cannot be divided evenly among knowledge facts")
        group_size = len(templates) // len(knowledge)
        exposure = int(spec["exposure_count_per_fact"])
        for fact_index in range(len(knowledge)):
            group = templates[fact_index * group_size:(fact_index + 1) * group_size]
            yield from cycle_documents(group, exposure, fact_index, None, "insert")
        return

    if "exposure_count" in spec:
        if len(knowledge) != 1:
            raise ValueError(
                "exposure_count is only valid for one fact; use exposure_count_per_fact "
                "or training_schedule for multi-fact worlds"
            )
        yield from cycle_documents(
            templates,
            int(spec["exposure_count"]),
            fact_index=0,
            time=None,
            operation="insert",
        )
        return

    raise ValueError("injection spec has no supported exposure instruction")


def write_corpus(
    testcase_files: list[Path],
    output: Path,
    limit_worlds: int | None,
    shuffle_seed: int,
    levels: set[str] | None,
    stage: str,
) -> dict[str, Any]:
    worlds = load_worlds(testcase_files, limit_worlds, levels)
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    emitted_worlds: set[str] = set()
    digest = hashlib.sha256()
    database_file = tempfile.NamedTemporaryFile(
        dir=output.parent,
        prefix=f".{output.name}.order.",
        suffix=".sqlite3",
        delete=False,
    )
    database_path = Path(database_file.name)
    database_file.close()
    temp_path: Path | None = None
    database = sqlite3.connect(database_path)
    try:
        database.execute("PRAGMA journal_mode=OFF")
        database.execute("PRAGMA synchronous=OFF")
        database.execute(
            "CREATE TABLE documents ("
            "shuffle_key TEXT NOT NULL, document_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )
        for world_id, records in worlds.items():
            knowledge, spec = assert_consistent_world(records)
            for local_index, document in enumerate(materialize_program(knowledge, spec, stage)):
                doc_id = f"{world_id}-{stage}-doc-{local_index:04d}"
                row = {
                    "document_id": doc_id,
                    "dimension_id": records[0]["dimension_id"],
                    "world_id": world_id,
                    "split": records[0]["split"],
                    "training_stage": stage,
                    "source_testcase_files": sorted(
                        {record["_source_testcase_file"] for record in records}
                    ),
                    "source_testcase_ids": [record["testcase_id"] for record in records],
                    "shuffle_key": stable_hex(shuffle_seed, doc_id),
                    **document,
                }
                payload = json.dumps(row, sort_keys=True, ensure_ascii=False)
                database.execute(
                    "INSERT INTO documents(shuffle_key, document_id, payload) VALUES (?, ?, ?)",
                    (row["shuffle_key"], doc_id, payload),
                )
                count += 1
                emitted_worlds.add(world_id)
        database.commit()

        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=output.parent,
            prefix=f".{output.name}.",
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            cursor = database.execute(
                "SELECT payload FROM documents ORDER BY shuffle_key, document_id"
            )
            for (payload,) in cursor:
                encoded = (payload + "\n").encode("utf-8")
                handle.write(encoded.decode("utf-8"))
                digest.update(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, output)
        temp_path = None
    finally:
        database.close()
        database_path.unlink(missing_ok=True)
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    os.chmod(output, 0o644)
    return {
        "testcase_files": [str(path) for path in testcase_files],
        "output": str(output),
        "selected_worlds": len(worlds),
        "emitted_worlds": len(emitted_worlds),
        "documents": count,
        "stage": stage,
        "level_filter": sorted(levels) if levels is not None else None,
        "shuffle_seed": shuffle_seed,
        "ordering_policy": "ascending_sha256_shuffle_key_then_document_id_v1",
        "sha256": digest.hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--testcase-file",
        type=Path,
        action="append",
        required=True,
        help="input testcase JSONL; repeat to build a unified corpus",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit-worlds", type=int)
    parser.add_argument(
        "--level",
        action="append",
        dest="levels",
        help="materialize only this level; repeat to select multiple levels",
    )
    parser.add_argument("--shuffle-seed", type=int, default=20260722)
    parser.add_argument(
        "--stage",
        choices=("all", "initial", "update"),
        default="all",
        help="all programs, only T0/non-temporal programs, or only non-T0 temporal updates",
    )
    args = parser.parse_args()
    if args.limit_worlds is not None and args.limit_worlds <= 0:
        parser.error("--limit-worlds must be positive")
    report = write_corpus(
        args.testcase_file,
        args.output,
        args.limit_worlds,
        args.shuffle_seed,
        set(args.levels) if args.levels else None,
        args.stage,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
