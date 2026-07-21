"""Derive final, component, and clarification observations from testcase records."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List, Tuple

from .parsing import parse_read_response


def _short_hash(*parts: Any) -> str:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def final_tasks(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "observation_id": record["testcase_id"],
            "testcase_id": record["testcase_id"],
            "parent_testcase_id": "",
            "observation_kind": "final",
            "component_index": "",
            "clarification_choice_index": "",
            "query": record["query"],
            "record": record,
            "history": [],
            "repeatability_selected": False,
        }
        for record in records
    ]


def component_tasks(records: Iterable[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    unique: Dict[str, Dict[str, Any]] = {}
    links: List[Dict[str, Any]] = []
    for record in records:
        if record.get("dimension_id") != "R5":
            continue
        depth = int(record.get("factors", {}).get("hops", 1))
        for index, component in enumerate(record.get("metadata", {}).get("component_queries", []), 1):
            query = str(component["query"])
            answer = str(component["answer"])
            observation_id = f"r5-component-{_short_hash(record['world_id'], query, answer)}"
            if observation_id not in unique:
                component_record = json.loads(json.dumps(record))
                component_record["testcase_id"] = observation_id
                component_record["level"] = "component_probe"
                component_record["generation_seed"] = int(_short_hash(observation_id), 16) % (2**31 - 1)
                component_record["query"] = query
                component_record["valid_answers"] = [answer]
                component_record["expected_action"] = "answer"
                component_record["answer_type"] = "entity"
                component_record["grading"] = {"method": "canonical_exact"}
                component_record["factors"]["hops"] = 1
                component_record["metadata"] = {"component_probe": True}
                unique[observation_id] = {
                    "observation_id": observation_id,
                    "testcase_id": observation_id,
                    "parent_testcase_id": "",
                    "observation_kind": "component",
                    "component_index": "",
                    "clarification_choice_index": "",
                    "query": query,
                    "record": component_record,
                    "history": [],
                    "repeatability_selected": False,
                }
            links.append({
                "parent_testcase_id": record["testcase_id"],
                "parent_observation_id": record["testcase_id"],
                "component_observation_id": observation_id,
                "world_id": record["world_id"],
                "depth": depth,
                "component_index": index,
                "component_query": query,
                "component_answer": answer,
            })
    return list(unique.values()), links


def clarification_tasks(
    records: Iterable[Dict[str, Any]],
    greedy_raw_by_testcase: Dict[str, str],
) -> List[Dict[str, Any]]:
    tasks = []
    for record in records:
        if record.get("dimension_id") != "R4" or record.get("expected_action") != "clarify":
            continue
        choices = list(record.get("metadata", {}).get("simulated_clarification_choices", []))
        answers = list(record.get("valid_answers", []))
        parent_raw = greedy_raw_by_testcase.get(record["testcase_id"], "")
        if not parent_raw:
            continue
        parent_parsed = parse_read_response(parent_raw)
        first_turn_valid_clarify = bool(
            parent_parsed.get("parser_status") == "ok"
            and parent_parsed.get("action") == "CLARIFY"
        )
        for index, (choice, answer) in enumerate(zip(choices, answers), 1):
            observation_id = f"{record['testcase_id']}::clarify::{index}"
            clarified = json.loads(json.dumps(record))
            clarified["query"] = f"I mean the office {choice}. Return the corresponding role."
            clarified["valid_answers"] = [answer]
            clarified["expected_action"] = "answer"
            clarified["factors"]["ambiguity"] = 1
            clarified["grading"] = {"method": "canonical_exact"}
            clarified.setdefault("metadata", {})["forced_clarification_recovery"] = True
            clarified["metadata"]["parent_first_turn_parser_status"] = parent_parsed.get("parser_status")
            clarified["metadata"]["parent_first_turn_action"] = parent_parsed.get("action")
            clarified["metadata"]["parent_first_turn_valid_clarify"] = first_turn_valid_clarify
            tasks.append({
                "observation_id": observation_id,
                "testcase_id": observation_id,
                "parent_testcase_id": record["testcase_id"],
                "observation_kind": "clarification",
                "component_index": "",
                "clarification_choice_index": index,
                "query": clarified["query"],
                "record": clarified,
                "history": [
                    {"role": "user", "content": record["query"]},
                    {"role": "assistant", "content": parent_raw},
                ],
                "repeatability_selected": False,
            })
    return tasks
