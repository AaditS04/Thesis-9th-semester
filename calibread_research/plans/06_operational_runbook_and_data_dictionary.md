# Operational runbook and data dictionary

This file turns the methodology into a repeatable sequence. A researcher should
be able to stop after any phase and determine exactly which inputs, outputs, and
quality gates exist.

## 1. One-time project setup

Create and freeze:

- a source-control repository;
- an environment lock file;
- a model registry with exact revisions and licenses;
- a dataset registry with source, version, license, and checksum;
- an experiment registry with immutable run IDs;
- a decision/deviation log;
- a compute ledger;
- an annotation rubric and conflict procedure.

Recommended run ID:

~~~text
YYYYMMDD_model_dimension_split_trainseed_decodeseed_shortconfighash
~~~

Never encode the observed result into a run ID or filename.

## 2. Testcase lifecycle

### 2.1 Generate

Run `scripts/generate_testcases.py`. The seed, generator version, schema version,
counts, and split assignment are source-controlled.

### 2.2 Validate mechanically

Run `scripts/validate_testcases.py`. The command must return exit status zero and
`"valid": true`.

### 2.3 Audit manually

Before any expensive training, sample 25 fit/tune rows from every file,
stratified by level. Calibration and test rows are ineligible for this
design-repair audit. Two reviewers verify:

- the query is grammatical;
- the valid answer follows from knowledge;
- the expected action is correct;
- no extra interpretation invalidates the label;
- precision and temporal wording are exact;
- entity strings do not accidentally reveal the answer;
- the training template is not an evaluation-query copy.

Record accept/reject plus reason. Repair the generator and regenerate the entire
suite; never patch a generated row.

After the week-20 lock and one-shot test run, create a different blinded
test-only artifact with 25 test case IDs per suite, then join those same 200
specifications to their frozen model outputs. This is the single locked-test
quality audit, not two independent samples. Findings may be reported as
label/data deviations but cannot change prompts, graders, policies, hypotheses,
or inclusion rules.

### 2.4 Freeze

Copy the manifest hash into the preregistration and every experiment manifest.
Opening test results freezes that testcase version permanently for the paper.

## 3. Testcase field dictionary

| Field | Type | Meaning | Analysis use |
|---|---|---|---|
| schema_version | string | record contract revision | compatibility gate |
| generator_version | string | generator logic revision | reproducibility |
| testcase_id | string | globally unique query ID | joins and completeness |
| dimension_id | R0–R7 | experimental suite | partition/analysis |
| dimension_name | string | human-readable suite | reports |
| level | string | manipulated cell/profile | planned contrast |
| world_id | string | shared latent fact/graph | splitting/bootstrap |
| split | enum | fit/tune/calibrate/test | leakage prevention |
| generation_seed | integer | deterministic row seed | regeneration |
| query | string | exact inference question | prompt input |
| expected_action | enum | answer/abstain/clarify/reject/set | action loss |
| answer_type | string | semantic response type | parsing |
| valid_answers | list | canonical acceptable target(s) | grading |
| factors | object | exposure/precision/time/ambiguity/hops/domain | profiler/models |
| knowledge | list | controlled world facts | injection/reference |
| grading | object | deterministic grading contract | scorer routing |
| injection_spec | object | exposure and paraphrase schedule | corpus build |
| metadata | object | suite-specific auxiliary labels | secondary analysis |

`valid_answers` on an abstention case records the unavailable ground truth for
diagnosis; it does not change the expected action. For false-premise R0 cases it
is empty because rejecting the premise is the complete expected response.

## 4. Corpus materialization

### 4.1 Command

Use the repeated-`--testcase-file`, stage-aware commands in
`08_unified_training_and_checkpoint_plan.md`. The confirmatory design produces
one unified initial corpus and one temporal-update corpus, not one adapter or
checkpoint per suite.

### 4.2 Materializer guarantees

- one injection program per world;
- exact exposure counts;
- even cycling through paraphrase templates;
- temporal steps emitted in declared order;
- future/current facts withheld when specified;
- stable per-document shuffle keys;
- output checksum;
- source testcase traceability.

### 4.3 Corpus checks

For each dimension and level, calculate:

- expected versus observed occurrences per fact;
- number of facts and documents;
- token-length distribution under the target tokenizer;
- answer-string token length;
- duplicate-document rate;
- accidental test-query overlap;
- presence/absence of the current value for R3/R7 stale cases;
- relation and entity vocabulary balance.

Randomize the R1 entity-to-exposure assignment once, record it, and reuse that
same assignment for every model size and optimizer seed. Training seeds vary
only optimizer/data order. The confirmatory unified document stream and token
budget must be identical across seeds/models. If a separate ablation genuinely
changes corpus length, add tokenizer-aware unrelated filler in an external
training-preparation step; the materializer itself does not claim to do this.

## 5. Model training run

### 5.1 Frozen inputs

- base model and tokenizer revision;
- materialized corpus hash;
- data-order seed;
- optimizer, scheduler, precision, batch size, sequence length;
- number of tokens/steps;
- adapter/full-tune method;
- checkpoint policy;
- three training seeds;
- general-capability sanity set.

### 5.2 Training outputs

- complete config;
- stdout/stderr log;
- environment and hardware metadata;
- step-level loss and learning rate;
- checkpoint or adapter hash;
- wall time, GPU-hours, peak memory, energy if available;
- interruptions and resumes.

### 5.3 Training acceptance gates

- no NaN or unexplained loss explosion;
- planned token count reached;
- checkpoint reload reproduces a fixed probe;
- exposure counts match the manifest;
- at every included checkpoint, raw R0 known-direct accuracy exceeds 70%, direct-to-paraphrase loss is below 20 absolute points, grading agreement passes, and split integrity passes;
- raw R0 unknown false-commit and false-premise rejection behavior is reported but is not used as a pre-calibration policy gate;
- no unexplained collapse on the sanity set.

After the controller is calibrated, run a separate policy sanity check on R0
unknown and false-premise strata under the frozen 5% false-commit contract.

## 6. Frozen inference contract

Use the exact text in `prompts/read_system.txt` and the appropriate output
schema. The model must select one action:

- `ANSWER`: return a value;
- `ABSTAIN`: insufficient reliable stored knowledge;
- `CLARIFY`: ambiguity prevents a unique response;
- `REJECT_PREMISE`: an explicit premise conflicts with stored knowledge.

For every testcase/model/training seed:

1. one deterministic/greedy response;
2. five stochastic responses for the primary uncertainty estimate;
3. fixed temperature, top-p, maximum tokens, and stop sequence;
4. token log probabilities when the model API permits;
5. raw response saved before parsing.

Use sampling budgets 1, 3, 5, 10, and 20 only on the preregistered ablation
subset. Never adapt generation parameters after inspecting test failures.

## 7. Raw-generation field dictionary

Compound primary key:

~~~text
(run_id, testcase_id, sample_index)
~~~

Required fields:

| Group | Fields |
|---|---|
| identity | run_id, testcase_id, sample_index |
| model | provider, model_id, model_revision, tokenizer_revision, checkpoint_hash |
| training | train_seed, corpus_hash, data_order_seed |
| prompt | system_prompt, system_prompt_hash, exact user_prompt or immutable user_prompt_uri, user_prompt_hash |
| decoding | decoding_seed, temperature, top_p, max_new_tokens, stop |
| output | raw_text, token_ids, token_logprobs, finish_reason |
| determinism | inference_engine, engine_version, attention_backend, deterministic_algorithms, kernel_mode, tensor_parallel, pipeline_parallel, batch_size, batch_schedule_hash, request_order_hash, repeatability_audit_id |
| operations | timestamp_utc, latency_ms, input_tokens, output_tokens, gpu_seconds |
| errors | status, retry_count, error_code, error_message |

Retries keep the same key and append an attempt record; they do not silently
replace failed raw data.

## 8. Parsing and grading

### 8.1 Parser order

1. validate the JSON response;
2. parse action;
3. normalize Unicode and whitespace;
4. preserve raw answer;
5. normalize aliases, dates, or numeric text according to grading metadata;
6. mark malformed output rather than inventing a value.

### 8.2 Deterministic graders

- canonical/alias exact match for entities and codes;
- calendar-aware date parsing;
- decimal rounding/tolerance from `grading`;
- stale versus current answer classification;
- set precision, recall, and F1 for ambiguity;
- required component/path validation for synthesis;
- action correctness for abstain/clarify/reject.

Also derive `commit_correct` and the primary loss. For ordinary unique-answer
rows, commit correctness equals frozen factual correctness. For R4 ambiguity
levels 2–4, a singleton commit is operationally incorrect even if it matches one
plausible role. Then
`false_commit_loss = 1(parsed_action == ANSWER and not commit_correct)`.

### 8.3 Human review

Send to blinded review:

- unresolved parser/format cases not already determined by the frozen malformed-output rule;
- semantic aliases not covered by the frozen list;
- automatic-grader conflicts;
- all natural-data semantic matches;
- all high-confidence errors for error taxonomy, not label alteration.

Execute the fixed audit streams and sample sizes in Section 7 of
`03_results_collection_and_analysis_plan.md`: 200 testcase specifications, 300
development grader outputs, 200 development R4 clarifications, and a separate
200-output locked-test quality sample. The construction and development audits
cannot contain calibrate/test cases. Natural-dataset random auditing uses the
prespecified capped 5% rule there. Targeted conflicts and high-confidence errors
are never used as unbiased rate estimates.

Report raw agreement, Cohen's kappa or Krippendorff's alpha as appropriate, and
adjudication counts.

## 9. Uncertainty feature extraction

Compute without test-label fitting:

- answer mean/total negative log-likelihood;
- minimum generated-token probability;
- P(True) under a frozen prompt;
- exact sample agreement;
- exact answer entropy;
- deterministic query-only complexity profile.

Exact agreement is primary; P(True) and token scores are optional
availability-labelled diagnostics. Verify orientation on tune and save feature
version, sampling count, and compute cost.

## 10. Calibration and policy selection

### 10.1 Partition use

- fit: calibration-map parameters and profile penalties;
- tune: feature selection, finite policy grid, prompt selection;
- calibrate: conformal quantile/risk tests only;
- test: final evaluation once.

### 10.2 Required policy sequence

1. H3 aggregate-only global diagnostic policy;
2. H4 global joint-safe policy tested against aggregate plus all 13 hard groups;
3. declared group/domain baseline;
4. continuous adaptive or recent conditional baseline;
5. CCRC predicted-profile deployment version under the same joint family as item 2;
6. CCRC deterministic query-profile assignment audit.

If a calibration group is below its frozen minimum, route to its declared parent.
If no supported policy passes the risk test, output `unsupported`; do not choose
the least-bad invalid policy.

## 11. Final analysis execution

Before opening test:

- sign off testcase/model/prompt/scorer/policy hashes;
- render empty final tables from the result templates;
- run every analysis on synthetic mock labels;
- freeze exclusions and hypothesis code;
- have a second person verify no test read path exists in tuning code.
- verify no locked-test generation, grading, parsed output, or summaries exist.

After opening test:

1. generate and grade the sealed test for the first time with the frozen pipeline;
2. verify row counts and compound-key uniqueness;
3. generate H1–H5 outputs together;
4. compute world-cluster confidence intervals;
5. apply Holm correction across five primary hypotheses;
6. run prespecified sensitivity analyses;
7. label everything else exploratory;
8. write deviations before interpretation;
9. archive the complete result manifest.

## 12. Backup and recovery

At the end of each completed run, store in two locations:

- config and manifest;
- code checksum/commit;
- raw output checksum;
- parsed/scored/aggregate checksums;
- logs;
- paper figure/table revision that consumed the run.

A result is reproducible only if another researcher can start from the manifest
and reach the same aggregate table without undocumented manual edits.
