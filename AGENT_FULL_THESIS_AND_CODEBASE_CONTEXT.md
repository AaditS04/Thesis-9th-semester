# CalibRead Thesis and Codebase: Full Agent Context

**Context snapshot date:** 2026-07-22  
**Workspace:** `/Users/aadit.shah@zomato.com/Documents/thesis`  
**Intended reader:** a new research or coding agent taking over the project  
**Status:** comprehensive handoff, not a replacement for the authoritative
proposal, preregistration, SOPs, code, or the current repair plan

**Repair update:** The original audit state described in parts of this snapshot
has been superseded by the completed 2026-07-22 code/method repair pass. Read
Section 23 and the repair ledger in
FINAL_CONSISTENCY_ISSUES_AND_REPAIR_PLAN.md before acting on older
“not implemented” statements.

---

## 0. Read this first

CalibRead is a six-month thesis project intended to produce an ICLR-quality
research paper about the reliability of **parametric reads from language
models**. The central empirical object is not ordinary benchmark accuracy. It
is the probability that a model commits to an operationally incorrect answer
as controlled properties of the requested knowledge/read become more complex.

The repository already contains:

- the original P03 proposal;
- a finalized research crosswalk that corrects/refines the proposal;
- 70,000 deterministic synthetic testcase specifications across R0–R7;
- a corpus materializer for controlled parametric injection;
- an OpenRouter-compatible inference/collection package;
- a separate standard-library-only analysis package;
- executable H1–H5 analyses;
- CPR candidate-set construction;
- research plans, SOPs, bibliography, paper-writing instructions, and output
  templates;
- a detailed final consistency audit and repair plan.

The testcase corpus and repaired offline pipeline are structurally valid, but
the repository is **not ready for confirmatory execution**. The former
code/method blockers have been repaired. The remaining blockers are the absent
immutable Git revision, incomplete human testcase/output audits, and real
checkpoint/development execution gates. Section 23 is the current status.

Before changing code, read:

1. `FINAL_CONSISTENCY_ISSUES_AND_REPAIR_PLAN.md`;
2. `calibread_research/plans/00_p03_to_final_crosswalk.md`;
3. `calibread_research/plans/02_hypothesis_execution_plan.md`;
4. `calibread_research/operating_protocols/01_TEST_EXECUTION_STANDARD_OPERATING_PROTOCOL.md`;
5. `calibread_research/operating_protocols/02_ANALYSIS_STANDARD_OPERATING_PROTOCOL.md`;
6. the runner and analytics READMEs;
7. the source modules affected by the chosen repair.

Do **not** run the locked test, paste credentials into tracked files, hand-edit
generated JSONL, or describe public-model/contextual results as confirmatory
parametric evidence.

---

## 1. Project identity

### 1.1 Working title

**CalibRead: Parametric Complexity Analysis of Probabilistic Read Reliability in
LLM Knowledge Systems**

Proposal theme:

> P03 · Theme B — Parametric CRUD  
> Calibration · Hallucination · Conformal Prediction

The source proposal is `Proposal (2).html` at the workspace root.

### 1.2 Core systems framing

Treat a language model containing injected or learned facts as a **parametric
database**. A Read request should not merely return answer text `y`; the system
should also expose calibrated reliability information and, where possible, a
formal decision or set-level guarantee.

The project studies a model `theta` and query population `Q` under controlled
complexity factors. The primary risk is:

```text
L_fc = 1{the system commits and the committed response is not operationally correct}

H(theta, Q) = E[L_fc]
              = false commits / incoming queries
```

`H` is the **hallucination/false-commit index**, not the bibliometric h-index.
The code exports selective risk separately:

```text
H_selective = false commits / committed answers
```

### 1.3 Core thesis claim

Hallucination/false-commit risk is not a single intrinsic scalar property of a
model. It is a structured function of independently controlled Read complexity
dimensions, model/checkpoint state, confidence mechanism, and operating policy.

CalibRead therefore produces **reliability curves and surfaces**, not just one
accuracy or hallucination number.

### 1.4 Contributions intended by the current design

1. A deterministic controlled benchmark for parametric Read behavior.
2. A complexity-indexed reliability surface over R1–R6, with R0 controls and R7
   policy stress.
3. A separation between factual correctness, action correctness, operational
   commit correctness, answer coverage, and false-commit risk.
4. Risk-controlled global and complexity-conditioned Read policies.
5. Conformal Parametric Read (CPR): a frozen sampled-candidate nested prediction
   set with marginal conformal coverage and an explicit vacuous fallback.
6. Reproducible inference, nondeterminism, cost, latency, and provider metadata
   auditing.

### 1.5 Important novelty boundary

The project should **not** claim to be the first conformal method for LLM
generation. The final crosswalk deliberately frames the contribution as the
controlled parametric benchmark, conditional-reliability characterization, and
contract layer.

---

## 2. Source-of-truth hierarchy

Conflicts must be resolved in this order unless a later signed preregistration
explicitly supersedes it:

1. **Current signed/frozen preregistration** — once completed.
2. `calibread_research/plans/00_p03_to_final_crosswalk.md` — authoritative
   mapping from original P03 ideas to the executable final design.
3. `calibread_research/plans/02_hypothesis_execution_plan.md` — authoritative
   H1–H5 populations, groups, endpoints, margins, and outputs.
4. `calibread_research/plans/09_frozen_secondary_scope_decisions.md` —
   protocol-v1.2 decisions that demote R02–R05 optional features.
5. `calibread_research/plans/07_preregistration_template.md` — fields that must
   be finalized before test release.
6. `calibread_research/plans/08_unified_training_and_checkpoint_plan.md` —
   checkpoint/corpus logic.
7. The two SOPs — operational execution and analysis order.
8. Executable code — what the repository currently does.
9. `FINAL_CONSISTENCY_ISSUES_AND_REPAIR_PLAN.md` — known divergences between
   intended method and current code, plus required repair acceptance tests.
10. Remaining plans/dimension protocols — detailed supporting design.
11. Original proposal — motivation and original ideas, but not authoritative
    where the final crosswalk says a hypothesis was replaced or refined.

Do not “repair” the implementation by returning it to superseded proposal
claims. Repair it toward the final crosswalk and preregistration.

---

## 3. Repository map

### 3.1 Workspace root

| Path | Purpose |
|---|---|
| `Proposal (2).html` | Original P03 proposal. |
| `CalibRead_research_blueprint.md` | Large methodology/research blueprint. |
| `CALIBREAD_CODE_PACKAGES.md` | Package overview and usage context. |
| `FINAL_CONSISTENCY_ISSUES_AND_REPAIR_PLAN.md` | Current blocker list and exact repair plan. |
| `AGENT_FULL_THESIS_AND_CODEBASE_CONTEXT.md` | This handoff document. |

### 3.2 `calibread_research/`

Research design, testcase data, corpus construction, references, and SOPs.

Important subtrees:

```text
calibread_research/
  README.md
  plans/
    00_master_execution_index.md
    00_p03_to_final_crosswalk.md
    01_sample_size_and_power_plan.md
    02_hypothesis_execution_plan.md
    03_results_collection_and_analysis_plan.md
    04_week_by_week_26_week_plan.md
    05_complete_research_paper_plan.md
    06_operational_runbook_and_data_dictionary.md
    07_preregistration_template.md
    08_unified_training_and_checkpoint_plan.md
    dimensions/R0...R7 protocols
  operating_protocols/
    01_TEST_EXECUTION_STANDARD_OPERATING_PROTOCOL.md
    02_ANALYSIS_STANDARD_OPERATING_PROTOCOL.md
    03_ICLR_PAPER_WRITING_AGENT_PROMPT.md
    04_TESTING_CODE_LOGIC_AND_H_INTERPRETATION.md
  references/
    ANNOTATED_BIBLIOGRAPHY.md
    calibread_references.bib
  prompts/
    read_system.txt
    p_true_system.txt
    p_true_user_template.txt
  scripts/
    generate_testcases.py
    validate_testcases.py
    create_human_audit_sample.py
    materialize_training_corpus.py
    test_materialize_training_corpus.py
  testcases/
    r0_baseline_controls.jsonl
    r1_exposure_frequency.jsonl
    ... r7_threshold_policy.jsonl
    testcase.schema.json
    manifest.json
    human_audit_sample.csv
  results/
    templates/
    manifests/
    logs/
  configs/run_manifest.template.json
```

### 3.3 `calibread_openrouter/`

Inference, caching, deterministic grading, confidence features, candidate
construction, and CSV export.

```text
calibread_openrouter/
  README.md
  pyproject.toml
  config.example.json
  config.parametric_t2.example.json
  config.parametric_t0_temporal.example.json
  checkpoint_manifest.example.json
  src/calibread_openrouter/
    cli.py
    client.py
    config.py
    grading.py
    io.py
    parsing.py
    prompting.py
    runner.py
    tasks.py
    uncertainty.py
  tests/test_runner.py
```

### 3.4 `calibread_analytics/`

Offline paper analysis. It deliberately uses only Python’s standard library and
generates native SVG figures.

```text
calibread_analytics/
  README.md
  pyproject.toml
  analysis_config.example.json
  analysis_config.parametric.example.json
  src/calibread_analytics/
    analysis.py
    cli.py
    cpr.py
    data.py
    diagnostics.py
    hypotheses.py
    metrics.py
    plots.py
    policy.py
    report.py
    stats.py
  tests/test_analytics.py
```

---

## 4. Final operational definitions

### 4.1 Response actions

The base Read JSON contract contains:

```text
ANSWER          -> commit
ABSTAIN         -> non-commit
CLARIFY         -> non-commit, request disambiguation
REJECT_PREMISE  -> non-commit, reject false premise
```

A schema-valid response contains action, answer, and clarification fields with
conditional null/non-null requirements.

### 4.2 Correctness fields

The runner distinguishes:

- `factual_correct`: answer content matches the testcase grader;
- `action_correct`: schema-valid action equals expected action;
- `commit_correct`: schema-valid `ANSWER`, factually correct, and operationally
  unique under the query contract;
- `answer_attempted`: an answer/commit was attempted, including answer-payload
  smuggling under the intended strict policy;
- `false_commit_loss`: answer attempted but `commit_correct=0`;
- `stale_answer`: answer matches a known superseded value.

For R4 ambiguity 2–4, one plausible office-specific answer is not an
operationally correct singleton response. The correct first action is
`CLARIFY`.

### 4.3 Primary contract

Current frozen design values:

```text
target false-commit risk r*       = 0.05
calibration confidence 1-delta    = 0.95
primary utility                   = answer coverage
primary population                = equal weight R1-R6,
                                    equal level weight inside each suite
R7                                = secondary policy stress
```

### 4.4 What `c` may and may not mean

The original motivation asks for `(y,c)` where confidence bounds factual error.
The executable design separates three objects:

1. `raw_confidence_score`: an uncalibrated ordering score.
2. `c_point_estimate`: isotonic estimate of correctness fitted on development
   data; descriptive, not a formal individual bound.
3. `c_policy_error_upper`: formal upper bound for the selected policy over the
   declared query mixture; not an individual posterior probability.

Never write that an individual answer has “95% probability of being correct”
because the policy certificate is 95% confident. CPR gives marginal set
coverage under exchangeability for the frozen candidate mechanism, not a
posterior truth probability.

---

## 5. Testcase corpus

### 5.1 Global counts

```text
total records                 70,000
unique worlds                 36,000
fit                           28,000 (40%)
tune                          10,500 (15%)
calibrate                     14,000 (20%)
sealed test                   17,500 (25%)
generator seed                20260722
```

All rows derived from one world remain in the same split. Do not reshuffle
individual rows.

### 5.2 Per-suite summary

| Suite | Records | Worlds | Levels | Role |
|---|---:|---:|---|---|
| R0 | 8,000 | 2,000 | 4 | baseline, negative, infrastructure and checkpoint gates |
| R1 | 7,000 | 7,000 | 7 | exact parametric exposure frequency |
| R2 | 16,000 | 2,000 | 8 | precision and formatting demand |
| R3 | 8,000 | 8,000 | 4 | storage availability, update, staleness |
| R4 | 8,000 | 2,000 | 4 | number of valid interpretations |
| R5 | 10,000 | 2,000 | 5 | synthesis/path depth |
| R6 | 8,000 | 8,000 | 4 | controlled domain transfer |
| R7 | 5,000 | 5,000 | 5 | threshold/policy stress profiles |

### 5.3 Common record structure

Each JSONL record is an experimental specification, not model output. It
contains at least:

- `testcase_id`, `world_id`, `dimension_id`, `dimension_name`;
- `level`, `split`, `query`;
- `expected_action`, `answer_type`, `valid_answers`;
- controlled `factors`;
- ground-truth `knowledge` facts;
- deterministic `grading` rule;
- `injection_spec` for training-corpus construction;
- dimension-specific `metadata`.

### 5.4 R0 — baseline and negative controls

Four queries are derived from each of 2,000 control worlds:

| Level | Expected action | Purpose |
|---|---|---|
| `known_direct` | ANSWER | direct stored-fact retrieval |
| `known_paraphrase` | ANSWER | paraphrase robustness |
| `unknown_entity` | ABSTAIN | unknown-fact control |
| `false_premise` | REJECT_PREMISE | premise rejection |

R0 is required for checkpoint acceptance but is not part of the R1–R6 primary
complexity mixture. The current runner does not yet support R0; this is a known
repair item.

### 5.5 R1 — exact exposure frequency

Seven levels, 1,000 independent facts each:

```text
exposure = 0, 1, 2, 4, 8, 16, 32
```

Exposure-zero expects ABSTAIN; positive exposures expect ANSWER. Exposure is an
exact controlled injection count, not estimated web frequency. Fact-to-exposure
assignment is deterministically randomized and fixed across models/seeds.

### 5.6 R2 — precision

Each of 2,000 worlds yields eight demands:

```text
categorical
year
month_year
exact_date
integer
decimal_1
decimal_3
decimal_5
```

All expect ANSWER. Numeric graders use frozen decimal-place tolerances; date
graders enforce the requested component or exact date. These eight rows are
dependent within world and must remain clustered in inference statistics.

### 5.7 R3 — temporal availability and supersession

2,000 independent worlds per status:

| Level | Training availability | Expected action |
|---|---|---|
| `stable_pre_cutoff` | old/current value inserted at T0 | ANSWER |
| `superseded_stale` | old value inserted, new valid value withheld | ABSTAIN |
| `current_after_update` | old at T0, controlled update at T2 | ANSWER at T2 checkpoint |
| `post_cutoff_unknown` | valid value never inserted | ABSTAIN |

R3 measures controlled storage/update availability, not passive calendar-time
memory decay. Stale answers are separately labelled.

### 5.8 R4 — ambiguity

Each of 2,000 people/worlds has four office-specific identities/roles and yields
queries with 1–4 valid interpretations:

```text
interpretations_1 -> ANSWER
interpretations_2 -> CLARIFY
interpretations_3 -> CLARIFY
interpretations_4 -> CLARIFY
```

Metadata provides a frozen clarification question and simulated choices. The
runner can evaluate forced second-turn recovery. That must not be confused with
end-to-end interactive success unless the first turn actually emitted a valid
CLARIFY.

### 5.9 R5 — synthesis depth

Each of 2,000 graphs yields depths/hops 1–5. Answers are matched synthetic
`Designation` entities to reduce answer-morphology confounding. Metadata
contains required component queries and supporting facts.

Across all R5 worlds:

```text
final rows                     10,000
deduplicated component tasks  18,000
parent-to-component links     30,000
```

H2 conditions on all required component probes being correct for each depth
2–5 final query. The multiplicative independence product is a separate
cross-fitted all-graphs diagnostic; it must not be applied after conditioning
on observed component success.

### 5.10 R6 — domain shift

Four parallel synthetic domains with 2,000 independent worlds each:

```text
general
biomedical
legal
technical
```

Relation, answer morphology, exposure, and query template are controlled across
domains. H5 uses four frozen calibration-transfer directions. Planned secondary
continuous features—embedding distance, domain classifier log odds, prompt
perplexity, template novelty, answer-token rarity—are not yet implemented.

### 5.11 R7 — policy stress

Five unique-query profiles, 1,000 each:

```text
easy_known
low_frequency
high_precision
stale_unknown
multihop
```

Thresholds are applied post hoc on the same scored queries. The 101 threshold
points are not 101 independent testcase sets. R7 is secondary stress testing,
not the seventh primary complexity factor.

### 5.12 CPR eligible controlled test population

The current operationally unique R1–R6 test population contains 12,750 final
targets:

```text
R1  1,750
R2  4,000
R3  2,000
R4    500  (interpretations_1 only)
R5  2,500
R6  2,000
```

R4 ambiguity 2–4 are excluded from singleton-answer CPR evaluation.

### 5.13 Frozen H3/H4 hard groups

The 13 groups are:

```text
r1_low_exposure           exposure 0, 1, or 2
r2_exact_date
r2_decimal_5
r3_superseded_stale
r3_post_cutoff_unknown
r4_interpretations_3
r4_interpretations_4
r5_hops_4
r5_hops_5
r6_general
r6_biomedical
r6_legal
r6_technical
```

The pooled R1 group has 600 calibration and 750 test units. Each other group
has 400 calibration and 500 test units. R7 profiles and interaction groups are
not confirmatory hard groups.

### 5.14 Corpus integrity already verified

The current audit established:

- all 70,000 rows pass the custom validator;
- manifest hashes match;
- testcase IDs are unique;
- exact query strings are unique;
- no direct answer text leakage was detected in queries;
- subject/relation keys do not leak across splits;
- generated synthetic facts do not conflict across worlds/suites;
- deterministic regeneration is byte-identical;
- all world-level paired rows stay within one split.

The `human_audit_sample.csv` contains 200 development-side cases, but its review
fields are blank. Human semantic acceptance has not yet passed.

---

## 6. Parametric training and checkpoint design

### 6.1 Why public OpenRouter results are not confirmatory

The controlled facts are synthetic. A normal public model has never been
trained on the unified CalibRead injection corpus. Therefore:

- `closed_book_external`: useful public zero-shot baseline, nonconfirmatory;
- `contextual_debug`: facts placed in context, pipeline debugging only;
- `parametric_checkpoint`: the only confirmatory mode, requiring a genuinely
  trained/updated checkpoint and manifest attestation.

Do not use contextual retrieval as evidence about parametric memory.

### 6.2 Unified initial corpus

The initial corpus combines deduplicated positive-exposure injection programs
from R0–R7 and the T0 portions of R3 schedules. Exposure-zero and deliberately
withheld current facts produce no training documents.

The fit/tune/calibrate/test label is a downstream evaluation/policy split. It is
not a rule for withholding positive-exposure knowledge from training. Positive
facts from every evaluation partition must be injected as specified; otherwise
the test would measure accidental omission rather than Read reliability.

### 6.3 Two checkpoint stages

#### T0

1. Materialize all non-temporal facts and only T0 temporal steps.
2. Tokenize/order under frozen rules.
3. Train to the frozen budget.
4. Save `checkpoint_t0`.
5. Run only the preregistered pre-update temporal probes and checkpoint gates.

#### T2

1. Materialize non-T0 R3 update steps.
2. Continue from T0 under frozen optimizer/reset semantics.
3. Save `checkpoint_t2`.
4. Run final R0 gates and the main R1–R6 evaluation; run R7 separately as
   secondary policy stress.
5. Compare T0/T2 for the paired R3 update diagnostic.

### 6.4 Primary and secondary inference sources

Primary configuration:

```text
analysis_role       primary
checkpoint_stage    checkpoint_t2
suites              R1-R7 in current runner; main statistical mixture R1-R6
levels              all
```

Secondary temporal configuration:

```text
analysis_role       secondary_temporal
checkpoint_stage    checkpoint_t0
suite               R3
level               current_after_update
```

Both endpoints for one trained model/seed should share a paper-facing
`model.analysis_id`, while preserving real endpoint slugs, checkpoint hashes,
and stages in provenance.

### 6.5 Materializer behavior

`materialize_training_corpus.py`:

- consumes `injection_spec`, not evaluation queries;
- cycles templates to exact exposure counts;
- handles per-fact exposure for multi-fact worlds;
- separates T0 from temporal update steps;
- deduplicates shared world programs across repeated input files;
- emits deterministic ordering/shuffle metadata.

It does **not** currently guarantee tokenizer-aware filler/token equality or
fully enforce final shuffled trainer order. That must be handled and hashed in a
verified downstream preparation step or implemented directly.

### 6.6 Checkpoint acceptance

Before a checkpoint enters analysis:

- token/step budget completed;
- loss is not corrupted;
- reload probe matches under declared backend;
- development R0 known-direct/paraphrase gates pass;
- general sanity degradation remains within preregistered margin;
- corpus, order, optimizer, checkpoint, environment, and code hashes exist;
- repeatability behavior is measured and reported.

The current runner cannot yet execute R0; fix this before checkpoint acceptance.

---

## 7. OpenRouter runner architecture

### 7.1 CLI

Entry point: `calibread-openrouter`.

Commands:

```text
validate   validate configuration; optional online model-capability query
models     search/list current OpenRouter model metadata
estimate   count observations and requests without API calls
run        run or resume generation, then grade
grade      rebuild derived results from cached raw outputs
```

Selection overrides support suite, split, and exact level. Current CLI suite
choices are R1–R7, which is a known R0 gap.

### 7.2 Module responsibilities

| Module | Responsibility |
|---|---|
| `config.py` | load/resolve/validate config; scientific status; selected suites/splits/levels |
| `client.py` | OpenRouter HTTP calls, retry/rate control, model listing, response metadata |
| `prompting.py` | JSON schemas, prompt loading, Read/P(True) message construction |
| `parsing.py` | Read and P(True) parsing |
| `grading.py` | exact/alias/date/numeric/action/ambiguity/stale grading |
| `tasks.py` | final, R5 component, and R4 clarification task construction |
| `uncertainty.py` | agreement, entropy, NLL/probability, P(True), candidate extraction |
| `io.py` | CSV/JSONL schemas, append and atomic materialization helpers |
| `runner.py` | orchestration, resume, generation, grading, output materialization |
| `cli.py` | command dispatch and errors |

### 7.3 Task types

1. **Final tasks:** one per selected R1–R7 testcase.
2. **R5 component tasks:** deduplicated per world/query; used for H2.
3. **R4 clarification tasks:** one forced second-turn task per frozen simulated
   choice for ambiguous cases.

Observation IDs distinguish final/component/clarification tasks. Parent and
component links are persisted for H2 joins.

### 7.4 Sampling plan

Current examples use:

```text
greedy samples per observation          1
stochastic samples per final            5
stochastic samples per component        0 by default
temperature greedy                      0.0
temperature stochastic                  0.7
top_p                                   0.95
max completion tokens                   64
repeatability repeats                   2
repeatability selected per suite        50
```

Repeatability requests reuse the same deterministic seed and are excluded from
uncertainty sampling. They measure exact and parsed-output nondeterminism.

### 7.5 Full request volume under current defaults

All R1–R7 splits, R5 components enabled, R4 second turns enabled, five
stochastic final samples, two repeats for 50 cases per suite, P(True) disabled:

```text
final observations                62,000
component observations            18,000
clarification observations        18,000
final generation calls           372,000  (62,000 * 6)
component calls                    18,000
clarification calls                18,000
generation subtotal              408,000
repeatability calls                  700
total                            408,700
```

If P(True) is enabled for final, component, and clarification observations, the
current estimator adds 98,000 P(True) calls, producing 506,700 total. Always
pilot and use real usage/cost data before a full run.

The current `estimate` implementation crashes when component tasks are present;
see the repair plan H01.

### 7.6 Prompt contract

The Read prompt demands structured JSON with one of the four actions. The
provider may be asked to enforce JSON Schema. Parsing and deterministic grading
still operate locally because provider enforcement is not universally stable.

The current parser is less strict than documented: it extracts the first JSON
object from prose and does not reject extra keys. Fix M02/M05 before frozen
collection.

### 7.7 Deterministic grading

Graders include:

- canonical normalized exact/alias matching;
- date component and exact date;
- rounded numeric tolerance and absolute error;
- temporal stale-answer detection;
- operational ambiguity/action handling;
- path/depth metadata for R5.

The grader uses the greedy sample for primary response grading. Stochastic
samples supply confidence/candidate features rather than independent primary
test rows.

### 7.8 Confidence features

Currently implemented:

- exact normalized-answer agreement with the greedy answer;
- exact normalized-answer entropy;
- answer-token mean/total NLL when token alignment is available;
- answer-token minimum probability;
- full-response NLL fields;
- P(True), optionally via a separate request;
- configured `confidence_score` and `confidence_method`.

Important limitations:

- exact answer entropy is not semantic entropy;
- verbal confidence and learned correctness scorer are not fully implemented;
- missing P(True)/token score silently falls back per row to exact agreement;
  this must be removed or separated before primary analysis;
- P(True) raw provenance currently records the main generation top-p/token cap
  rather than its actual 1.0/24 request settings.

### 7.9 Candidate sets

Stochastic ANSWER strings are normalized and grouped. Candidates are ranked by
frequency, with deterministic normalized-text tie-breaking. Candidate CSV rows
include rank, mass, sample count, greedy membership, and correctness.

Current candidate extraction does not require `parser_status=ok`; this must be
fixed before CPR claims.

### 7.10 Runner outputs

Each run directory should contain:

```text
raw_generations.csv
scored_results.csv
candidate_sets.csv
component_links.csv
run_summary.csv
observation_specs.jsonl
resolved_config.redacted.json
model_metadata.json
by_suite/R1 ... by_suite/R7
```

Raw rows include exact returned model/provider, request ID, system fingerprint
when available, seed, sampling parameters, prompt/message hashes, messages, raw
text, logprobs, tokens, cost, latency, errors, and config hash.

### 7.11 Scientific-mode status

Runner rows contain `scientific_status`:

```text
parametric checkpoint + attestation -> confirmatory_parametric
parametric without attestation       -> invalid_missing_attestation
contextual debug                     -> contextual_pipeline_debug_nonparametric
public closed-book                   -> external_zero_shot_nonconfirmatory
```

### 7.12 Resume design and known critical flaw

The intended behavior is append-only/resume-safe. Successful request keys are
skipped, failed requests remain and are retried. Observation specs and links can
merge across separate split commands.

The actual config/resume identity does not hash prompt contents, testcase
contents, testcase manifest, checkpoint-manifest contents, or grader/source
identity. A changed file at the same path can silently reuse old requests. Fix
C03 by introducing a content-addressed scientific bundle before using resume.

### 7.13 Model/provider stability

For frozen runs:

- pin a provider route;
- keep fallbacks disabled;
- require supported seeds/logprobs/structured outputs as configured;
- archive model/provider capabilities and pricing;
- compare every returned model/provider to frozen expectations;
- reject drift instead of merely logging it.

No real API key is stored in this repository. Do not add one.

---

## 8. Analytics architecture

### 8.1 Package purpose

`calibread_analytics` consumes runner CSVs and produces:

- the R1–R7 H surface;
- calibration/reliability/confidence-quality analysis;
- risk-coverage curves;
- H1–H5 tests with Holm correction;
- global and CCRC policy contracts;
- CPR calibration/evaluation;
- calibrated Read-pair exports;
- R3 paired checkpoint diagnostics;
- errors, cost, latency, and repeatability diagnostics;
- native SVG figures and CSV/LaTeX paper tables.

It does not make API calls.

### 8.2 Module responsibilities

| Module | Responsibility |
|---|---|
| `data.py` | analysis config, CSV loading/normalization, writes, file hashes |
| `stats.py` | exact intervals, bootstrap, PAVA, Holm, test primitives |
| `metrics.py` | H, risk coverage, reliability, aggregate metrics |
| `policy.py` | hard groups, profiles, thresholds, risk intervals, CCRC penalties |
| `cpr.py` | isotonic Read pairs, conformal rank cutoff, CPR test sets |
| `hypotheses.py` | H1–H5 execution and hypothesis outputs |
| `diagnostics.py` | errors, temporal pairing, auxiliary metrics, cost/repeatability |
| `plots.py` | SVG figures |
| `report.py` | Markdown/LaTeX reports and claim notes |
| `analysis.py` | end-to-end orchestration and output manifest |
| `cli.py` | `calibread-analyze --config ...` |

### 8.3 Primary versus secondary rows

Intended primary rows:

```text
analysis_role      primary
checkpoint_stage   checkpoint_t2
```

Intended secondary rows:

```text
analysis_role      secondary_temporal
checkpoint_stage   checkpoint_t0
dimension          R3
level              current_after_update
```

The code currently filters primary by role but does not enforce T2 stage or the
full artifact/count/hash contract. This is critical issue C02.

### 8.4 H surface

For every model, dimension, and test level:

```text
H_false_commit
world-cluster bootstrap interval
H_selective
factual wrong commits per incoming query
answer coverage
factual accuracy
query/world counts
controlled factor and value
```

One complete model has 37 R1–R7 level cells:

```text
R1 7 + R2 8 + R3 4 + R4 4 + R5 5 + R6 4 + R7 5 = 37
```

### 8.5 Confidence analysis

The package constructs:

- threshold risk-coverage curves;
- fixed-bin reliability tables;
- calibration summary/ECE-style outputs;
- confidence ranking quality/AURC-style outputs;
- an isotonic point calibrator fitted on fit/tune;
- selected Read pairs with raw score, point estimate, and policy bound.

Fit/tune learns descriptive/profile mappings. Calibrate chooses thresholds and
formal cutoffs. Test is for the one-shot frozen evaluation.

### 8.6 Global mixture and hard groups

Primary mixture:

1. each R1–R6 suite receives equal total weight;
2. each level within its suite receives equal weight;
3. rows within a level share that cell’s weight.

Current code applies a weighted Hoeffding interval to rows. This is invalid for
the repeated-world dependence in R2/R4/R5. Implement C01’s independent-world
cluster bound before treating any aggregate UCB as formal.

### 8.7 Threshold selection

The configured threshold grid is normally 0.00–1.00 in 0.01 increments. A
candidate threshold is certified only if every required group’s simultaneous
upper bound is at or below 0.05 and the group has sufficient sample size. Among
passing candidates, the code selects maximum aggregate answer coverage, with a
threshold tie-break.

If no threshold passes, the policy is `UNSUPPORTED`; do not substitute the
least-bad threshold.

### 8.8 Query-only inference profiles for H4

Current profile classes:

```text
ordinary
ambiguity
temporal
precision
multihop
domain_specialist
```

Rules inspect query text only. Fit/tune estimates smoothed profile loss
penalties; calibrate selects global and adjusted thresholds; test compares
coverage after both pass the same aggregate-plus-13-group gate.

Known defect: the current rule recognizes `five decimal` but R2 says
`Round to 5 decimal places`, so every R2 `decimal_5` case is classified
`ordinary`. Fix H04 and freeze the assignment audit before test.

The week plan also describes trained profile classifiers and a ground-truth
oracle. Those are not implemented. Decide whether deterministic query rules are
the final primary method and revise the plan, or implement the classifiers
before freeze. Ground-truth profiles may only be an oracle diagnostic.

### 8.9 CPR

Current CPR mechanism:

1. group normalized sampled answers for operationally unique R1–R6 targets;
2. identify the first rank containing a correct answer;
3. assign a missing rank when no sampled candidate is correct;
4. on calibrate, choose conformal order
   `ceil((n+1)(1-alpha))`;
5. return the top-k candidate set on test;
6. if the cutoff reaches the missing/universal member, return a vacuous
   all-answers marker and operationally ABSTAIN.

Exports include empirical coverage, exact coverage interval, fallback rate, and
mean nonvacuous set size. The guarantee is marginal under exchangeability and
only for the frozen candidate-generation mechanism.

Known CPR blockers:

- grouping uses only `observation_id`, so same-ID separate runs can merge;
- missing-rank support is inferred from observed calibration answer counts,
  rather than a frozen candidate draw budget;
- parser-invalid candidate ANSWERs can enter;
- reporting needs candidate recall, subgroup coverage, fuller set-size
  distribution, and singleton rate.

### 8.10 Output tree

Expected paper assets include:

```text
paper_assets/<analysis>/
  H_INDEX_AND_CONFIDENCE.md
  PAPER_ASSET_REPORT.md
  analysis_manifest.json
  figures/
    fig_h_complexity.svg
    fig_risk_coverage.svg
    fig_calibration.svg
    fig_hard_groups.svg
    fig_domain_transfer.svg
    fig_cpr.svg
    fig_hypotheses.svg
    fig_error_taxonomy.svg
    fig_r3_update_effect.svg
  tables/
    hallucination_index.csv
    aggregate_metrics.csv
    risk_coverage.csv
    reliability_bins.csv
    calibration_summary.csv
    confidence_quality.csv
    auxiliary_observation_metrics.csv
    error_taxonomy.csv
    cost_and_latency.csv
    repeatability_audit.csv
    profile_assignment_audit.csv
    r3_temporal_confusion.csv
    r3_paired_update_effect.csv
    hypothesis_results.csv
    h3_contracts.csv
    h4_contracts.csv
    h5_domain_directions.csv
    cpr_summary.csv
    cpr_test_sets.csv
    calibrated_read_pairs.csv
    policy_diagnostics.json
    LaTeX tables
  suites/R1 ... suites/R7/
```

Current analysis manifests hash generated assets but not all source artifacts,
and output directories can retain stale files. Fix H09.

---

## 9. Final confirmatory hypotheses

### 9.1 Multiplicity rule

Each H1–H5 contributes exactly one primary p-value/decision statistic to a
five-way Holm family. Within-H3 and within-H5 multiplicity is handled before
Holm through frozen simultaneous/max-direction logic. Depth-specific H2 and
other model/interaction analyses are secondary.

Current code has a bug that converts a legitimate raw `p=0.0` to 1.0 before
Holm. Fix H02.

### 9.2 H1 — exposure-frequency reliability

**Claim:** operational accuracy improves monotonically with exact controlled
exposure.

**Data:** R1 test final rows for the preregistered primary model.

**Executable primary test:**

- outcome: `commit_correct`;
- exposure levels: 0,1,2,4,8,16,32;
- one-sided isotonic Bernoulli likelihood-ratio statistic;
- exposure labels permuted at fact-cluster level;
- practical contrast: accuracy at exposure 16 minus exposure 1;
- support requires raw H1 test plus lower one-sided 95% bootstrap bound above
  5 percentage points.

Other models, model-size interactions, and change points are secondary.

### 9.3 H2 — synthesis failure despite component availability

**Claim:** among depth 2–5 graph queries whose complete required component set
is answered correctly, final composition error remains above 5%.

**Data:** R5 test final rows joined to deduplicated component probes through
`component_links.csv`.

**Executable primary test:**

- require every linked component `commit_correct=1`;
- outcome `1-final commit_correct`;
- pool depths 2–5;
- graph/world-cluster one-sided test and bootstrap;
- practical floor 5%.

Secondary diagnostic: on all graphs, compare observed final success to the
product of cross-fitted component success probabilities. Do not use that
product inside the conditioned primary subset.

### 9.4 H3 — aggregate validity hides hard-group failure

**Claim:** a global policy calibrated only for the aggregate mixture can pass
the aggregate 5% risk contract while at least one frozen hard group exceeds
7%—the target plus a 2-point practical margin.

**Procedure:**

1. On calibrate R1–R6, choose an aggregate-only certified threshold.
2. On test, require aggregate upper bound <=0.05.
3. Evaluate the 13 hard groups with simultaneous inference.
4. Require the simultaneous lower bound for the worst group to exceed 0.07.
5. Emit one H3 family p-value.

This aggregate-only policy is diagnostic and is not H4’s joint-safe global
baseline.

The aggregate gate is currently not formally valid because of C01.

### 9.5 H4 — deployable complexity conditioning improves utility

**Claim:** among policies passing the same joint aggregate-plus-13-group 5%
contract, predicted-profile CCRC retains at least 3 percentage points more
answers than one global joint-safe threshold.

**Procedure:**

1. Learn profile penalties on fit/tune only.
2. On calibrate, independently choose a global threshold and a profile-adjusted
   threshold, each required to pass all 14 scopes.
3. If either is unsupported, report H4 unsupported.
4. On test, compare answer-coverage decisions on the same R1–R6 rows/worlds.
5. Use a one-sided paired world-cluster comparison against 0.03.

Current `_mixture_bootstrap()` resamples worlds independently inside level
cells, breaking R2/R4/R5 cross-level pairing. Fix H03.

### 9.6 H5 — asymmetric cross-domain calibration transfer

**Claim:** at least one frozen source-to-target calibration direction has a
cross-minus-within target-domain false-commit gap exceeding 2 points.

Directions:

```text
general -> biomedical
general -> legal
biomedical -> general
legal -> technical
```

For source `s` and target `t`:

```text
D_s,t = R_fc(policy calibrated on s, evaluated on t)
        - R_fc(policy calibrated on t, evaluated on t)
```

The code calibrates one threshold per R6 source domain, applies source and
within-domain thresholds to the same target test rows, calculates paired loss
differences, and uses a Bonferroni/max-direction result before five-way Holm.

Embedding/perplexity regression is supportive secondary analysis and does not
determine H5.

### 9.7 Interpretation if hypotheses vary

The design explicitly allows a valuable measurement paper even if the method
does not win:

- H1–H3 supported, H4 weak: strong benchmark/measurement paper;
- H3–H4 supported: benchmark plus method paper;
- unsupported policies: report infeasibility, never tune on test or substitute a
  least-bad threshold;
- null/negative hypotheses remain publishable if execution and uncertainty are
  rigorous.

---

## 10. Known issues and required repairs

The authoritative detailed repair document is
`FINAL_CONSISTENCY_ISSUES_AND_REPAIR_PLAN.md`. It contains severity, exact
repair, and acceptance tests for every issue. The summary below exists so a new
agent cannot miss the state of the repository.

### 10.1 Critical blockers

| ID | Issue | Consequence |
|---|---|---|
| C01 | row-level weighted Hoeffding ignores dependent rows in repeated worlds | advertised aggregate finite-sample risk guarantee is not justified |
| C02 | analytics accepts incomplete/duplicated/mixed-stage/malformed sources | invalid data can become confirmatory outputs |
| C03 | resume identity hashes paths/config but not every scientific file’s contents | prompt/testcase/checkpoint changes can silently reuse old responses |
| C04 | all project content is currently untracked in Git | no immutable source revision or reproducible run manifest |

Recommended C01 method: retain row mixture weights, aggregate them within
independent `(run_id,world_id)` clusters, and apply weighted Hoeffding using
cluster ranges/weights. Exact binomial is permitted only after verifying one
equal-weight Bernoulli per independent cluster.

### 10.2 High-priority defects

| ID | Issue |
|---|---|
| H01 | request estimator crashes on R5 component tasks because it sums `None` repeatability flags |
| H02 | raw `p=0.0` becomes 1.0 before Holm correction |
| H03 | H4 bootstrap does not preserve cross-level world pairing |
| H04 | `decimal_5` query profile is misclassified as ordinary |
| H05 | CPR groups only by observation ID and can merge separate runs |
| H06 | confidence methods silently mix through per-row fallback |
| H07 | CPR family support/missing rank is inferred from calibration data rather than frozen draw budget |
| H08 | returned provider/model drift is recorded but not rejected |
| H09 | analysis output reuse can retain stale assets and manifest omits source hashes |

### 10.3 Medium correctness/provenance issues

- P(True) request top-p/token cap is logged incorrectly.
- Parser accepts first JSON object inside prose and extra fields.
- Invalid non-string answer can lose evidence of answer smuggling.
- Candidate extraction does not require `parser_status=ok`.
- Config does not fully enforce role/stage/suite relationships.
- Forced R4 clarification recovery is not actual interactive success.
- CPR output needs richer candidate/set/subgroup diagnostics.
- One hypothesis plot mixes effects with different scales.
- Repeatability metric name does not reveal that it means “all repeats match.”

### 10.4 Roadmap gaps

- no executable R0 runner/gate;
- R6 continuous shift features/transfer recovery analyses absent;
- semantic entropy absent—current field is exact string-answer entropy;
- distinct verbal confidence and learned correctness scorer incomplete;
- trained query profiler and ground-truth oracle diagnostic absent;
- 200-case human testcase audit blank;
- planned 300-output grader audit not represented;
- legacy CSV/run-manifest templates drift from executable schemas;
- materializer does not itself freeze final token-aware training order;
- validator is custom rather than full JSON Schema execution.

### 10.5 Non-blocking qualifications that must be stated correctly

- CPR universal fallback is valid but vacuous; deployed action is ABSTAIN.
- CPR “minimal” means minimal only inside the frozen top-k-plus-universal family.
- R1 exposure-zero and R3 withheld cases retain hidden valid labels for grading
  and candidate recall, despite expecting non-commit actions.
- Query-only profiling cannot infer hidden factors such as R1 exposure; ordinary
  classification there is a deployment limitation, not permission to use
  ground-truth factors.
- Provider seed and temperature zero do not guarantee deterministic inference.

---

## 11. Nondeterminism research and repository decisions

### 11.1 Thinking Machines article

The reviewed article is:

```text
Horace He and Thinking Machines Lab
“Defeating Nondeterminism in LLM Inference”
https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
```

Key lesson: fixed seeds and temperature zero do not ensure identical outputs.
Batch composition, reduction order, floating-point behavior, kernels, routing,
parallelism, quantization, and backend revisions can cause divergence.

CalibRead implications:

- keep repeated same-condition requests;
- record hardware/backend/kernel/provider/model/system fingerprint;
- record batching and request order where self-hosted;
- report exact and parsed-output repeatability;
- optionally benchmark pinned batch-invariant kernels;
- never force stochastic candidate samples to be identical.

The companion `batch_invariant_ops` repository is optional proof-of-concept
software, not a universal dependency. Pin a commit and benchmark compatibility
before using it.

### 11.2 Fxis decision

Repository reviewed:

```text
https://github.com/Pranavbh1/Fxis
```

Decision already recorded in the annotated bibliography:

- do not cite Fxis as evidence of batch-invariant deterministic inference;
- do not make it a required dependency;
- its reviewed implementation mainly wrapped seed settings and had incomplete
  or broken paths;
- seed wrappers do not address batch-order/floating-point mechanisms;
- it may be reevaluated only if a later tagged release provides tested
  batch-invariant operations, hardware/version coverage, and benchmarks.

### 11.3 Repeatability subset

Current default repeatability audit sends two additional same-seed greedy
requests for 50 final observations per suite, totaling 700 repeat calls over
R1–R7. These repeats are separate from confidence estimation.

Recommended outputs:

- all-repeats byte-identical rate;
- parsed action/answer-identical rate;
- pairwise agreement;
- provider/model/fingerprint drift;
- latency/cost distribution;
- disagreement examples.

---

## 12. Bibliography and external resources

Primary bibliography files:

```text
calibread_research/references/ANNOTATED_BIBLIOGRAPHY.md
calibread_research/references/calibread_references.bib
```

The annotated bibliography explains how each source should be used, not merely
its citation. Software/repositories already identified include:

- LM-Polygraph — uncertainty estimators;
- semantic_uncertainty — semantic-entropy reference;
- uncertainty_in_the_wild — domain-shift baselines;
- TorchCP — conformal utilities/test oracle;
- BatchMultivalidConformal — multigroup comparator;
- AbstentionBench — unanswerability external validation;
- MuSiQue — multihop external validation;
- FreshQA — temporal external validation;
- FActScore and SAFE — factuality comparators;
- simple-evals/SimpleQA — evaluation reference;
- OLMo/Pythia — open controlled model/training candidates;
- OLMES — reproducible evaluation harness;
- batch_invariant_ops — optional deterministic backend experiment.

Any external code used in results must have repository URL, full commit SHA,
license, environment lock, model revision, and local modifications recorded.

---

## 13. Current test and validation status

### 13.1 Unit tests

Latest audit results:

```text
calibread_openrouter       8/8 passed
calibread_analytics        8/8 passed
corpus materializer        3/3 passed
```

These tests do not cover the newly found critical/high issues. Passing them is
necessary but not sufficient.

### 13.2 Compilation and syntax

- Python `compileall` passed when `PYTHONPYCACHEPREFIX` was directed to a
  writable `/private/tmp` directory.
- The first compile attempt failed only because macOS’s default bytecode cache
  path was not writable in the managed environment; that was not a source syntax
  failure.
- All JSON files parsed successfully.
- Markdown local-link audit reported no broken local links.
- `git diff --check` found no whitespace errors, but most content is untracked.

### 13.3 Testcase validation

`python3 scripts/validate_testcases.py` returned:

```json
{"valid": true, "errors": [], "total_records": 70000}
```

Per-file counts/hashes matched `testcases/manifest.json`.

### 13.4 Deterministic regeneration

The generator was run into a temporary audit directory and compared against the
checked-in corpus. Files were byte-identical.

### 13.5 Reproduced defects

- Full request estimate reached 62,000 final tasks, 18,000 component tasks, and
  then raised the `int + NoneType` repeatability error.
- All 2,000 R2 `decimal_5` records were assigned profile `ordinary` by the
  current query rule.
- A statistical primitive can return raw p-value zero, and the current
  `value or 1.0` code changes it to 1.0.

### 13.6 What has not been tested

- No live OpenRouter generation was run during the consistency audit.
- No real parametric checkpoint has been trained or served in this workspace.
- No final runner output CSV corpus exists for paper analysis.
- No locked-test release has occurred.
- No human testcase/grader acceptance gate has passed.
- No full cluster-valid risk-control simulation suite exists yet.

---

## 14. Operating commands

Run commands from the thesis workspace unless a package-specific `cd` is shown.

### 14.1 Testcase regeneration and validation

```shell
PYTHONPYCACHEPREFIX=/private/tmp/calibread_pycache \
python3 calibread_research/scripts/generate_testcases.py

PYTHONPYCACHEPREFIX=/private/tmp/calibread_pycache \
python3 calibread_research/scripts/validate_testcases.py
```

Do not regenerate after freeze without a declared version/deviation. Do not
hand-edit JSONL.

### 14.2 Human audit sheet

```shell
python3 calibread_research/scripts/create_human_audit_sample.py
```

The default development sample is intentionally blank and needs human review.

### 14.3 Materializer tests

```shell
cd calibread_research
python3 -m unittest -v scripts/test_materialize_training_corpus.py
```

### 14.4 Runner tests

```shell
cd calibread_openrouter
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

### 14.5 Analytics tests

```shell
cd calibread_analytics
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

### 14.6 Runner environment

```shell
cd calibread_openrouter
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

Copy a template to a **private ignored config**, then add the API key and model
slug only there. Parametric runs should use the T2 and T0 temporal templates,
not the generic public-model template.

### 14.7 Runner commands after defects are repaired

```shell
calibread-openrouter validate --config config.json
calibread-openrouter validate --config config.json --online
calibread-openrouter models --config config.json --contains llama --limit 20
calibread-openrouter estimate --config config.json --suite R1 --split fit
calibread-openrouter run --config config.json --suite R1 --split fit
calibread-openrouter grade --config config.json
```

Do not treat the current estimator as reliable until H01 is fixed.

### 14.8 Locked test acknowledgement

The exact access acknowledgement is:

```json
"test_release_attestation": "I_CONFIRM_WEEK20_FREEZE_IS_ARCHIVED"
```

It must remain unset until preregistration, prompts, graders, profiles, policies,
analysis, code hashes, checkpoint/corpus hashes, and development results have
been archived.

### 14.9 Analytics environment and command

```shell
cd calibread_analytics
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
calibread-analyze --config analysis_config.json
```

Do not trust confirmatory labels until C01/C02/H09 are repaired.

---

## 15. Six-month execution roadmap

The authoritative detailed schedule is
`calibread_research/plans/04_week_by_week_26_week_plan.md`. High-level context:

| Week | Main objective |
|---:|---|
| 1 | lock research question, scope, terminology, contribution boundary |
| 2 | novelty review and preregistration structure |
| 3 | testcase schema/generators and human construction audit |
| 4 | unified/stage-aware knowledge-corpus materialization |
| 5 | small-model injection and R0 pilot |
| 6 | final design, sample size, power, practical margins |
| 7 | scalable, resume-safe generation pipeline |
| 8 | strict parsers, graders, and blinded grader audit |
| 9 | basic uncertainty features and risk-coverage plots |
| 10 | semantic uncertainty implementation/audit or demotion |
| 11 | learned correctness scorer |
| 12 | natural external datasets |
| 13 | ordinary conformal baseline reproduction |
| 14 | global risk-control policy and simulations |
| 15 | CCRC group hierarchy and oracle unit path |
| 16 | predicted query profiler and routing audit |
| 17 | main controlled model training and R0 gates |
| 18 | R1–R3 development-side generation |
| 19 | R4–R7 development generation and analysis freeze |
| 20 | calibration, risk contracts, signed freeze |
| 21 | one-shot locked controlled evaluation |
| 22 | natural validation and shift analysis |
| 23 | final hypothesis statistics and Holm family |
| 24 | ablations, errors, initial full paper |
| 25 | internal review and independent reproducibility |
| 26 | thesis/paper release and archival package |

The current repository contains substantial implementations from weeks 3–16,
but the audit found gaps. Do not assume the calendar boxes are complete merely
because files exist.

---

## 16. Paper-writing rules

The dedicated paper-agent prompt is:

```text
calibread_research/operating_protocols/03_ICLR_PAPER_WRITING_AGENT_PROMPT.md
```

Apply it only after real frozen results and repaired manifests exist.

### 16.1 Claims that are allowed if supported

- false-commit risk changes systematically with controlled Read complexity;
- aggregate calibration can hide hard-group failures, if H3 gates pass;
- query-visible complexity conditioning improves coverage at matched validated
  risk, if H4 gates pass;
- calibration transfer is asymmetric under controlled domain shift, if H5
  passes;
- CPR achieves empirical marginal set coverage under the frozen exchangeable
  candidate mechanism, with fallback and set size fully reported.

### 16.2 Claims that are not allowed

- “the confidence is the probability this individual answer is correct”;
- “OpenRouter public-model results prove parametric storage effects”;
- “contextual prompting is parametric memory”;
- “temperature zero/fixed seed guarantees deterministic inference”;
- “Fxis provides batch-invariant determinism”;
- “CPR is the first conformal LLM generation method”;
- “prediction sets are always small” when universal fallback occurs;
- “CCRC is optimal” outside the frozen policy family/objective;
- causal natural-domain claims from observational data;
- interpreting R3 as passive time decay;
- counting R7 thresholds as independent testcases.

### 16.3 Reporting failures

- Unsupported policy is a result, not an invitation to retune on test.
- Report every exclusion and failed checkpoint gate.
- Report fallback, missing score, provider drift, parsing failure, and cost.
- Retain null results and falsifications.
- Separate confirmatory, secondary, sensitivity, and exploratory outputs.

---

## 17. New-agent repair workflow

### 17.1 Recommended implementation order

1. Read the detailed repair plan.
2. Add regression tests that fail for the selected issue.
3. Repair C01 cluster-valid risk bounds and their simulations.
4. Repair C02 strict analysis preflight.
5. Repair C03 scientific bundle hashing/resume identity.
6. Establish C04 Git/tag/environment provenance.
7. Repair request estimation, p-value handling, H4 bootstrap/profile, CPR keys
   and support, score-method enforcement, provider drift, and output manifests.
8. Repair parser/candidate/provenance measurement issues.
9. Add R0 gate.
10. Decide implement-versus-demote for secondary roadmap features.
11. Complete human audits.
12. Run an offline/mock end-to-end suite.
13. Run a very small real development pilot only.
14. Freeze and archive before any locked-test access.

### 17.2 Testing philosophy

Every methodological repair needs more than a unit example:

- invariant/property tests;
- adversarial malformed-input tests;
- duplicate/mixed-run tests;
- simulation coverage for formal risk/conformal claims;
- deterministic small hand calculations;
- end-to-end mocked runner-to-analysis tests;
- manifest mutation tests.

For C01, duplicating a dependent row inside one world must not narrow the bound.
For C03, changing one prompt/testcase/checkpoint-manifest byte must make resume
fail. For C02, duplicate directories and mixed stages must fail before outputs
are written.

### 17.3 File-edit boundaries

- Preserve user work and unrelated changes.
- Generated testcase JSONL should be changed only through the generator.
- A generator change requires version increment, full regeneration, validation,
  manifest update, and human reaudit before freeze.
- Keep credentials/private configs/output directories untracked.
- Avoid destructive Git or filesystem operations without explicit authority.
- Do not open the sealed test to debug code.

### 17.4 When a design choice is unclear

Check, in order:

1. signed preregistration;
2. final crosswalk;
3. hypothesis execution plan;
4. repair plan;
5. SOP;
6. code/tests.

If the choice would change a primary endpoint, population, practical margin,
group list, split use, or guarantee, stop and obtain the thesis owner’s decision
before implementation.

---

## 18. Outstanding owner decisions

These cannot be silently chosen by a future agent after test access:

1. Which trainable base model family/size(s) and training compute are approved?
2. Which exact OpenRouter/self-hosted endpoints correspond to T0 and T2?
3. Which provider/backend can supply stable structured output/logprobs/identity?
4. Is exact agreement the primary confidence score, or will likelihood/P(True)
   be primary? Missingness behavior must be frozen.
5. Will semantic entropy be implemented or demoted?
6. Will a learned correctness scorer be included or demoted?
7. Will H4 use deterministic query rules or trained profile classifiers?
8. Will the ground-truth profile oracle be implemented as a secondary
   diagnostic?
9. Which R6 continuous shift features and natural datasets are in scope?
10. What exact R0 gate thresholds and checkpoint exclusion rules are signed?
11. Who performs the testcase and output-grader audits and adjudication?
12. Where are signed preregistration, manifests, checkpoints, and results
    archived?

The recommended C01 independent-world bound is a repair of a mathematical
error, not an optional favorable-analysis choice. Its exact implementation and
simulation evidence should nevertheless be frozen before calibration/test.

---

## 19. Historical pre-repair repository state at initial handoff

- Workspace files are currently shown as untracked by Git.
- No project files were modified during the consistency audit itself.
- Two audit/handoff files have now been added:

  ```text
  FINAL_CONSISTENCY_ISSUES_AND_REPAIR_PLAN.md
  AGENT_FULL_THESIS_AND_CODEBASE_CONTEXT.md
  ```

- No live API requests were made.
- No API key was seen or stored.
- No locked-test attestation was set.
- No real paper results currently exist in runner output directories.
- The deterministic testcase corpus and current unit tests pass.
- The code is not yet freeze-ready for the reasons documented above.

---

## 20. Compact glossary

| Term | Meaning in this project |
|---|---|
| Parametric Read | retrieving/using information stored in model parameters/checkpoint |
| Incoming query risk | loss divided by all received queries, including non-commit decisions |
| False commit | attempted answer that is not operationally correct |
| Operational correctness | valid Answer action + factual correctness + unique singleton contract |
| Selective risk | error among committed answers only |
| Answer coverage | fraction of incoming queries receiving a selected Answer |
| Calibration split | data for threshold/conformal cutoff selection, not model fitting |
| Fit/tune | development data for score/profile fitting and design debugging |
| Locked test | one-shot sealed evaluation after archive/attestation |
| CPR | conformal sampled-candidate prediction set with universal fallback |
| CCRC | complexity-conditioned risk-control policy/profile adjustment |
| Universal fallback | vacuous all-answers set; deployed system abstains |
| Hard group | one of 13 frozen R1–R6 risk subpopulations |
| Scientific bundle | implemented content-addressed manifest of every frozen input |
| T0 | initial stored-fact checkpoint before controlled R3 updates |
| T2 | updated checkpoint used for the primary evaluation |
| R7 | policy stress suite, not a seventh primary complexity dimension |
| `c_point_estimate` | descriptive isotonic estimated correctness |
| `c_policy_error_upper` | policy-mixture false-commit upper confidence bound |

---

## 21. Context maintenance rule

This file is a snapshot of the repository and audit state on 2026-07-22. A
future agent making a material change should append a dated context update that
records:

- files changed;
- issue IDs resolved;
- tests/simulations run and results;
- scientific or preregistration decisions made by the owner;
- new hashes/tags;
- remaining blockers;
- whether any split beyond fit/tune/calibrate was accessed.

Do not simply change this context file to declare an issue resolved. The source,
tests, repair acceptance criteria, and manifests must provide the evidence.

---

## 22. Final handoff statement

The CalibRead project has a strong, coherent core: controlled synthetic
parametric knowledge, explicit action contracts, a false-commit risk surface,
five falsifiable hypotheses, and a clear separation between calibration,
policy-level guarantees, and conformal sets. The corpus construction is in good
shape.

The next agent’s priority is not to add more features or open the locked test.
It is to complete the remaining owner/human/experimental gates:

1. review, commit, and tag the repaired baseline;
2. complete the 200-testcase human audit;
3. train and verify T0/T2 checkpoints and execute R0 gates;
4. collect development outputs and complete the 300-output grader audit;
5. sign/archive the preregistration and run a small development pilot.

Once those conditions are met, the repository can support a rigorous thesis and
an ICLR-style paper whether the final hypotheses are supported or falsified.

---

## 23. Dated repair update — 2026-07-22

The full code/method repair pass requested after this context snapshot has now
been implemented. The authoritative per-issue status is the execution ledger
near the top of FINAL_CONSISTENCY_ISSUES_AND_REPAIR_PLAN.md.

### 23.1 Completed code and method repairs

- C01 now certifies risk over independent (run_id, world_id) clusters and
  reports cluster count/effective sample size.
- C02 uses a mandatory strict preflight for confirmatory inputs, including
  artifact, schema/type, unique-key, count, role/stage, returned route, bundle,
  confidence, candidate, and R5 component-link checks.
- C03 creates a content-addressed scientific bundle and locks resume, grading,
  and every required output row to it.
- H01–H09 and M01–M08 are implemented, including zero p-values, paired H4
  bootstrap, query_rules_v1.1, fixed CPR support, fail-closed confidence/route
  handling, atomic analysis publication, strict parsing, clarification metric
  separation, expanded CPR reports, and unambiguous repeatability naming.
- R0 is executable as a development checkpoint gate and excluded from primary
  H/CPR populations.
- R08 templates are generated from executable constants.
- R09 corpus output is deterministically sorted and hashed.
- R10 executes the checked-in JSON Schema before custom corpus invariants.

### 23.2 Frozen scope decisions

Protocol v1.2 resolves R02–R05 by demotion:

- exact agreement is the sole primary confidence score;
- P(True) and token scores are optional availability-labelled diagnostics;
- exact answer entropy is not semantic entropy;
- verbal confidence, semantic clustering, and learned correctness scoring are
  future work;
- H4 uses deterministic query_rules_v1.1, without a trained/oracle profiler;
- H5 remains categorical; continuous R6 shift features/regression are future
  work.

### 23.3 Verification evidence

- 20 runner unit/adversarial tests pass.
- 21 analytics unit/preflight/simulation/end-to-end tests pass.
- 7 research tooling/materializer tests pass.
- All source compiles under Python 3.9.6.
- All JSON documents parse.
- All 70,000 testcases pass JSON Schema plus bespoke validation.
- Regeneration into a temporary directory is byte-identical for the manifest
  and all eight R0–R7 JSONL files.
- The actual full 62,000-observation R1–R7 plan estimates 408,700 requests.
- No API request and no locked-test inference was performed.

### 23.4 Remaining external blockers

1. C04: the files remain untracked and there is no baseline commit/tag. The
   root ignore policy and frozen-run clean-Git enforcement exist, but the
   repository owner must review, commit, and tag.
2. R06: the 200-row human testcase sheet is still blank. The new audit validator
   correctly fails it.
3. R07: the deterministic 100-R0/200-R1–R7 blinded output sampler and automated
   key exist, but real development outputs and human review are required.
4. Real unified corpus training, T0/T2 checkpoints, R0 gate passage, development
   inference, a small real pilot, preregistration signing, and archive steps
   remain to be executed.

Do not mark these external gates complete, open the locked test, or call the
study confirmatory-ready until documentary evidence exists.
