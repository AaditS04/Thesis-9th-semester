# CalibRead R0–R7 research package

This directory is the executable companion to the full thesis blueprint. It
contains 70,000 deterministic experimental specifications, a protocol for every
research dimension, a hypothesis-by-hypothesis analysis plan, a 26-week
schedule, result schemas, and reproducibility utilities.

## Start here

Read in this order:

1. [P03-to-final crosswalk](plans/00_p03_to_final_crosswalk.md) — authority for scope, hypotheses, and primary endpoints
2. [Master execution index](plans/00_master_execution_index.md)
3. [Unified training and checkpoint plan](plans/08_unified_training_and_checkpoint_plan.md)
4. [Sample-size and power plan](plans/01_sample_size_and_power_plan.md)
5. [Hypothesis execution plan](plans/02_hypothesis_execution_plan.md)
6. [Results and analysis plan](plans/03_results_collection_and_analysis_plan.md)
7. [Detailed 26-week schedule](plans/04_week_by_week_26_week_plan.md)
8. [Complete paper plan](plans/05_complete_research_paper_plan.md)
9. [Operational runbook and data dictionary](plans/06_operational_runbook_and_data_dictionary.md)
10. [Preregistration template](plans/07_preregistration_template.md)
11. [Frozen secondary-scope decisions](plans/09_frozen_secondary_scope_decisions.md)
12. The R0–R7 dimension protocols in [plans/dimensions](plans/dimensions/)
13. [Annotated reference guide](references/ANNOTATED_BIBLIOGRAPHY.md)
14. [Citation-manager-ready BibTeX](references/calibread_references.bib)

The broader motivation, literature synthesis, estimands, conformal framework,
risks, and contribution strategy remain in
[CalibRead_research_blueprint.md](../CalibRead_research_blueprint.md).

Executable inference and paper-analysis code is documented in
[CALIBREAD_CODE_PACKAGES.md](../CALIBREAD_CODE_PACKAGES.md). The two independent
packages are [calibread_openrouter](../calibread_openrouter/) and
[calibread_analytics](../calibread_analytics/).

## End-to-end operating documents

Use these after the study design and code packages are frozen:

1. [Test-execution SOP](operating_protocols/01_TEST_EXECUTION_STANDARD_OPERATING_PROTOCOL.md) — environment setup, public and parametric runs, API configuration, pilots, locked-test execution, recovery, grading, and data acceptance
2. [Analysis SOP](operating_protocols/02_ANALYSIS_STANDARD_OPERATING_PROTOCOL.md) — accepted-input audit, H curves, H1–H5, calibration, risk policies, CPR, figures, sensitivity analyses, and archiving
3. [ICLR paper-writing agent prompt](operating_protocols/03_ICLR_PAPER_WRITING_AGENT_PROMPT.md) — a copy-paste prompt that forces evidence-first manuscript construction and claim-to-result traceability
4. [Testing-code logic and H interpretation](operating_protocols/04_TESTING_CODE_LOGIC_AND_H_INTERPRETATION.md) — code flow, R1–R7 mechanics, exact false-commit estimands, confidence signals, CPR logic, CSV lineage, worked examples, and claim guardrails

## Generated testcases

| Suite | Records | Main manipulated dimension |
|---|---:|---|
| R0 | 8,000 | controls, paraphrase, unknown entity, false premise |
| R1 | 7,000 | exact controlled exposure 0–32 |
| R2 | 16,000 | categorical through five-decimal precision |
| R3 | 8,000 | stable, stale, updated, unavailable-current |
| R4 | 8,000 | one through four valid interpretations |
| R5 | 10,000 | one through five hops |
| R6 | 8,000 | general, biomedical, legal, technical |
| R7 | 5,000 | post-hoc confidence-threshold policy profiles |
| **Total** | **70,000** | |

The files are in [testcases](testcases/). They are generated artifacts: change
the generator, not individual JSONL rows.

## Reproduce and validate

~~~shell
PYTHONPYCACHEPREFIX=/private/tmp/calibread_pycache \
python3 calibread_research/scripts/generate_testcases.py

PYTHONPYCACHEPREFIX=/private/tmp/calibread_pycache \
python3 calibread_research/scripts/validate_testcases.py

PYTHONPYCACHEPREFIX=/private/tmp/calibread_pycache \
python3 calibread_research/scripts/test_materialize_training_corpus.py

PYTHONPATH=calibread_openrouter/src:calibread_analytics/src \
python3 calibread_research/scripts/generate_result_templates.py
~~~

After development outputs exist, create the required blinded grader audit:

~~~shell
python3 calibread_research/scripts/create_output_grader_audit_sample.py \
  --run-dir /absolute/path/to/r0_gate_outputs \
  --run-dir /absolute/path/to/r1_r7_development_outputs \
  --output calibread_research/audits/private/grader_audit_items_blinded.csv

python3 calibread_research/scripts/validate_human_audit_gates.py \
  --grader-audit calibread_research/audits/private/grader_audit_items_blinded.csv
~~~

The sampler creates a separate automated key so reviewers can remain blind.
The validator fails until all 200 testcase rows and all 300 output rows are
completed and the preregistered 98% gates pass.

Materialize the unified initial-stage knowledge-injection corpus. Repeat
`--testcase-file` for all eight suites, as specified in the unified training
plan:

~~~shell
python3 calibread_research/scripts/materialize_training_corpus.py \
  --testcase-file calibread_research/testcases/r0_baseline_controls.jsonl \
  --testcase-file calibread_research/testcases/r1_exposure_frequency.jsonl \
  --testcase-file calibread_research/testcases/r2_precision.jsonl \
  --testcase-file calibread_research/testcases/r3_temporal.jsonl \
  --testcase-file calibread_research/testcases/r4_ambiguity.jsonl \
  --testcase-file calibread_research/testcases/r5_synthesis_depth.jsonl \
  --testcase-file calibread_research/testcases/r6_domain_shift.jsonl \
  --testcase-file calibread_research/testcases/r7_threshold_policy.jsonl \
  --stage initial \
  --output calibread_research/corpora/unified_initial_documents.jsonl
~~~

Do not use the generated `split=test` rows to select prompts, models, features,
thresholds, groups, exclusions, or hypotheses.

## What still requires real experiments

These files specify the study but do not fabricate results. Completion requires:

- controlled knowledge injection or fine-tuning on selected open models;
- frozen-model inference;
- scoring and uncertainty extraction;
- calibration on the calibration split;
- one locked-test analysis;
- human review where deterministic grading is insufficient;
- reporting every planned result, including null results and deviations.

## Reproducibility rules

- Pin model/tokenizer/data revisions rather than names alone.
- Use at least three training seeds for the primary controlled model.
- Keep every world in one split and bootstrap by world.
- Treat stochastic answers as uncertainty samples, not independent testcases.
- Keep raw output append-only.
- Apply the 101 R7 thresholds after generation; never count them as 101 new
  observations.
- Make formal guarantees only for the population, grouping, loss, and sampling
  assumptions actually calibrated and tested.
