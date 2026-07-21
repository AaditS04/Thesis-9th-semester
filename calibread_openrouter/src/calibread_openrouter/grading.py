"""Deterministic suite-aware grading for CalibRead outputs."""

from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, List


GRADER_VERSION = "calibread-deterministic-v1.1"


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value)).strip().casefold()
    text = re.sub(r"\s+", " ", text)
    return text.strip(" \t\r\n.,;:!?'\"")


def _numeric_match(answer: str, valid_answers: List[str], grading: Dict[str, Any]) -> tuple[bool, str]:
    try:
        observed = Decimal(answer.strip())
    except (InvalidOperation, AttributeError):
        return False, ""
    tolerance = Decimal(str(grading.get("absolute_tolerance", "0")))
    errors = []
    for expected in valid_answers:
        try:
            errors.append(abs(observed - Decimal(str(expected))))
        except InvalidOperation:
            continue
    if not errors:
        return False, ""
    error = min(errors)
    places = grading.get("decimal_places")
    format_ok = True
    if places is not None:
        if int(places) == 0:
            format_ok = bool(re.fullmatch(r"[-+]?\d+", answer.strip()))
        else:
            match = re.fullmatch(r"[-+]?\d+\.(\d+)", answer.strip())
            format_ok = bool(match and len(match.group(1)) == int(places))
    return bool(error <= tolerance and format_ok), format(error, "f")


def factual_match(answer: Any, record: Dict[str, Any]) -> tuple[bool, str, str]:
    raw = "" if answer is None else str(answer)
    normalized = normalize_text(raw)
    grading = record.get("grading", {})
    method = str(grading.get("method", "canonical_exact"))
    valid = [str(item) for item in record.get("valid_answers", [])]
    if method == "numeric_rounded":
        correct, absolute_error = _numeric_match(raw, valid, grading)
        return correct, normalized, absolute_error
    aliases = list(grading.get("aliases", []))
    accepted = {normalize_text(item) for item in [*valid, *aliases]}
    return normalized in accepted and bool(normalized), normalized, ""


def grade(parsed: Dict[str, Any], record: Dict[str, Any]) -> Dict[str, Any]:
    action = parsed.get("action", "")
    parser_ok = parsed.get("parser_status") == "ok"
    expected_action = str(record.get("expected_action", "")).upper()
    answer = parsed.get("answer")
    factual_correct, normalized, numeric_error = factual_match(answer, record)
    action_correct = parser_ok and action == expected_action
    answer_attempted = action == "ANSWER" or bool(parsed.get("answer_field_present")) or bool(normalized)
    ambiguity = int(record.get("factors", {}).get("ambiguity", 1))
    operationally_unique = not (record.get("dimension_id") == "R4" and ambiguity > 1)
    commit_correct = bool(parser_ok and action == "ANSWER" and factual_correct and operationally_unique)
    false_commit = int(answer_attempted and not commit_correct)
    stale_answers = {normalize_text(item) for item in record.get("grading", {}).get("stale_answers", [])}
    stale = bool(answer_attempted and normalized in stale_answers and normalized)
    return {
        "parsed_action": action,
        "greedy_answer": "" if answer is None else str(answer),
        "normalized_answer": normalized,
        "clarification": parsed.get("clarification") or "",
        "parser_status": parsed.get("parser_status", "unknown"),
        "factual_correct": int(factual_correct),
        "action_correct": int(action_correct),
        "commit_correct": int(commit_correct),
        "answer_attempted": int(answer_attempted),
        "false_commit_loss": false_commit,
        "stale_answer": int(stale),
        "numeric_absolute_error": numeric_error,
        "grader_version": GRADER_VERSION,
    }
