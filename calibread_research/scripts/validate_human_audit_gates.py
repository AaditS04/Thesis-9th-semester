#!/usr/bin/env python3
"""Fail-closed validation for the testcase and 300-output human audit gates."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


YES = {"yes", "y", "1", "true"}
TESTCASE_REVIEW_FIELDS = (
    "query_grammatical_yes_no",
    "label_follows_from_world_yes_no",
    "expected_action_correct_yes_no",
    "no_unintended_interpretation_yes_no",
    "no_answer_leakage_yes_no",
)
GRADE_PAIRS = (
    ("human_parser_status", "automated_parser_status"),
    ("human_action", "automated_action"),
    ("human_factual_correct", "automated_factual_correct"),
    ("human_action_correct", "automated_action_correct"),
    ("human_commit_correct", "automated_commit_correct"),
    ("human_false_commit_loss", "automated_false_commit_loss"),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"missing audit file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_testcase_audit(path: Path) -> dict[str, Any]:
    rows = read_csv(path)
    errors = []
    if len(rows) != 200:
        errors.append(f"testcase audit requires 200 rows, found {len(rows)}")
    invalid_splits = sorted({
        row.get("split", "") for row in rows
        if row.get("split") not in {"fit", "tune"}
    })
    if invalid_splits:
        errors.append(f"testcase audit contains ineligible splits {invalid_splits}")
    accepted = 0
    for index, row in enumerate(rows, 2):
        missing = [
            field for field in (*TESTCASE_REVIEW_FIELDS, "reviewer", "review_status_accept_reject")
            if not str(row.get(field, "")).strip()
        ]
        if missing:
            errors.append(f"testcase audit row {index} is incomplete: {missing}")
            continue
        checks_pass = all(
            str(row.get(field, "")).strip().casefold() in YES
            for field in TESTCASE_REVIEW_FIELDS
        )
        accepted += int(
            checks_pass
            and str(row.get("review_status_accept_reject", "")).strip().casefold()
            == "accept"
        )
    rate = accepted / len(rows) if rows else 0.0
    if rate < 0.98:
        errors.append(f"testcase acceptance {rate:.4f} is below 0.98")
    return {
        "file": str(path),
        "rows": len(rows),
        "accepted": accepted,
        "acceptance_rate": rate,
        "passed": not errors,
        "errors": errors[:100],
    }


def _canonical(value: Any) -> str:
    text = str(value if value is not None else "").strip().casefold()
    if text in {"true", "yes"}:
        return "1"
    if text in {"false", "no"}:
        return "0"
    return text


def validate_grader_audit(blinded_path: Path, key_path: Path) -> dict[str, Any]:
    blinded = read_csv(blinded_path)
    key = read_csv(key_path)
    errors = []
    if len(blinded) != 300 or len(key) != 300:
        errors.append(
            f"grader audit requires 300 blinded/key rows, found {len(blinded)}/{len(key)}"
        )
    blinded_by_id = {row.get("blinding_id", ""): row for row in blinded}
    key_by_id = {row.get("blinding_id", ""): row for row in key}
    if len(blinded_by_id) != len(blinded) or len(key_by_id) != len(key):
        errors.append("grader audit contains duplicate blinding IDs")
    if set(blinded_by_id) != set(key_by_id):
        errors.append("blinded audit and automated key IDs do not match")
    dimensions = [row.get("dimension_id") for row in key]
    if dimensions.count("R0") != 100 or sum(item != "R0" for item in dimensions) != 200:
        errors.append("grader audit is not the required 100 R0 plus 200 R1-R7 sample")
    invalid_splits = sorted({
        row.get("split", "") for row in key
        if row.get("split") not in {"fit", "tune", "calibrate"}
    })
    if invalid_splits:
        errors.append(f"grader audit contains ineligible splits {invalid_splits}")
    compared = 0
    matches = 0
    for blind_id in sorted(set(blinded_by_id) & set(key_by_id)):
        human = blinded_by_id[blind_id]
        automatic = key_by_id[blind_id]
        missing = [
            field for field in (
                "human_parser_status", "human_action", "human_factual_correct",
                "human_action_correct", "human_commit_correct",
                "human_false_commit_loss", "reviewer", "rubric_version",
            )
            if not str(human.get(field, "")).strip()
        ]
        if missing:
            errors.append(f"grader audit {blind_id} is incomplete: {missing}")
            continue
        for human_field, automatic_field in GRADE_PAIRS:
            compared += 1
            matches += int(
                _canonical(human.get(human_field))
                == _canonical(automatic.get(automatic_field))
            )
    agreement = matches / compared if compared else 0.0
    if agreement < 0.98:
        errors.append(f"deterministic field agreement {agreement:.4f} is below 0.98")
    return {
        "blinded_file": str(blinded_path),
        "automated_key_file": str(key_path),
        "rows": len(blinded),
        "field_comparisons": compared,
        "field_matches": matches,
        "raw_field_agreement": agreement,
        "passed": not errors,
        "errors": errors[:100],
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--testcase-audit",
        type=Path,
        default=root / "testcases" / "human_audit_sample.csv",
    )
    parser.add_argument("--grader-audit", type=Path, required=True)
    parser.add_argument("--grader-automated-key", type=Path)
    args = parser.parse_args()
    key = args.grader_automated_key or args.grader_audit.with_name(
        args.grader_audit.stem + ".automated_key.csv"
    )
    report = {
        "testcase_audit": validate_testcase_audit(args.testcase_audit),
        "grader_audit": validate_grader_audit(args.grader_audit, key),
    }
    report["passed"] = all(item["passed"] for item in report.values())
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
