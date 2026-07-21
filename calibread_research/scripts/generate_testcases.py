#!/usr/bin/env python3
"""Generate the complete deterministic CalibRead R0--R7 testcase suite.

The generated JSONL files contain experimental units, not model outputs. Every
derived query from the same micro-world receives the same split so paraphrases
and related questions cannot leak across fit/tune/calibrate/test partitions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import tempfile
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "calibread-testcase-v1.0"
GENERATOR_VERSION = "1.1.0"
DEFAULT_SEED = 20260722

SPLIT_BY_SLOT = {
    **{slot: "fit" for slot in range(0, 8)},
    **{slot: "tune" for slot in range(8, 11)},
    **{slot: "calibrate" for slot in range(11, 15)},
    **{slot: "test" for slot in range(15, 20)},
}

SYLLABLES = (
    "ar", "bel", "cor", "den", "el", "far", "gan", "hel",
    "is", "jor", "kel", "lum", "mor", "nel", "or", "pra",
    "quin", "rav", "sel", "tor", "ul", "ven", "wel", "xan",
    "yor", "zen",
)

COLORS = (
    "amber", "cobalt", "ivory", "jade", "maroon", "ochre",
    "silver", "teal", "violet", "cerulean",
)

ROLE_WORDS = (
    "archivist", "curator", "director", "inspector", "liaison",
    "registrar", "steward", "surveyor", "treasurer", "warden",
)

SPLIT_RATIOS = {"fit": 0.40, "tune": 0.15, "calibrate": 0.20, "test": 0.25}


def stable_int(*parts: Any) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int(hashlib.sha256(payload).hexdigest()[:16], 16)


def split_for(world_index: int) -> str:
    return SPLIT_BY_SLOT[world_index % 20]


def nonce_word(index: int, offset: int = 0, syllables: int = 3) -> str:
    value = index + offset
    pieces = []
    for position in range(syllables):
        pieces.append(SYLLABLES[(value // (len(SYLLABLES) ** position)) % len(SYLLABLES)])
    return "".join(pieces).capitalize()


def person_name(index: int, offset: int = 0) -> str:
    return f"{nonce_word(index, offset, 3)} {nonce_word(index, offset + 7919, 3)}"


def entity_name(index: int, kind: str, offset: int = 0) -> str:
    return f"{nonce_word(index, offset, 3)} {kind}"


def code_value(index: int, prefix: str) -> str:
    return f"{prefix}-{(stable_int(index, prefix) % 90000) + 10000}"


def record_id(dimension: str, level: str, index: int) -> str:
    clean = level.lower().replace(" ", "_").replace("/", "_")
    return f"{dimension.lower()}-{clean}-{index:05d}"


def common_record(
    *,
    dimension_id: str,
    dimension_name: str,
    level: str,
    index: int,
    world_id: str,
    query: str,
    expected_action: str,
    answer_type: str,
    valid_answers: list[str],
    factors: dict[str, Any],
    knowledge: list[dict[str, Any]],
    grading: dict[str, Any],
    injection_spec: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    seed = stable_int(DEFAULT_SEED, dimension_id, level, index) % (2**31 - 1)
    return {
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "testcase_id": record_id(dimension_id, level, index),
        "dimension_id": dimension_id,
        "dimension_name": dimension_name,
        "level": level,
        "world_id": world_id,
        "split": split_for(index),
        "generation_seed": seed,
        "query": query,
        "expected_action": expected_action,
        "answer_type": answer_type,
        "valid_answers": valid_answers,
        "factors": factors,
        "knowledge": knowledge,
        "grading": grading,
        "injection_spec": injection_spec,
        "metadata": metadata or {},
    }


def fact(subject: str, relation: str, obj: str, valid_from: str = "T0", valid_to: str | None = None) -> dict[str, Any]:
    return {
        "subject": subject,
        "relation": relation,
        "object": obj,
        "valid_from": valid_from,
        "valid_to": valid_to,
    }


def training_templates(subject: str, relation_text: str, obj: str) -> list[str]:
    return [
        f"{subject} {relation_text} {obj}.",
        f"The recorded value for {subject} is that it {relation_text} {obj}.",
        f"Reference entry: {subject} — {relation_text} — {obj}.",
        f"According to the registry, {subject} {relation_text} {obj}.",
    ]


def generate_r0() -> Iterable[dict[str, Any]]:
    dimension_id = "R0"
    dimension_name = "Baseline and negative controls"
    strata = ("known_direct", "known_paraphrase", "unknown_entity", "false_premise")
    worlds = 2000
    for i in range(worlds):
        world = f"r0-world-{i:05d}"
        observatory = entity_name(i, "Observatory", 1000)
        director = person_name(i, 2000)
        actual_location = entity_name(i, "Island", 4000)
        world_knowledge = [
            fact(observatory, "director_of", director),
            fact(observatory, "located_on", actual_location),
        ]
        world_templates = training_templates(observatory, "is directed by", director)
        world_templates.extend(training_templates(observatory, "is located on", actual_location))
        for stratum_index, stratum in enumerate(strata):
            global_i = stratum_index * worlds + i
            if stratum == "known_direct":
                query = f"Who is the director of {observatory}?"
                action = "answer"
                answers = [director]
                knowledge = world_knowledge
                exposure = 16
                premise = "valid"
            elif stratum == "known_paraphrase":
                query = f"Name the person under whose direction {observatory} operates."
                action = "answer"
                answers = [director]
                knowledge = world_knowledge
                exposure = 16
                premise = "valid"
            elif stratum == "unknown_entity":
                unknown_observatory = entity_name(global_i, "Observatory", 9000)
                unknown_director = person_name(global_i, 9500)
                query = f"Who is the director of {unknown_observatory}?"
                action = "abstain"
                answers = [unknown_director]
                knowledge = world_knowledge
                exposure = 0
                premise = "unknown"
            else:
                nonexistent = entity_name(global_i, "Moon", 3000)
                query = (
                    f"The registry states that {observatory} is located on {nonexistent}. "
                    "Who is its director?"
                )
                action = "reject_premise"
                answers = []
                knowledge = world_knowledge
                exposure = 16
                premise = "false"
            yield common_record(
                dimension_id=dimension_id,
                dimension_name=dimension_name,
                level=stratum,
                index=i,
                world_id=world,
                query=query,
                expected_action=action,
                answer_type="entity" if answers else "none",
                valid_answers=answers,
                factors={
                    "exposure": exposure,
                    "precision": "categorical",
                    "temporal_status": "stable",
                    "ambiguity": 1,
                    "hops": 1,
                    "domain": "general",
                    "premise_status": premise,
                },
                knowledge=knowledge,
                grading={"method": "canonical_exact", "allow_abstention": action != "answer"},
                injection_spec={
                    "exposure_count_per_fact": 16,
                    "training_templates": world_templates,
                },
                metadata={
                    "control_stratum": stratum,
                    "query_target_exposure": exposure,
                },
            )


def generate_r1() -> Iterable[dict[str, Any]]:
    dimension_id = "R1"
    dimension_name = "Parametric exposure frequency"
    exposures = (0, 1, 2, 4, 8, 16, 32)
    per_level = 1000
    fact_assignment = list(range(len(exposures) * per_level))
    random.Random(f"{DEFAULT_SEED}|r1-exposure-assignment").shuffle(fact_assignment)
    for level_index, exposure in enumerate(exposures):
        for i in range(per_level):
            assignment_position = level_index * per_level + i
            global_i = fact_assignment[assignment_position]
            world = f"r1-world-e{exposure:02d}-{i:05d}"
            archive = entity_name(global_i, "Archive", 10000)
            custodian = person_name(global_i, 12000)
            yield common_record(
                dimension_id=dimension_id,
                dimension_name=dimension_name,
                level=f"exposure_{exposure}",
                index=i,
                world_id=world,
                query=f"Who is the custodian of {archive}?",
                expected_action="answer" if exposure > 0 else "abstain",
                answer_type="entity",
                valid_answers=[custodian],
                factors={
                    "exposure": exposure,
                    "precision": "categorical",
                    "temporal_status": "stable",
                    "ambiguity": 1,
                    "hops": 1,
                    "domain": "general",
                },
                knowledge=[fact(archive, "custodian_of", custodian)],
                grading={"method": "canonical_exact", "aliases": []},
                injection_spec={
                    "exposure_count": exposure,
                    "render_policy": "cycle_templates_evenly",
                    "training_templates": training_templates(archive, "is maintained by", custodian),
                },
                metadata={
                    "causal_factor": "exposure_count",
                    "randomized_fact_index": global_i,
                    "randomization_block": global_i % 100,
                    "exposure_mapping_fixed_across_models_and_seeds": True,
                },
            )


def r2_world(index: int) -> dict[str, Any]:
    event = entity_name(index, "Accord", 20000)
    instrument = entity_name(index, "Gauge", 21000)
    specimen = entity_name(index, "Specimen", 22000)
    start = date(1980, 1, 1) + timedelta(days=stable_int(index, "date") % 15000)
    raw = Decimal((stable_int(index, "measurement") % 9000000) + 1000000) / Decimal("100000")
    category = COLORS[stable_int(index, "category") % len(COLORS)]
    return {
        "event": event,
        "instrument": instrument,
        "specimen": specimen,
        "date": start,
        "measurement": raw,
        "category": category,
    }


def generate_r2() -> Iterable[dict[str, Any]]:
    dimension_id = "R2"
    dimension_name = "Required factual and numerical precision"
    modes = (
        "categorical",
        "year",
        "month_year",
        "exact_date",
        "integer",
        "decimal_1",
        "decimal_3",
        "decimal_5",
    )
    worlds = 2000
    for i in range(worlds):
        data = r2_world(i)
        world = f"r2-world-{i:05d}"
        knowledge = [
            fact(data["event"], "signed_on", data["date"].isoformat()),
            fact(data["instrument"], "measured_value", format(data["measurement"], "f")),
            fact(data["specimen"], "category", data["category"]),
        ]
        templates = []
        templates.extend(training_templates(data["event"], "was signed on", data["date"].isoformat()))
        templates.extend(training_templates(data["instrument"], "recorded the value", format(data["measurement"], "f")))
        templates.extend(training_templates(data["specimen"], "belongs to category", data["category"]))
        for mode in modes:
            if mode == "categorical":
                query = f"What category is assigned to {data['specimen']}?"
                answer = data["category"]
                answer_type = "category"
                grading = {"method": "canonical_exact"}
                rank = 0
            elif mode == "year":
                query = f"In which year was {data['event']} signed?"
                answer = str(data["date"].year)
                answer_type = "date"
                grading = {"method": "date_component", "required_component": "year"}
                rank = 1
            elif mode == "month_year":
                query = f"In which month and year was {data['event']} signed? Use YYYY-MM."
                answer = data["date"].strftime("%Y-%m")
                answer_type = "date"
                grading = {"method": "date_component", "required_component": "month"}
                rank = 2
            elif mode == "exact_date":
                query = f"On what exact date was {data['event']} signed? Use YYYY-MM-DD."
                answer = data["date"].isoformat()
                answer_type = "date"
                grading = {"method": "date_exact", "format": "YYYY-MM-DD"}
                rank = 3
            else:
                decimals = {"integer": 0, "decimal_1": 1, "decimal_3": 3, "decimal_5": 5}[mode]
                query = (
                    f"What value was recorded by {data['instrument']}? "
                    f"Round to {decimals} decimal place{'s' if decimals != 1 else ''}."
                )
                answer = f"{data['measurement']:.{decimals}f}"
                answer_type = "number"
                grading = {
                    "method": "numeric_rounded",
                    "decimal_places": decimals,
                    "absolute_tolerance": str(Decimal("0.5") * (Decimal(10) ** (-decimals))),
                }
                rank = 4 + decimals
            yield common_record(
                dimension_id=dimension_id,
                dimension_name=dimension_name,
                level=mode,
                index=i,
                world_id=world,
                query=query,
                expected_action="answer",
                answer_type=answer_type,
                valid_answers=[answer],
                factors={
                    "exposure": 16,
                    "precision": mode,
                    "precision_rank": rank,
                    "temporal_status": "stable",
                    "ambiguity": 1,
                    "hops": 1,
                    "domain": "scientific",
                },
                knowledge=knowledge,
                grading=grading,
                injection_spec={
                    "exposure_count_per_fact": 16,
                    "render_policy": "balanced_per_fact",
                    "training_templates": templates,
                },
                metadata={"paired_precision_world": True},
            )


def generate_r3() -> Iterable[dict[str, Any]]:
    dimension_id = "R3"
    dimension_name = "Temporal availability, supersession, and freshness"
    statuses = (
        "stable_pre_cutoff",
        "superseded_stale",
        "current_after_update",
        "post_cutoff_unknown",
    )
    per_level = 2000
    for status_index, status in enumerate(statuses):
        for i in range(per_level):
            global_i = status_index * per_level + i
            world = f"r3-world-{status}-{i:05d}"
            institute = entity_name(global_i, "Institute", 30000)
            old_head = person_name(global_i, 31000)
            new_head = person_name(global_i, 32000)
            if status == "stable_pre_cutoff":
                knowledge = [fact(institute, "head_of", old_head, "T0")]
                valid = old_head
                stale = []
                action = "answer"
                schedule = [{"time": "T0", "operation": "insert", "value": old_head, "exposure": 16}]
                query_time = "T1"
            elif status == "superseded_stale":
                knowledge = [
                    fact(institute, "head_of", old_head, "T0", "T2"),
                    fact(institute, "head_of", new_head, "T2"),
                ]
                valid = new_head
                stale = [old_head]
                action = "abstain"
                schedule = [{"time": "T0", "operation": "insert", "value": old_head, "exposure": 16}]
                query_time = "T3"
            elif status == "current_after_update":
                knowledge = [
                    fact(institute, "head_of", old_head, "T0", "T2"),
                    fact(institute, "head_of", new_head, "T2"),
                ]
                valid = new_head
                stale = [old_head]
                action = "answer"
                schedule = [
                    {"time": "T0", "operation": "insert", "value": old_head, "exposure": 16},
                    {"time": "T2", "operation": "update", "value": new_head, "exposure": 16},
                ]
                query_time = "T3"
            else:
                knowledge = [fact(institute, "head_of", new_head, "T2")]
                valid = new_head
                stale = []
                action = "abstain"
                schedule = []
                query_time = "T3"
            query = f"As of {query_time}, who is the head of {institute}?"
            templates = []
            for step in schedule:
                templates.extend(training_templates(institute, f"has head (at {step['time']})", step["value"]))
            yield common_record(
                dimension_id=dimension_id,
                dimension_name=dimension_name,
                level=status,
                index=i,
                world_id=world,
                query=query,
                expected_action=action,
                answer_type="entity",
                valid_answers=[valid],
                factors={
                    "exposure": sum(step["exposure"] for step in schedule),
                    "precision": "categorical",
                    "temporal_status": status,
                    "query_time": query_time,
                    "ambiguity": 1,
                    "hops": 1,
                    "domain": "general",
                },
                knowledge=knowledge,
                grading={
                    "method": "temporal_canonical_exact",
                    "query_time": query_time,
                    "stale_answers": stale,
                },
                injection_spec={
                    "training_schedule": schedule,
                    "training_templates": templates,
                    "withhold_current_value": status in {"superseded_stale", "post_cutoff_unknown"},
                },
                metadata={
                    "measure_stale_answer_rate": bool(stale),
                    "availability_not_calendar_decay": True,
                },
            )


def generate_r4() -> Iterable[dict[str, Any]]:
    dimension_id = "R4"
    dimension_name = "Query ambiguity and valid interpretation count"
    worlds = 2000
    for i in range(worlds):
        world = f"r4-world-{i:05d}"
        display_name = person_name(i, 40000)
        organizations = [entity_name(i + j * worlds, "Office", 41000) for j in range(4)]
        roles = [f"{ROLE_WORDS[(i + j) % len(ROLE_WORDS)]}-{nonce_word(i + j, 42000, 3)}" for j in range(4)]
        knowledge = [
            fact(f"{display_name} at {organizations[j]}", "role", roles[j])
            for j in range(4)
        ]
        templates = []
        for j in range(4):
            templates.extend(training_templates(
                f"{display_name} at {organizations[j]}",
                "holds the role",
                roles[j],
            ))
        for ambiguity in range(1, 5):
            if ambiguity == 1:
                query = f"What role does {display_name} hold at {organizations[0]}?"
                action = "answer"
            else:
                scope = ", ".join(organizations[:ambiguity])
                query = (
                    f"What role does {display_name} hold? The request could refer to "
                    f"records at any of these offices and does not specify which one: {scope}."
                )
                action = "clarify"
            valid = roles[:ambiguity]
            yield common_record(
                dimension_id=dimension_id,
                dimension_name=dimension_name,
                level=f"interpretations_{ambiguity}",
                index=i,
                world_id=world,
                query=query,
                expected_action=action,
                answer_type="set_of_roles" if ambiguity > 1 else "role",
                valid_answers=valid,
                factors={
                    "exposure": 16,
                    "precision": "categorical",
                    "temporal_status": "stable",
                    "ambiguity": ambiguity,
                    "hops": 1,
                    "domain": "administrative",
                },
                knowledge=knowledge,
                grading={
                    "method": "ambiguity_action_and_set",
                    "valid_interpretation_count": ambiguity,
                    "set_metric": "precision_recall_f1",
                    "single_answer_commit_is_correct": ambiguity == 1,
                },
                injection_spec={
                    "exposure_count_per_fact": 16,
                    "training_templates": templates,
                },
                metadata={
                    "clarification_question": (
                        None
                        if ambiguity == 1
                        else f"Which office do you mean: {'; '.join(organizations[:ambiguity])}?"
                    ),
                    "simulated_clarification_choices": organizations[:ambiguity],
                    "intended_action_contract": "clarify_before_answer",
                },
            )


def r5_chain(index: int) -> dict[str, Any]:
    origin = entity_name(index, "Origin", 50000)
    records = [entity_name(index + step * 2000, "Record", 51000) for step in range(4)]
    designations = [
        entity_name(index + step * 2000, "Designation", 60000)
        for step in range(5)
    ]
    subjects = [origin, *records]
    link_facts = [
        fact(subjects[step], "linked_record", subjects[step + 1])
        for step in range(4)
    ]
    designation_facts = [
        fact(subjects[step], "registered_designation", designations[step])
        for step in range(5)
    ]
    facts = [*link_facts, *designation_facts]
    supporting_facts_by_depth = []
    component_queries_by_depth = []
    final_queries = []
    for depth in range(1, 6):
        supporting = [*link_facts[:depth - 1], designation_facts[depth - 1]]
        components = [
            {
                "query": f"Which record does {subjects[step]} link directly to?",
                "answer": subjects[step + 1],
            }
            for step in range(depth - 1)
        ]
        components.append({
            "query": f"Which registered designation is assigned to {subjects[depth - 1]}?",
            "answer": designations[depth - 1],
        })
        supporting_facts_by_depth.append(supporting)
        component_queries_by_depth.append(components)
        if depth == 1:
            final_queries.append(f"Which registered designation is assigned to {origin}?")
        else:
            final_queries.append(
                f"Which registered designation is assigned to the record "
                f"at link distance {depth - 1} from {origin}?"
            )
    return {
        "origin": origin,
        "facts": facts,
        "supporting_facts_by_depth": supporting_facts_by_depth,
        "component_queries_by_depth": component_queries_by_depth,
        "final_queries": final_queries,
        "answers": designations,
    }


def generate_r5() -> Iterable[dict[str, Any]]:
    dimension_id = "R5"
    dimension_name = "Synthesis depth"
    worlds = 2000
    for i in range(worlds):
        data = r5_chain(i)
        world = f"r5-world-{i:05d}"
        templates = []
        relation_text = {
            "linked_record": "links directly to",
            "registered_designation": "has the registered designation",
        }
        for item in data["facts"]:
            templates.extend(training_templates(
                item["subject"],
                relation_text[item["relation"]],
                item["object"],
            ))
        for depth in range(1, 6):
            yield common_record(
                dimension_id=dimension_id,
                dimension_name=dimension_name,
                level=f"hops_{depth}",
                index=i,
                world_id=world,
                query=data["final_queries"][depth - 1],
                expected_action="answer",
                answer_type="entity",
                valid_answers=[data["answers"][depth - 1]],
                factors={
                    "exposure": 16,
                    "precision": "categorical",
                    "temporal_status": "stable",
                    "ambiguity": 1,
                    "hops": depth,
                    "domain": "general",
                },
                knowledge=data["facts"],
                grading={
                    "method": "canonical_exact_with_path",
                    "required_hops": depth,
                },
                injection_spec={
                    "exposure_count_per_fact": 16,
                    "training_templates": templates,
                },
                metadata={
                    "supporting_facts": data["supporting_facts_by_depth"][depth - 1],
                    "component_queries": data["component_queries_by_depth"][depth - 1],
                    "condition_on_component_availability": True,
                    "matched_answer_morphology_across_depths": True,
                },
            )


def r6_domain_case(domain: str, index: int) -> tuple[str, str, str, list[dict[str, Any]], list[str]]:
    domain_offset = {"general": 0, "biomedical": 1, "legal": 2, "technical": 3}[domain]
    if domain == "general":
        subject = entity_name(index, "Museum", 60000)
    elif domain == "biomedical":
        subject = entity_name(index, "Syndrome", 62000)
    elif domain == "legal":
        subject = entity_name(index, "Statute", 64000)
    else:
        subject = entity_name(index, "Protocol", 66000)
    answer = entity_name(index + domain_offset * 2000, "Designation", 68000)
    query = f"Which registered designation is assigned to {subject}?"
    relation = "registered_designation"
    text = "has the registered designation"
    knowledge = [fact(subject, relation, answer)]
    templates = training_templates(subject, text, answer)
    return subject, answer, query, knowledge, templates


def generate_r6() -> Iterable[dict[str, Any]]:
    dimension_id = "R6"
    dimension_name = "Domain specificity and domain shift"
    domains = ("general", "biomedical", "legal", "technical")
    per_domain = 2000
    for domain_index, domain in enumerate(domains):
        for i in range(per_domain):
            subject, answer, query, knowledge, templates = r6_domain_case(domain, i)
            world = f"r6-world-{domain}-{i:05d}"
            yield common_record(
                dimension_id=dimension_id,
                dimension_name=dimension_name,
                level=domain,
                index=i,
                world_id=world,
                query=query,
                expected_action="answer",
                answer_type="entity",
                valid_answers=[answer],
                factors={
                    "exposure": 16,
                    "precision": "categorical",
                    "temporal_status": "stable",
                    "ambiguity": 1,
                    "hops": 1,
                    "domain": domain,
                },
                knowledge=knowledge,
                grading={"method": "canonical_exact"},
                injection_spec={
                    "exposure_count": 16,
                    "training_templates": templates,
                    "parallel_domain_template": True,
                },
                metadata={
                    "domain_shift_features_required": [
                        "embedding_distance",
                        "domain_classifier_log_odds",
                        "prompt_perplexity",
                    ]
                },
            )


def generate_r7() -> Iterable[dict[str, Any]]:
    dimension_id = "R7"
    dimension_name = "Confidence threshold and operating policy"
    profiles = ("easy_known", "low_frequency", "high_precision", "stale_unknown", "multihop")
    per_profile = 1000
    for profile_index, profile in enumerate(profiles):
        for i in range(per_profile):
            global_i = profile_index * per_profile + i
            world = f"r7-world-{profile}-{i:05d}"
            if profile == "easy_known":
                subject = entity_name(global_i, "Archive", 70000)
                answer = person_name(global_i, 71000)
                query = f"Who maintains {subject}?"
                knowledge = [fact(subject, "maintainer", answer)]
                factors = {"exposure": 32, "precision": "categorical", "temporal_status": "stable", "ambiguity": 1, "hops": 1, "domain": "general"}
                action = "answer"
                templates = training_templates(subject, "is maintained by", answer)
                injection_spec = {"exposure_count": 32, "training_templates": templates}
                grading = {"method": "canonical_exact"}
            elif profile == "low_frequency":
                subject = entity_name(global_i, "Archive", 72000)
                answer = person_name(global_i, 73000)
                query = f"Who maintains {subject}?"
                knowledge = [fact(subject, "maintainer", answer)]
                factors = {"exposure": 1, "precision": "categorical", "temporal_status": "stable", "ambiguity": 1, "hops": 1, "domain": "general"}
                action = "answer"
                templates = training_templates(subject, "is maintained by", answer)
                injection_spec = {"exposure_count": 1, "training_templates": templates}
                grading = {"method": "canonical_exact"}
            elif profile == "high_precision":
                subject = entity_name(global_i, "Gauge", 74000)
                value = Decimal((stable_int(global_i, "r7-value") % 9000000) + 1000000) / Decimal("100000")
                answer = f"{value:.5f}"
                query = f"What value was recorded by {subject}? Give exactly five decimal places."
                knowledge = [fact(subject, "measured_value", format(value, "f"))]
                factors = {"exposure": 16, "precision": "decimal_5", "temporal_status": "stable", "ambiguity": 1, "hops": 1, "domain": "scientific"}
                action = "answer"
                templates = training_templates(subject, "recorded the value", format(value, "f"))
                injection_spec = {"exposure_count": 16, "training_templates": templates}
                grading = {"method": "numeric_rounded", "decimal_places": 5, "absolute_tolerance": "0.000005"}
            elif profile == "stale_unknown":
                subject = entity_name(global_i, "Institute", 75000)
                old = person_name(global_i, 76000)
                answer = person_name(global_i, 77000)
                query = f"As of T3, who is the head of {subject}?"
                knowledge = [fact(subject, "head", old, "T0", "T2"), fact(subject, "head", answer, "T2")]
                factors = {"exposure": 16, "precision": "categorical", "temporal_status": "superseded_stale", "ambiguity": 1, "hops": 1, "domain": "general"}
                action = "abstain"
                templates = training_templates(subject, "had head at T0", old)
                injection_spec = {
                    "training_schedule": [
                        {"time": "T0", "operation": "insert", "value": old, "exposure": 16}
                    ],
                    "training_templates": templates,
                    "withhold_current_value": True,
                }
                grading = {"method": "temporal_canonical_exact", "query_time": "T3", "stale_answers": [old]}
            else:
                chain = r5_chain(global_i + 80000)
                answer = chain["answers"][2]
                query = chain["final_queries"][2]
                knowledge = chain["supporting_facts_by_depth"][2]
                factors = {"exposure": 16, "precision": "categorical", "temporal_status": "stable", "ambiguity": 1, "hops": 3, "domain": "general"}
                action = "answer"
                templates = []
                relation_text = {
                    "linked_record": "links directly to",
                    "registered_designation": "has the registered designation",
                }
                for item in knowledge:
                    templates.extend(training_templates(item["subject"], relation_text[item["relation"]], item["object"]))
                injection_spec = {
                    "exposure_count_per_fact": 16,
                    "training_templates": templates,
                }
                grading = {"method": "canonical_exact_with_path", "required_hops": 3}
            yield common_record(
                dimension_id=dimension_id,
                dimension_name=dimension_name,
                level=profile,
                index=i,
                world_id=world,
                query=query,
                expected_action=action,
                answer_type="entity_or_number",
                valid_answers=[answer],
                factors=factors,
                knowledge=knowledge,
                grading=grading,
                injection_spec=injection_spec,
                metadata={
                    "policy_grid_id": "tau_000_100_step_001",
                    "thresholds_applied_posthoc": True,
                    "cluster_analysis_by_world": True,
                    "primary_curves": [
                        "risk_coverage",
                        "selective_risk_coverage",
                        "coverage_at_target_risk",
                    ],
                },
            )


GENERATORS = {
    "r0_baseline_controls.jsonl": generate_r0,
    "r1_exposure_frequency.jsonl": generate_r1,
    "r2_precision.jsonl": generate_r2,
    "r3_temporal.jsonl": generate_r3,
    "r4_ambiguity.jsonl": generate_r4,
    "r5_synthesis_depth.jsonl": generate_r5,
    "r6_domain_shift.jsonl": generate_r6,
    "r7_threshold_policy.jsonl": generate_r7,
}


def atomic_write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts: Counter[str] = Counter()
    split_counts: Counter[str] = Counter()
    level_split_counts: dict[str, Counter[str]] = defaultdict(Counter)
    worlds: set[str] = set()
    ids: set[str] = set()
    sha256 = hashlib.sha256()
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temp_name = handle.name
        for record in records:
            testcase_id = record["testcase_id"]
            if testcase_id in ids:
                raise ValueError(f"Duplicate testcase_id: {testcase_id}")
            ids.add(testcase_id)
            worlds.add(record["world_id"])
            counts[record["level"]] += 1
            split_counts[record["split"]] += 1
            level_split_counts[record["level"]][record["split"]] += 1
            line = json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
            encoded = line.encode("utf-8")
            sha256.update(encoded)
            handle.write(line)
    os.replace(temp_name, path)
    os.chmod(path, 0o644)
    return {
        "file": path.name,
        "records": len(ids),
        "unique_worlds": len(worlds),
        "levels": dict(sorted(counts.items())),
        "splits": dict(sorted(split_counts.items())),
        "level_splits": {
            level: dict(sorted(counter.items()))
            for level, counter in sorted(level_split_counts.items())
        },
        "sha256": sha256.hexdigest(),
        "bytes": path.stat().st_size,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temp_name = handle.name
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temp_name, path)
    os.chmod(path, 0o644)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "testcases",
    )
    args = parser.parse_args()
    random.seed(DEFAULT_SEED)
    summaries = []
    for filename, generator in GENERATORS.items():
        summaries.append(atomic_write_jsonl(args.output_dir / filename, generator()))
    total_records = sum(item["records"] for item in summaries)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generator_seed": DEFAULT_SEED,
        "scientific_roles": {
            "R0": "pipeline_and_negative_controls",
            "R1-R6": "six_controlled_complexity_factors",
            "R7": "secondary_policy_stress_suite",
        },
        "primary_contract_defaults": {
            "loss": "false_commit_per_incoming_query",
            "target_risk": 0.05,
            "calibration_confidence": 0.95,
            "primary_utility": "answer_coverage",
            "joint_group_scope": "aggregate_plus_h3_13_hard_groups",
        },
        "primary_policy_mixture": {
            "included_suites": ["R1", "R2", "R3", "R4", "R5", "R6"],
            "suite_weighting": "equal_total_weight",
            "within_suite_level_weighting": "equal",
            "excluded_from_confirmatory_mixture": ["R0", "R7"],
        },
        "split_policy": {
            "assignment": "world_index modulo 20",
            "ratios": SPLIT_RATIOS,
            "world_grouped": True,
        },
        "r7_threshold_grid": {
            "start": 0.0,
            "stop": 1.0,
            "step": 0.01,
            "application": "posthoc to one cached score per unique query",
        },
        "files": summaries,
        "total_records": total_records,
    }
    write_json(args.output_dir / "manifest.json", manifest)
    print(json.dumps({"output_dir": str(args.output_dir), "total_records": total_records}, indent=2))


if __name__ == "__main__":
    main()
