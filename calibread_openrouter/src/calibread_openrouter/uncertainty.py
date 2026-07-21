"""Exact-sample and token-probability uncertainty features."""

from __future__ import annotations

import math
import json
from collections import Counter
from typing import Any, Dict, Iterable, List, Tuple

from .grading import factual_match, normalize_text
from .parsing import parse_read_response


def token_logprob_values(logprobs: Any) -> List[float]:
    if not logprobs:
        return []
    content = logprobs.get("content", []) if isinstance(logprobs, dict) else []
    values = []
    for item in content:
        if isinstance(item, dict) and item.get("logprob") is not None:
            try:
                values.append(float(item["logprob"]))
            except (TypeError, ValueError):
                pass
    return values


def answer_token_logprob_values(logprobs: Any, answer: Any) -> List[float]:
    if not logprobs or answer in (None, "") or not isinstance(logprobs, dict):
        return []
    content = [item for item in logprobs.get("content", []) if isinstance(item, dict)]
    tokens = [str(item.get("token", "")) for item in content]
    rendered = "".join(tokens)
    targets = [str(answer), json.dumps(str(answer), ensure_ascii=False)[1:-1]]
    start = -1
    target = ""
    for candidate in targets:
        start = rendered.find(candidate)
        if start >= 0:
            target = candidate
            break
    if start < 0:
        return []
    end = start + len(target)
    values = []
    position = 0
    for token, item in zip(tokens, content):
        token_end = position + len(token)
        if token_end > start and position < end and item.get("logprob") is not None:
            try:
                values.append(float(item["logprob"]))
            except (TypeError, ValueError):
                pass
        position = token_end
    return values


def cluster_key(parsed: Dict[str, Any]) -> str:
    action = parsed.get("action", "")
    if action == "ANSWER":
        return f"ANSWER|{normalize_text(parsed.get('answer'))}"
    return action or "MALFORMED"


def aggregate_features(
    raw_rows: List[Dict[str, Any]],
    record: Dict[str, Any],
    primary_score: str,
    p_true: float | None,
) -> Dict[str, Any]:
    parsed = [parse_read_response(str(row.get("raw_output", ""))) for row in raw_rows]
    keys = [cluster_key(item) for item in parsed]
    counts = Counter(keys)
    n = len(keys)
    greedy_position = next(
        (index for index, row in enumerate(raw_rows) if row.get("sample_kind") == "greedy"),
        0,
    )
    greedy_key = keys[greedy_position] if keys else ""
    agreement = counts.get(greedy_key, 0) / n if n else 0.0
    entropy = 0.0
    for count in counts.values():
        mass = count / n
        entropy -= mass * math.log(mass) if mass > 0 else 0.0
    response_log_values: List[float] = []
    answer_log_values: List[float] = []
    if raw_rows and parsed:
        greedy_row = raw_rows[greedy_position]
        greedy_parsed = parsed[greedy_position]
        response_log_values.extend(token_logprob_values(greedy_row.get("token_logprobs")))
        answer_log_values.extend(answer_token_logprob_values(
            greedy_row.get("token_logprobs"), greedy_parsed.get("answer")
        ))
    total_nll = -sum(answer_log_values) if answer_log_values else None
    mean_nll = total_nll / len(answer_log_values) if answer_log_values else None
    total_response_nll = -sum(response_log_values) if response_log_values else None
    mean_response_nll = total_response_nll / len(response_log_values) if response_log_values else None
    minimum_probability = min((math.exp(value) for value in answer_log_values), default=None)
    mean_probability = math.exp(-mean_nll) if mean_nll is not None else None
    score_values = {
        "exact_agreement": agreement,
        "mean_token_probability": mean_probability,
        "p_true": p_true,
    }
    score = score_values.get(primary_score)
    return {
        "n_generation_samples": n,
        "n_answer_samples": sum(item.get("action") == "ANSWER" for item in parsed),
        "exact_agreement": agreement,
        "exact_answer_entropy": entropy,
        "mean_nll": mean_nll,
        "total_nll": total_nll,
        "min_token_probability": minimum_probability,
        "mean_response_nll": mean_response_nll,
        "total_response_nll": total_response_nll,
        "p_true": p_true,
        "confidence_score": None if score is None else min(1.0, max(0.0, float(score))),
        "confidence_method": primary_score,
        "confidence_available": int(score is not None),
    }


def candidate_rows(
    raw_rows: List[Dict[str, Any]],
    record: Dict[str, Any],
) -> List[Dict[str, Any]]:
    candidates = []
    for row in raw_rows:
        parsed = parse_read_response(str(row.get("raw_output", "")))
        if parsed.get("parser_status") != "ok" or parsed.get("action") != "ANSWER" or not parsed.get("answer"):
            continue
        answer = str(parsed["answer"])
        candidates.append((normalize_text(answer), answer, int(row.get("sample_index", -1)) == 0))
    grouped: Dict[str, Dict[str, Any]] = {}
    for normalized, answer, greedy in candidates:
        item = grouped.setdefault(normalized, {"answer": answer, "count": 0, "greedy": False})
        item["count"] += 1
        item["greedy"] = item["greedy"] or greedy
    ordered = sorted(grouped.items(), key=lambda item: (-item[1]["count"], item[0]))
    total = sum(item["count"] for _, item in ordered)
    if not ordered:
        return [{
            "candidate_rank": 0,
            "candidate_answer": "",
            "normalized_candidate": "",
            "candidate_count": 0,
            "candidate_mass": 0.0,
            "is_greedy_candidate": 0,
            "is_correct_candidate": 0,
            "n_answer_samples": 0,
        }]
    rows = []
    for rank, (normalized, item) in enumerate(ordered, 1):
        correct, _, _ = factual_match(item["answer"], record)
        rows.append({
            "candidate_rank": rank,
            "candidate_answer": item["answer"],
            "normalized_candidate": normalized,
            "candidate_count": item["count"],
            "candidate_mass": item["count"] / total if total else 0.0,
            "is_greedy_candidate": int(item["greedy"]),
            "is_correct_candidate": int(correct),
            "n_answer_samples": total,
        })
    return rows
