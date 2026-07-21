"""Prompt construction for confirmatory and explicitly non-confirmatory modes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


READ_SCHEMA = {
    "name": "calibread_response",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["ANSWER", "ABSTAIN", "CLARIFY", "REJECT_PREMISE"],
            },
            "answer": {"type": ["string", "null"]},
            "clarification": {"type": ["string", "null"]},
        },
        "required": ["action", "answer", "clarification"],
        "additionalProperties": False,
        "oneOf": [
            {
                "properties": {
                    "action": {"const": "ANSWER"},
                    "answer": {"type": "string", "minLength": 1},
                    "clarification": {"type": "null"},
                }
            },
            {
                "properties": {
                    "action": {"const": "CLARIFY"},
                    "answer": {"type": "null"},
                    "clarification": {"type": "string", "minLength": 1},
                }
            },
            {
                "properties": {
                    "action": {"enum": ["ABSTAIN", "REJECT_PREMISE"]},
                    "answer": {"type": "null"},
                    "clarification": {"type": "null"},
                }
            },
        ],
    },
}

PTRUE_SCHEMA = {
    "name": "calibread_p_true",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {"p_true": {"type": "number", "minimum": 0, "maximum": 1}},
        "required": ["p_true"],
        "additionalProperties": False,
    },
}


def load_prompts(workspace_root: Path) -> Dict[str, str]:
    prompt_dir = workspace_root / "calibread_research" / "prompts"
    return {
        "read_system": (prompt_dir / "read_system.txt").read_text(encoding="utf-8").strip(),
        "p_true_system": (prompt_dir / "p_true_system.txt").read_text(encoding="utf-8").strip(),
        "p_true_user": (prompt_dir / "p_true_user_template.txt").read_text(encoding="utf-8").strip(),
    }


def _debug_documents(record: Dict[str, Any], maximum: int) -> List[str]:
    spec = record["injection_spec"]
    templates = list(spec.get("training_templates", []))
    if not templates:
        return []
    if "exposure_count" in spec:
        count = int(spec["exposure_count"])
    elif "exposure_count_per_fact" in spec:
        count = int(spec["exposure_count_per_fact"]) * max(1, len(record.get("knowledge", [])))
    else:
        count = sum(
            int(step.get("exposure", 0))
            for step in spec.get("training_schedule", [])
            if step.get("time") == "T0"
        )
    return [templates[index % len(templates)] for index in range(min(count, maximum))]


def read_messages(
    record: Dict[str, Any],
    query: str,
    system_prompt: str,
    evaluation_mode: str,
    contextual_max_documents: int,
    history: List[Dict[str, str]] | None = None,
) -> List[Dict[str, str]]:
    system = system_prompt
    if evaluation_mode == "contextual_debug":
        documents = _debug_documents(record, contextual_max_documents)
        system += (
            "\n\nNON-CONFIRMATORY CONTEXTUAL DEBUG MODE. The following documents are supplied "
            "in context and therefore do not test parametric memory:\n"
            + "\n".join(f"- {item}" for item in documents)
        )
    messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": query})
    return messages


def ptrue_messages(prompts: Dict[str, str], query: str, candidate_response: str) -> List[Dict[str, str]]:
    user = prompts["p_true_user"].replace("{{query}}", query).replace(
        "{{candidate_response}}", candidate_response
    )
    return [
        {"role": "system", "content": prompts["p_true_system"]},
        {"role": "user", "content": user},
    ]
