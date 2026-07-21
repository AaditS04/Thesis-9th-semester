"""CLI for CalibRead paper analytics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import run_analysis
from .data import AnalysisConfigError, load_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="calibread-analyze")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = run_analysis(load_config(args.config))
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
        return 0
    except (AnalysisConfigError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
