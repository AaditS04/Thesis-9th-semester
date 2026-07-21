# CalibRead test-execution standard operating protocol

Document ID: `CALIBREAD-SOP-TEST-001`  
Protocol version: `1.0`  
Applies to: CalibRead R0–R7 inference, result collection, checkpoint provenance,
resume/recovery, and locked-test release  
Workspace root: `/Users/aadit.shah@zomato.com/Documents/thesis`

## 1. Purpose

This SOP begins before the first test command and ends only when the raw and
scored result directories have passed the acceptance checklist and have been
archived. It covers both:

1. non-confirmatory public OpenRouter experiments; and
2. the confirmatory two-checkpoint parametric experiment.

The procedure is deliberately strict because a successful API call is not, by
itself, a scientifically valid CalibRead experiment. The model/checkpoint,
provider, prompts, generation settings, testcase split, grader, and analysis
role must all be attributable to one immutable run.

Do not use this SOP to train the T0/T2 checkpoints. Checkpoint training and
knowledge injection are defined in
`../plans/08_unified_training_and_checkpoint_plan.md`. This SOP starts after a
public model has been chosen or after the trained checkpoint endpoints exist.

## 2. Authoritative files

Read these files before starting:

1. `../../calibread_openrouter/README.md`
2. `../../calibread_openrouter/config.example.json`
3. `../../calibread_openrouter/config.parametric_t2.example.json`
4. `../../calibread_openrouter/config.parametric_t0_temporal.example.json`
5. `../../calibread_openrouter/checkpoint_manifest.example.json`
6. `../plans/07_preregistration_template.md`
7. `../plans/08_unified_training_and_checkpoint_plan.md`
8. `../../calibread_analytics/PAPER_CLAIM_GUARDRAILS.md`

If this SOP and executable code disagree, stop. Record the discrepancy and
resolve it before spending API credits or opening the locked test split.

## 3. Scientific run types

| Evaluation mode | What the model receives | Output status | Permitted scientific use |
|---|---|---|---|
| `closed_book_external` | Public model, no synthetic facts in context | `external_zero_shot_nonconfirmatory` | Baseline, pipeline, and external hallucination diagnostics |
| `contextual_debug` | Synthetic training documents inserted into the prompt | `contextual_pipeline_debug_nonparametric` | Parser, grader, prompt, and infrastructure debugging only |
| `parametric_checkpoint` | Endpoint attested to serve a trained CalibRead checkpoint | `confirmatory_parametric` | Confirmatory H1–H5 and primary CalibRead claims |

Never describe a public-model or contextual-debug result as evidence about
parametric exposure frequency or stored synthetic knowledge.

## 4. The required confirmatory checkpoint layout

The paper experiment consists of two immutable inference runs.

### 4.1 Primary T2 run

- Endpoint: final `checkpoint_t2`.
- Suites: R1–R7 for the primary run; R0 development partitions in separate
  checkpoint-gate runs.
- Levels: all levels.
- `analysis_role`: `primary`.
- `checkpoint_stage`: `checkpoint_t2`.
- Used for: H(θ,Q), H1–H5, calibration, contracts, CPR, main tables, and main
  figures.

### 4.2 Secondary temporal T0 run

- Endpoint: initial `checkpoint_t0`.
- Suite: R3 only.
- Level: `current_after_update` only.
- `analysis_role`: `secondary_temporal`.
- `checkpoint_stage`: `checkpoint_t0`.
- Used for: paired T0-to-T2 controlled-update diagnostics only.
- Explicitly excluded by analytics from H1–H5, H(θ,Q), primary calibration,
  contracts, and CPR.

The two endpoints must use the same preregistered `model.analysis_id`, such as
`calibread-llama8b-seed01`, while retaining their real endpoint slugs in
`model.id`. Include the training seed in `analysis_id`; do not pool distinct
training seeds under one identifier.

## 5. Expected primary final-query counts

These counts exclude R4 clarification turns, R5 component probes, stochastic
samples, P(True) requests, and repeatability duplicates.

| Suite | Fit | Tune | Calibrate | Locked test | Total final queries |
|---|---:|---:|---:|---:|---:|
| R1 | 2,800 | 1,050 | 1,400 | 1,750 | 7,000 |
| R2 | 6,400 | 2,400 | 3,200 | 4,000 | 16,000 |
| R3 | 3,200 | 1,200 | 1,600 | 2,000 | 8,000 |
| R4 | 3,200 | 1,200 | 1,600 | 2,000 | 8,000 |
| R5 | 4,000 | 1,500 | 2,000 | 2,500 | 10,000 |
| R6 | 3,200 | 1,200 | 1,600 | 2,000 | 8,000 |
| R7 | 2,000 | 750 | 1,000 | 1,250 | 5,000 |
| **R1–R7** | **24,800** | **9,300** | **12,400** | **15,500** | **62,000** |

The secondary T0 R3 level contains 800 fit, 300 tune, 400 calibrate, and 500
test queries.

## 6. Roles and separation of responsibilities

For a thesis run one person may fill several roles, but the actions should
still be recorded separately.

- Experiment operator: prepares configs, invokes commands, and monitors errors.
- Freeze reviewer: verifies preregistration and locked-test release conditions.
- Checkpoint owner: supplies model, corpus, checkpoint, training, and seed
  provenance.
- Data reviewer: checks output completeness without selecting favorable
  thresholds or hypotheses.
- Analysis operator: runs the separately frozen analytics package after data
  acceptance.

Write the operator name, date, machine, run IDs, analysis IDs, endpoint IDs,
provider endpoints, and intended run type into the experiment log before the
first paid call.

## 7. Prepare the Python environment

Run from a terminal:

```shell
cd /Users/aadit.shah@zomato.com/Documents/thesis/calibread_openrouter
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
calibread-openrouter --help
```

Expected result: the final command lists `validate`, `models`, `estimate`,
`run`, and `grade`. If the command is missing, confirm that the virtual
environment is active and reinstall the local package.

Do not install or upgrade unrelated research libraries inside this environment
after the freeze. Record `python3 --version` and `python3 -m pip freeze` in the
run log.

## 8. Run all offline preflight checks

These checks make no OpenRouter calls and spend no credits.

```shell
cd /Users/aadit.shah@zomato.com/Documents/thesis

PYTHONPYCACHEPREFIX=/private/tmp/calibread-pycache \
PYTHONPATH=calibread_openrouter/src \
python3 -m unittest discover -s calibread_openrouter/tests -v

PYTHONPYCACHEPREFIX=/private/tmp/calibread-pycache \
PYTHONPATH=calibread_analytics/src \
python3 -m unittest discover -s calibread_analytics/tests -v

PYTHONPYCACHEPREFIX=/private/tmp/calibread-pycache \
python3 calibread_research/scripts/test_materialize_training_corpus.py

python3 calibread_research/scripts/validate_testcases.py \
  --testcase-dir calibread_research/testcases
```

Acceptance conditions:

- every unit test reports `OK`;
- testcase validation reports `"valid": true`;
- testcase validation reports `"total_records": 70000`;
- the validation error list is empty;
- the per-file hashes match the archived testcase manifest used for training.

If a testcase hash differs from the training-corpus provenance, do not run the
checkpoint. A different testcase file means the questions and injected facts
may no longer refer to the same experiment.

## 9. Protect credentials

The API key belongs only in a private config copied from an example. Never put
it in source code, a paper, a notebook, a terminal transcript, a screenshot, or
an issue tracker.

The following private filenames are ignored by the runner package:

- `config.json`
- `config_*.json`
- `outputs/`

Before sharing a config, confirm that `api.api_key` has been replaced with
`REDACTED`. The runner automatically writes `resolved_config.redacted.json` to
the output directory.

## 10. Public-model or infrastructure-debug configuration

For a public-model baseline:

```shell
cd /Users/aadit.shah@zomato.com/Documents/thesis/calibread_openrouter
cp config.example.json config.json
```

Edit only the private copy. At minimum set:

- `api.api_key`;
- `model.id` to the exact `author/model` slug;
- `experiment.run_id`;
- `experiment.output_dir`.

Keep:

- `evaluation_mode=closed_book_external` for a closed-book baseline; or
- use `contextual_debug` only for a clearly labeled nonparametric pipeline
  check.

Do not set `confirm_parametric_injection=true` for a public model.

## 11. Confirmatory parametric configuration

Create private configs:

```shell
cd /Users/aadit.shah@zomato.com/Documents/thesis/calibread_openrouter
cp config.parametric_t2.example.json config_t2.json
cp config.parametric_t0_temporal.example.json config_t0.json
cp checkpoint_manifest.example.json checkpoint_manifest_t2.json
cp checkpoint_manifest.example.json checkpoint_manifest_t0.json
```

### 11.1 Complete both checkpoint manifests

For each manifest set:

- `served_model_id`: exact OpenRouter slug used by that config;
- `base_model_revision`: immutable base-model revision;
- `checkpoint_stage`: `checkpoint_t0` or `checkpoint_t2`;
- `checkpoint_sha256`: real checkpoint digest;
- `corpus_sha256`: real materialized corpus digest;
- `unified_calibread_corpus`: `true`;
- `training_complete`: `true`;
- `training_seed`;
- `data_order_seed`;
- a note identifying the training log and environment manifest.

Do not use example words such as `64-hex-digest`. The manifest is an
attestation and must correspond to evidence in the training archive.

### 11.2 Complete `config_t2.json`

Set:

- API key;
- real T2 endpoint in `model.id`;
- shared frozen family/seed ID in `model.analysis_id`;
- a unique `experiment.run_id`;
- a matching unique `experiment.output_dir`;
- `knowledge_checkpoint_manifest=checkpoint_manifest_t2.json`;
- one frozen provider in `model.provider.only` or `order` when possible.

Confirm these fixed fields:

```text
evaluation_mode       = parametric_checkpoint
analysis_role         = primary
checkpoint_stage      = checkpoint_t2
suites                 = R1,R2,R3,R4,R5,R6,R7
levels                 = []
confirm_parametric_injection = true
```

### 11.3 Complete `config_t0.json`

Set the T0 endpoint and matching T0 manifest. Set exactly the same
`model.analysis_id`, prompt plan, decoding parameters, split membership,
provider policy, confidence method, and seed policy as T2.

Confirm these fixed fields:

```text
evaluation_mode       = parametric_checkpoint
analysis_role         = secondary_temporal
checkpoint_stage      = checkpoint_t0
suites                 = R3
levels                 = current_after_update
confirm_parametric_injection = true
```

Do not add other R3 levels to the T0 secondary run and do not change it to
`analysis_role=primary`.

## 12. Select and lock the OpenRouter model/provider

List models after inserting the API key:

```shell
calibread-openrouter models --config config_t2.json --limit 50
calibread-openrouter models --config config_t2.json --contains llama --limit 20
```

The chosen endpoint must advertise the parameters required by the frozen plan:

- structured output or `response_format`;
- `logprobs` if `request_logprobs=true`;
- `seed` for the repeatability audit.

For the paper run:

- set a specific provider endpoint in `model.provider.only` or `order`;
- keep `allow_fallbacks=false`;
- keep `require_parameters=true`;
- keep `data_collection=deny` unless an approved data policy says otherwise;
- set `zdr=true` only if the selected provider supports and requires the ZDR
  routing restriction;
- do not use an alias that silently changes model revision during collection.

Record the selected model metadata, context length, parameter list, pricing,
provider slug, and date in the experiment log.

## 13. Validate configurations

Offline validation checks paths, roles, stages, manifests, split gates, and
configuration consistency:

```shell
calibread-openrouter validate --config config_t2.json
calibread-openrouter validate --config config_t0.json
```

Online validation additionally queries OpenRouter model metadata:

```shell
calibread-openrouter validate --config config_t2.json --online
calibread-openrouter validate --config config_t0.json --online
```

Acceptance conditions:

- `"valid": true`;
- correct `scientific_status`;
- no parameter-support warnings;
- manifest stage equals config stage;
- manifest served model equals config `model.id`;
- config hash is recorded.

With `require_parameters=true`, unsupported structured output, logprobs, or
seed support is a hard failure. Choose a compatible endpoint or formally amend
the frozen feature plan before the test split—not after seeing test results.

## 14. Estimate volume and cost before calling the model

Run estimates separately by suite and split. Examples:

```shell
calibread-openrouter estimate --config config_t2.json --suite R1 --split fit
calibread-openrouter estimate --config config_t2.json --suite R4 --split fit
calibread-openrouter estimate --config config_t2.json --suite R5 --split fit
calibread-openrouter estimate --config config_t0.json --suite R3 --split fit
```

R4 has extra second-turn clarification requests. R5 has component probes. Each
final query also has one greedy generation plus the configured number of
stochastic samples, repeatability requests on the selected subset, and
optionally one P(True) call. Therefore API request count is intentionally
larger than testcase count.

Calculate a conservative budget from:

```text
estimated input tokens × provider input price
+ estimated output tokens × provider output price
+ retry reserve
+ pilot reserve
```

Do not infer full-run cost only from testcase count. Use the pilot’s actual
`usage.cost`, input-token, and output-token fields.

## 15. Run an isolated pilot

Never turn the final output directory into a pilot directory. Copy the config
to a new git-ignored filename and change both run ID and output directory.

Example:

```shell
cp config_t2.json config_pilot_t2.json
```

In the pilot config set:

```json
"run_id": "calibread_pilot_t2_001",
"output_dir": "outputs/calibread_pilot_t2_001",
"limit_per_suite": 10
```

Then:

```shell
calibread-openrouter validate --config config_pilot_t2.json --online
calibread-openrouter estimate --config config_pilot_t2.json --suite R1 --split fit
calibread-openrouter run --config config_pilot_t2.json --suite R1 --split fit
```

Inspect only pilot results. Confirm:

- requests complete;
- JSON parses under the strict response contract;
- model and provider returned are the intended ones;
- prompts and message hashes are populated;
- token/cost/latency fields are populated when offered by the provider;
- scored rows contain factual/action/commit labels;
- exact agreement is agreement with the greedy response, not merely the modal
  response;
- answer-token NLL is missing rather than incorrectly substituted when token
  alignment is impossible;
- no API key appears in outputs;
- estimated full cost remains approved.

The output directory is locked to one run ID and config hash. Removing the
pilot limit changes the hash; start the final run in the final output directory
instead of reusing the pilot directory.

## 16. Understand the frozen response contract

Every inference response must be one JSON object:

```json
{
  "action": "ANSWER|ABSTAIN|CLARIFY|REJECT_PREMISE",
  "answer": "string or null",
  "clarification": "string or null"
}
```

Semantic rules:

- `ANSWER`: non-empty answer, null clarification;
- `CLARIFY`: null answer, non-empty clarification;
- `ABSTAIN` or `REJECT_PREMISE`: null answer and null clarification.

The parser does not repair semantic violations. A malformed non-answer action
that contains a substantive answer payload is treated as a commit and can
become a false commit.

## 17. Run development partitions

Development partitions are fit, tune, and calibrate. They may be executed in
one command:

```shell
calibread-openrouter run --config config_t2.json \
  --split fit --split tune --split calibrate

calibread-openrouter run --config config_t0.json \
  --split fit --split tune --split calibrate
```

Or they may be divided by suite for monitoring:

```shell
calibread-openrouter run --config config_t2.json --suite R1 \
  --split fit --split tune --split calibrate

calibread-openrouter run --config config_t2.json --suite R2 \
  --split fit --split tune --split calibrate
```

Repeat for R3–R7. Separate invocations are safe: immutable observation specs
and R5 links are merged, and successful request keys are not called again.

Do not change config settings between suite invocations. The runner refuses to
mix a different config hash into the same output directory.

## 18. Monitor a running collection

Monitor these output files:

- `raw_generations.csv`: append-only request-level ledger;
- `run_summary.csv`: suite/split request, error, token, and cost totals;
- `model_metadata.json`: selected model capabilities and pricing;
- `resolved_config.redacted.json`: API-key-free resolved config.

Do not edit `raw_generations.csv`. Do not delete failure rows. Failed requests
are evidence of the collection process and are retried on the next resume.

After any interruption, rerun the identical command. The runner identifies
completed requests by observation ID, sample kind, and sample index. Successful
requests are skipped; incomplete/error requests are retried.

## 19. R4-specific behavior

For ambiguity levels 2–4 the correct first action is `CLARIFY`. A singleton
answer is an operational false commit even if it matches one possible role.

When enabled, the runner:

1. records the frozen first-turn response;
2. creates one simulated clarification choice for each valid office;
3. reuses the exact first-turn response in conversation history;
4. sends the clarified second turn;
5. scores those second turns as auxiliary clarification observations.

Do not mix first-turn and second-turn rows in the primary H denominator. The
analytics package uses `observation_kind=final` for primary metrics and reports
clarification rows separately.

## 20. R5-specific behavior

For every synthesis graph, the runner generates direct component probes. A
component query shared by several depth questions in the same world is
deduplicated. `component_links.csv` joins each final question to its required
component observations.

Do not treat component probes as independent primary testcases. H2 conditions
on all required components being answered correctly and clusters by graph/world.

## 21. Repeatability and nondeterminism subset

The first frozen subset per suite receives repeated, identical temperature-zero
requests. Repeats use:

- the same messages and message hash;
- the same model and requested provider controls;
- the same temperature, top-p, maximum tokens, and seed.

Repeat rows have `sample_kind=greedy_repeat`. They are excluded from confidence
estimation and used only in the nondeterminism audit. The audit reports exact
text repeatability, parsed JSON repeatability, parameter identity, backend
metadata stability, and fingerprint availability.

Do not substitute stochastic samples for this audit.

## 22. Development-side review before locked-test release

Create the 300-output blind audit with
`create_output_grader_audit_sample.py`. It draws exactly 100 R0 and 200
stratified R1–R7 fit/tune/calibrate outputs and creates a separate automated
key. Reviewers fill the blinded file before the key is joined. Run
`validate_human_audit_gates.py`; it also checks the existing 200-row
testcase audit and fails unless both samples are complete and deterministic
agreement/acceptance are at least 98%. Never fill these human fields
automatically.

Before opening test, confirm using fit/tune/calibrate only:

- the preregistration is complete and timestamped;
- primary model/analysis ID is fixed;
- prompts and response schema are fixed;
- grader behavior is fixed;
- the 200-testcase and 300-output human audit gates pass;
- H definition and denominators are fixed;
- H1–H5 endpoints, margins, and Holm family are fixed;
- confidence score is fixed;
- threshold grid is fixed;
- hard groups are fixed;
- CPR alpha and candidate-generation settings are fixed;
- exclusions and minimum group size are fixed;
- T0/T2 roles are fixed;
- code and config hashes are archived;
- pilot results are excluded from primary analysis;
- the output has no unexplained provider/model drift;
- API budget remains sufficient to finish test without changing settings.

Do not choose a model, prompt, threshold, subgroup, hypothesis, or exclusion
because it looks favorable on test. Test must still be unopened at this stage.

## 23. Archive the pre-test freeze

Archive at least:

- runner and analytics source trees;
- prompts;
- testcase manifest and hashes;
- T0/T2 checkpoint manifests;
- redacted configs;
- preregistration;
- model/provider metadata;
- environment information;
- development result directory hashes;
- the planned analysis command.

Example hashing command:

```shell
cd /Users/aadit.shah@zomato.com/Documents/thesis
shasum -a 256 \
  calibread_openrouter/config.parametric_t2.example.json \
  calibread_openrouter/config.parametric_t0_temporal.example.json \
  calibread_analytics/analysis_config.parametric.example.json \
  calibread_research/prompts/*.txt
```

Hash the actual private configs only after creating redacted copies. Never send
the key-bearing originals to an archive shared with others.

## 24. Release and run locked test

Only after the freeze reviewer approves release, set this exact value in each
private final config:

```json
"test_release_attestation": "I_CONFIRM_WEEK20_FREEZE_IS_ARCHIVED"
```

The attestation is an access acknowledgment and is excluded from the scientific
config hash, so adding it after freeze does not change the model/prompt
experiment identity.

Run primary T2 test:

```shell
calibread-openrouter run --config config_t2.json --split test
```

Run secondary T0 paired temporal test:

```shell
calibread-openrouter run --config config_t0.json --split test
```

Do not inspect partial test effects to decide whether to stop, change settings,
or add samples. Operational interruption is allowed; resume with the identical
config and command until all planned request keys are complete.

## 25. Rebuild derived CSVs without new API calls

If raw collection is complete but derived files need rebuilding:

```shell
calibread-openrouter grade --config config_t2.json
calibread-openrouter grade --config config_t0.json
```

`grade` reads cached raw output and immutable observation specs. It does not
call OpenRouter. Use this after code verification only; if grader code changed
after the freeze, record a protocol deviation and do not silently replace the
original scored results.

## 26. Output directory contents

Each run directory must contain:

| Artifact | Unit | Purpose |
|---|---|---|
| `raw_generations.csv` | API request/sample | Immutable outputs, errors, tokens, cost, messages, hashes, model/provider/fingerprint |
| `scored_results.csv` | Observation | Deterministic action, factual, commit, H-loss, and confidence features |
| `candidate_sets.csv` | Candidate answer cluster | CPR ranking and correctness |
| `component_links.csv` | Parent-component link | R5 graph conditioning |
| `run_summary.csv` | Suite/split | Completeness, errors, token usage, and cost |
| `observation_specs.jsonl` | Observation specification | Frozen join metadata needed to regrade |
| `resolved_config.redacted.json` | Run | Resolved key-free config and hash |
| `model_metadata.json` | Run | Model capabilities, pricing, warnings |
| `by_suite/R1` … `by_suite/R7` | Suite | Independently inspectable scored/candidate exports |

An empty by-suite CSV is acceptable for a suite not included in that run. It is
not acceptable when the suite was planned and raw/scored rows are missing.

## 27. Post-collection acceptance checks

Run from the runner directory with the virtual environment active.

### 27.1 Confirm there are no missing required files

```shell
ls -lh outputs/calibread_parametric_t2_001
ls -lh outputs/calibread_parametric_t0_temporal_001
```

### 27.2 Inspect summary counts and errors

```shell
python3 -c 'import csv; p="outputs/calibread_parametric_t2_001/run_summary.csv"; rows=list(csv.DictReader(open(p))); print("summary_rows",len(rows)); print("errors",sum(int(float(r["error_rows"] or 0)) for r in rows)); print("cost",sum(float(r["cost_credits"] or 0) for r in rows))'
```

Repeat with the T0 output path.

### 27.3 Count primary final observations by suite/split

```shell
python3 -c 'import csv,collections; p="outputs/calibread_parametric_t2_001/scored_results.csv"; c=collections.Counter((r["dimension_id"],r["split"]) for r in csv.DictReader(open(p)) if r["observation_kind"]=="final" and r["analysis_role"]=="primary"); print(*sorted(c.items()),sep="\n")'
```

Compare against Section 5. Do not compare total scored rows to final-query
counts because total rows also contain R4 clarification and R5 component
observations.

### 27.4 Confirm roles and checkpoint stages

```shell
python3 -c 'import csv,collections; paths=["outputs/calibread_parametric_t2_001/scored_results.csv","outputs/calibread_parametric_t0_temporal_001/scored_results.csv"]; [print(p,collections.Counter((r["analysis_role"],r["checkpoint_stage"],r["dimension_id"],r["level"]) for r in csv.DictReader(open(p)))) for p in paths]'
```

Acceptance conditions:

- T2 rows are `primary/checkpoint_t2`;
- T0 rows are `secondary_temporal/checkpoint_t0`;
- T0 contains only R3 `current_after_update`;
- both use the same intended `model_id` analysis family;
- actual endpoint fields distinguish T0 and T2.

### 27.5 Confirm test rows are present only after release

The final accepted directory should contain the expected test counts. The
archived pre-release snapshot must not contain test rows.

### 27.6 Confirm raw errors are resolved

Error rows may remain as an audit trail, but every planned request key must also
have a successful row after resume. `observations_scored` should match expected
observation specs. Investigate any `finish_reason`, parser, or model/provider
anomaly before analysis.

## 28. Failure handling

| Failure | Required action |
|---|---|
| 401/403 | Stop; verify key and endpoint authorization without printing the key |
| 404 model | Refresh current model listing; do not substitute a different model under the same run ID |
| 429 | Preserve output, lower operational request rate only if allowed by the frozen operational plan, then resume |
| 5xx/timeout | Resume identical run; retries and attempt counts remain in raw data |
| Unsupported parameter | Select a compatible endpoint before test or preregister an amended feature plan |
| Structured-output schema error | Stop pilot/development; do not repair test responses manually |
| Config hash mismatch | Use the original config or create a new run ID/output directory |
| Observation-spec conflict | Stop; the same immutable observation ID was generated differently |
| Provider/model drift | Stop and investigate; do not pool unexplained endpoint changes |
| Missing answer-token logprobs | Leave NLL missing; do not substitute full-response likelihood |
| Disk interruption | Preserve directory and resume identical command |
| Grader bug found after test | Preserve original outputs, document deviation, repair transparently, and report both when required |

## 29. Data-handling rules

- Never delete material failure rows.
- Never edit raw model text.
- Never hand-correct a CSV answer.
- Never merge different config hashes into one run directory.
- Never move a world between fit/tune/calibrate/test.
- Never count stochastic samples as independent testcases.
- Never count R7 thresholds as additional observations.
- Never use second-turn clarification observations in the primary H denominator.
- Never pool different training seeds under one `analysis_id`.
- Keep the API key only in ignored private configs.
- Archive outputs read-only after acceptance.

## 30. Final handoff to analysis

The experiment is ready for the analysis SOP only when all statements below are
true:

- [ ] Offline tests pass.
- [ ] All 70,000 testcase records validate.
- [ ] T0/T2 checkpoint and corpus hashes are real and archived.
- [ ] Both configs validate online without warnings.
- [ ] Pilot completed in a separate directory.
- [ ] Development collection is complete.
- [ ] Preregistration and code/config freeze are archived.
- [ ] Test attestation was added only after freeze.
- [ ] Primary T2 test collection is complete.
- [ ] Secondary T0 temporal collection is complete.
- [ ] Expected final-query counts match.
- [ ] R4 clarification and R5 component artifacts exist.
- [ ] Every planned request key has a successful result.
- [ ] Model/provider/stage/role provenance is correct.
- [ ] Raw and scored directories have been hashed and made read-only or copied
  to an immutable archive.
- [ ] No result-dependent model, prompt, threshold, group, or exclusion change
  occurred.

Proceed next to `02_ANALYSIS_STANDARD_OPERATING_PROTOCOL.md`.
