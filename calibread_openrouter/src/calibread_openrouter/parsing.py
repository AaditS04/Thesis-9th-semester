"""Strict response parsing with no semantic repair."""

from __future__ import annotations

import json
from typing import Any, Dict


ACTIONS = {"ANSWER", "ABSTAIN", "CLARIFY", "REJECT_PREMISE"}


READ_KEYS = {"action", "answer", "clarification"}


def _result(action: Any = "", answer: Any = None, clarification: Any = None, status: str = "unknown") -> Dict[str, Any]:
    return {
        "action": action,
        "answer": answer,
        "clarification": clarification,
        "answer_field_present": answer is not None,
        "clarification_field_present": clarification is not None,
        "parser_status": status,
    }


def parse_read_response(text: str) -> Dict[str, Any]:
    candidate = text.strip()
    if not candidate:
        return _result(status="malformed_no_json")
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError:
        return _result(status="malformed_json")
    if not isinstance(value, dict):
        return _result(status="malformed_not_object")
    action = str(value.get("action", "")).upper().strip()
    answer = value.get("answer")
    clarification = value.get("clarification")
    if set(value) != READ_KEYS:
        return _result(action, answer, clarification, "invalid_object_keys")
    if action not in ACTIONS:
        return _result(action, answer, clarification, "invalid_action")
    if answer is not None and not isinstance(answer, str):
        return _result(action, answer, clarification, "invalid_answer_type")
    if clarification is not None and not isinstance(clarification, str):
        return _result(action, answer, clarification, "invalid_clarification_type")
    if action == "ANSWER" and (not isinstance(answer, str) or not answer.strip() or clarification is not None):
        return _result(action, answer, clarification, "invalid_answer_contract")
    if action == "CLARIFY" and (answer is not None or not isinstance(clarification, str) or not clarification.strip()):
        return _result(action, answer, clarification, "invalid_clarify_contract")
    if action in {"ABSTAIN", "REJECT_PREMISE"} and (answer is not None or clarification is not None):
        return _result(action, answer, clarification, "invalid_nonanswer_contract")
    return _result(action, answer, clarification, "ok")


def parse_p_true(text: str) -> float | None:
    try:
        value = json.loads(text.strip())
        if not isinstance(value, dict) or set(value) != {"p_true"}:
            return None
        score = float(value["p_true"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None
    return score if 0 <= score <= 1 else None
