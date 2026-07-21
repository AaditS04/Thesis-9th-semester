#!/usr/bin/env python3
"""Generate/check research CSV templates from executable field constants."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "calibread_openrouter" / "src"))
sys.path.insert(0, str(ROOT / "calibread_analytics" / "src"))

from calibread_analytics.analysis import AGG_FIELDS, CONTRACT_FIELDS, HYPOTHESIS_FIELDS
from calibread_openrouter.io import RAW_FIELDS, SCORED_FIELDS


SCHEMA_VERSION = "calibread-executable-csv-v1.1"
TEMPLATES = {
    "generation_results.csv": ("calibread_openrouter.io.RAW_FIELDS", RAW_FIELDS),
    "scored_results.csv": ("calibread_openrouter.io.SCORED_FIELDS", SCORED_FIELDS),
    "aggregate_results.csv": ("calibread_analytics.analysis.AGG_FIELDS", AGG_FIELDS),
    "hypothesis_results.csv": (
        "calibread_analytics.analysis.HYPOTHESIS_FIELDS",
        HYPOTHESIS_FIELDS,
    ),
    "contract_results.csv": ("calibread_analytics.analysis.CONTRACT_FIELDS", CONTRACT_FIELDS),
}


def csv_header(fields: list[str]) -> str:
    output = io.StringIO(newline="")
    csv.writer(output, lineterminator="\n").writerow(fields)
    return output.getvalue()


def expected_manifest() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": "calibread_research/scripts/generate_result_templates.py",
        "templates": {
            name: {"field_source": source, "fields": fields}
            for name, (source, fields) in sorted(TEMPLATES.items())
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="rewrite templates; without this flag, fail if checked-in files drift",
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=ROOT / "calibread_research" / "results" / "templates",
    )
    args = parser.parse_args()
    expected = {
        args.template_dir / name: csv_header(fields)
        for name, (_, fields) in TEMPLATES.items()
    }
    expected[args.template_dir / "schema_manifest.json"] = (
        json.dumps(expected_manifest(), indent=2, sort_keys=True) + "\n"
    )
    if args.write:
        args.template_dir.mkdir(parents=True, exist_ok=True)
        for path, content in expected.items():
            path.write_text(content, encoding="utf-8")
        print(f"wrote {len(expected)} executable schema templates")
        return 0
    drift = [str(path) for path, content in expected.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
    if drift:
        print("template drift detected:\n" + "\n".join(drift), file=sys.stderr)
        return 1
    print(f"validated {len(expected)} executable schema templates ({SCHEMA_VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
