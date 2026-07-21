# CalibRead master execution index

## Start here

This directory turns the P03 concept into an executable research program.

Recommended reading order:

1. 00_p03_to_final_crosswalk.md
2. ../../CalibRead_research_blueprint.md
3. 08_unified_training_and_checkpoint_plan.md
4. 01_sample_size_and_power_plan.md
5. dimensions/R0_baseline_controls_protocol.md
6. dimensions/R1_exposure_frequency_protocol.md through R7
7. 02_hypothesis_execution_plan.md
8. 03_results_collection_and_analysis_plan.md
9. 04_week_by_week_26_week_plan.md
10. 05_complete_research_paper_plan.md
11. 06_operational_runbook_and_data_dictionary.md
12. 07_preregistration_template.md
13. ../testcases/README.md

The crosswalk is authoritative for research scope, estimands, hypotheses, and
primary endpoints. A dated preregistration amendment is required to supersede
it.

## Package outputs

- 70,000 validated case specifications.
- Eight separate R0–R7 JSONL files.
- Deterministic generator.
- Structural validator.
- Testcase manifest with SHA-256 hashes.
- Per-dimension execution protocols.
- Sample-size justification.
- Hypothesis plan.
- Results/data plan.
- 26-week plan.
- Paper plan.
- Operational runbook, data dictionary, frozen prompt, and run manifest template.
- Fill-in preregistration for H1–H5.

## Research dependency order

\[
\text{Definitions}
\rightarrow
\text{Testcases}
\rightarrow
\text{Knowledge injection}
\rightarrow
\text{R0 gates}
\rightarrow
\text{Uncertainty}
\rightarrow
\text{Published conformal baseline}
\rightarrow
\text{CCRC}
\rightarrow
\text{Locked evaluation}
\rightarrow
\text{Paper}
\]

Do not skip dependency gates.

## Non-negotiable decisions by week 6

- confirmation of the primary false-commit risk per incoming query at target 0.05 and calibration confidence 0.95;
- confirmation of the four model action labels and external answer-set construction;
- model panel;
- training seeds;
- testcase counts;
- prompt;
- grading rules;
- five hypotheses;
- group list;
- multiplicity plan;
- target risk levels;
- exclusions;
- compute budget.

## Core commands

Generate:

~~~shell
PYTHONPYCACHEPREFIX=/private/tmp/calibread_pycache \
python3 calibread_research/scripts/generate_testcases.py
~~~

Validate:

~~~shell
PYTHONPYCACHEPREFIX=/private/tmp/calibread_pycache \
python3 calibread_research/scripts/validate_testcases.py
~~~

Materialize the controlled unified corpus using the repeated-file command in
`08_unified_training_and_checkpoint_plan.md`. A suite-specific example is not a
valid confirmatory training design.

## Definition of done

The project is finished only when:

- R0 passes;
- all main raw outputs are immutable and complete;
- all five hypotheses have frozen result records;
- one precisely defined risk is controlled/tested;
- aggregate and worst-group performance are reported;
- natural shift is evaluated;
- every table/figure is reproduced from artifacts;
- limitations match the actual guarantee;
- the full paper and artifact pass clean-environment reproduction.
