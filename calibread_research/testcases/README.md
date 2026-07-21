# CalibRead testcase suite

## Contents

| File | Records | Experimental unit |
|---|---:|---|
| r0_baseline_controls.jsonl | 8,000 | paired baseline/control query |
| r1_exposure_frequency.jsonl | 7,000 | independent stored/unstored fact |
| r2_precision.jsonl | 16,000 | 2,000 worlds × eight precision variants |
| r3_temporal.jsonl | 8,000 | temporal-state fact |
| r4_ambiguity.jsonl | 8,000 | 2,000 worlds × four ambiguity variants |
| r5_synthesis_depth.jsonl | 10,000 | 2,000 graphs × five depth variants |
| r6_domain_shift.jsonl | 8,000 | parallel domain fact |
| r7_threshold_policy.jsonl | 5,000 | unique query scored over post-hoc thresholds |
| manifest.json | — | counts, split policy, hashes |
| testcase.schema.json | — | JSON Schema |
| human_audit_sample.csv | 200 | stratified manual-review sheet |

Total: 70,000 records; 17,500 belong to the sealed test split.

## What one record represents

A record is an experimental specification. It contains:

- query and valid answer;
- expected action;
- factor profile;
- ground-truth knowledge;
- knowledge-injection instructions;
- grading rule;
- split and grouping key;
- dimension-specific metadata.

It does not contain model output.

## Splits

- fit 40%;
- tune 15%;
- calibrate 20%;
- test 25%.

All queries derived from the same world remain in one split. Never reshuffle individual rows.

## Generation and validation

From the thesis workspace:

~~~shell
PYTHONPYCACHEPREFIX=/private/tmp/calibread_pycache \
python3 calibread_research/scripts/generate_testcases.py

PYTHONPYCACHEPREFIX=/private/tmp/calibread_pycache \
python3 calibread_research/scripts/validate_testcases.py
~~~

The generator is deterministic with seed 20260722. The validator checks:

- exact counts;
- level balance;
- split ratios;
- unique IDs;
- world grouping;
- required fields/factors;
- dimension-specific invariants;
- manifest hashes.

Create or refresh the deterministic, level-stratified review sheet:

~~~shell
python3 calibread_research/scripts/create_human_audit_sample.py
~~~

By default, the sheet samples 25 fit/tune case specifications from every R-file
(200 total) and never touches calibrate/test. It is a construction audit, not
the model-output grader audit. It is intentionally ungraded: two human reviewers must
complete its accept/reject and issue columns. An empty audit sheet is not
evidence that the generated semantics are valid. After the week-20 lock and
one-shot test run, create a separate 200-case test-only audit with `--split test
--output <separate-path>` and join those same case IDs to frozen model outputs.
Findings may qualify labels/results but may not trigger prompt, policy, or
hypothesis tuning.

## Materializing training documents

Use injection_spec rather than copying the evaluation query into training.

For ordinary exposure:

1. read training_templates;
2. for exposure_count, cycle the single fact's templates to the target count;
3. for exposure_count_per_fact, divide templates into contiguous fact groups and
   cycle every group to the target count;
4. preserve the stable data-order/shuffle manifest.

For R3, materialize the T0 schedule steps into the unified initial corpus and
non-T0 steps into the temporal update corpus. If `withhold_current_value` is
true, do not materialize the current value.

Use `scripts/materialize_training_corpus.py`; it implements these rules and
deduplicates paired queries by world across repeated input files. Use the exact
commands in `plans/08_unified_training_and_checkpoint_plan.md`. Tokenizer-aware
filler, if needed for a separate corpus-changing ablation, belongs to an
external verified preparation step and is not a materializer guarantee.

## Important interpretation notes

- R0 is a baseline/control suite created for this study.
- R1 is exact controlled exposure, not estimated web frequency.
- R3 is storage availability/supersession, not passive calendar-time memory decay.
- R4 requires action grading; one plausible answer is not a complete response to an ambiguous query.
- R5 uses matched Designation answers at every depth. Its primary H2 analysis is graph-level conditional composition error among all-components-correct observations; the cross-fitted independence product is a separate all-graphs diagnostic.
- R7 thresholds are applied after scoring. Its 101 thresholds are not independent cases.

## Extension policy

To add more cases:

- change generator counts;
- increment generator/schema version;
- regenerate every file;
- rerun validation;
- record new manifest;
- do so before opening locked test results.

Do not hand-edit generated JSONL records.
