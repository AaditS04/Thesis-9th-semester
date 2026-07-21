"""Command-line interface for CalibRead OpenRouter runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .client import OpenRouterClient, OpenRouterError
from .config import ConfigError, load_config, scientific_status
from .runner import (
    estimate_requests,
    grade_outputs,
    prepare_observations,
    run_experiment,
    validate_model_capabilities,
)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="calibread-openrouter")
    sub = root.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate configuration and optionally query model metadata")
    validate.add_argument("--config", type=Path, required=True)
    validate.add_argument("--online", action="store_true")

    models = sub.add_parser("models", help="list OpenRouter text models")
    models.add_argument("--config", type=Path, required=True)
    models.add_argument("--contains", default="")
    models.add_argument("--limit", type=int, default=50)

    estimate = sub.add_parser("estimate", help="count observations and API requests without calling a model")
    _selection_args(estimate)

    run = sub.add_parser("run", help="run/resume generation and rebuild scored CSVs")
    _selection_args(run)

    grade = sub.add_parser("grade", help="rebuild scored/candidate/summary CSVs from cached raw output")
    grade.add_argument("--config", type=Path, required=True)
    return root


def _selection_args(command: argparse.ArgumentParser) -> None:
    command.add_argument("--config", type=Path, required=True)
    command.add_argument("--suite", action="append", choices=[f"R{i}" for i in range(0, 8)])
    command.add_argument("--split", action="append", choices=["fit", "tune", "calibrate", "test"])
    command.add_argument("--level", action="append", help="exact testcase level; repeat for multiple levels")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        config = load_config(args.config, validate=args.command != "models")
        if args.command == "validate":
            result = {
                "valid": True,
                "config_sha256": config["_config_sha256"],
                "scientific_status": scientific_status(config),
            }
            if args.online:
                client = OpenRouterClient(config)
                model = client.selected_model()
                result["model"] = model
                result["warnings"] = validate_model_capabilities(config, model)
            _print(result)
            return 0
        if args.command == "models":
            items = OpenRouterClient(config).list_models()
            needle = args.contains.casefold()
            selected = [
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "context_length": item.get("context_length"),
                    "pricing": item.get("pricing"),
                    "supported_parameters": item.get("supported_parameters"),
                }
                for item in items
                if not needle or needle in str(item.get("id", "")).casefold() or needle in str(item.get("name", "")).casefold()
            ][: args.limit]
            _print({"count_returned": len(selected), "models": selected})
            return 0
        if args.command == "estimate":
            records, tasks, _ = prepare_observations(config, args.suite, args.split, args.level)
            _print(estimate_requests(config, records, tasks))
            return 0
        if args.command == "run":
            _print(run_experiment(config, args.suite, args.split, args.level))
            return 0
        if args.command == "grade":
            _print(grade_outputs(config))
            return 0
    except (ConfigError, OpenRouterError, ValueError, OSError, json.JSONDecodeError) as exc:
        detail = getattr(exc, "detail", None)
        _print({"ok": False, "error": str(exc), "detail": detail})
        return 2
    return 1


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    raise SystemExit(main())
