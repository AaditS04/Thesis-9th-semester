# CalibRead Final Consistency Issues and Repair Plan

**Audit date:** 2026-07-22  
**Repository:** `/Users/aadit.shah@zomato.com/Documents/thesis`  
**Audit mode:** read-only review of the proposal, runner, analytics package,
testcase tooling, schemas, configurations, SOPs, research plans, and generated
testcase integrity. No live model inference was performed.

## 1. Executive decision

The project is technically repairable. No issue found requires abandoning the
CalibRead thesis, the seven-suite benchmark, the finalized H1–H5 hypotheses, or
the CPR idea. The frozen testcase corpus is structurally sound.

At the time of the original read-only audit, the repository was **not yet ready
for a confirmatory model run or locked-test release**. The principal reasons
were:

1. the aggregate finite-sample risk bound treats dependent rows as independent;
2. the analysis loader does not enforce the confirmatory data contract;
3. resume identity does not hash all scientific inputs;
4. the current project has no immutable Git revision;
5. several concrete runner and analytics defects can change reported results.

All critical and high-priority issues below should be repaired and regression
tested before spending substantial inference credits. Items explicitly marked
as secondary may instead be removed or demoted in the frozen protocol, but that
decision must be made before the test split is opened.

### Post-repair update — 2026-07-22

The code/method repair pass described by this document is complete. All
code-solvable C/H/M/R items now have implementations and regression evidence.
R02–R05 were resolved before freeze by the explicit protocol-v1.2 demotions in
calibread_research/plans/09_frozen_secondary_scope_decisions.md.

The repository is still **not ready for confirmatory execution** for three
truthfully external reasons:

1. **C04:** the repository has no baseline commit/tag and the current scientific
   files are untracked. Frozen-run code now rejects this state, but the
   repository owner must review, commit, and tag it.
2. **R06:** the existing 200-row testcase audit remains blank and must be
   completed by human reviewers.
3. **R07:** the reproducible 300-output audit tooling is complete, but the audit
   cannot be sampled or human-graded until real development outputs exist.

Real T0/T2 checkpoints, R0 gate results, development inference, and a small real
pilot also remain experimental execution tasks; no results were fabricated
during repair.

## 2. Status vocabulary

| Status | Meaning |
|---|---|
| **Yes — code repair** | Solvable by changing and testing repository code. |
| **Yes — method repair** | Solvable, but the statistical method and paper wording must both change. |
| **Yes — process repair** | Requires a human/repository procedure, not only code. |
| **Yes — implement or demote** | Either implement before freeze or explicitly remove from required claims/deliverables. |

Repair-execution statuses used below:

| Repair status | Meaning |
|---|---|
| **COMPLETED** | Implemented, documented where required, and covered by offline regression evidence. |
| **RESOLVED — DEMOTED** | Formally removed from required protocol-v1.2 claims/deliverables before test access. |
| **PARTIAL — HUMAN EXECUTION PENDING** | Reproducible tooling/gates exist, but a human review using real data is still required. |
| **BLOCKED — REPOSITORY OWNER ACTION** | Code enforcement exists, but commit/tag authority and repository review are external to this repair pass. |

## 2.1 Repair execution ledger

| ID | Repair status | Implementation/evidence | Remaining action |
|---|---|---|---|
| C01 | **COMPLETED** | Independent-(run, world) cluster weights, effective sample size, exact-binomial eligibility assertion, permutation/duplication tests, and perfect-correlation Monte Carlo coverage. | None in code. |
| C02 | **COMPLETED** | Mandatory strict preflight, artifact/type/key/count/role/stage/model/provider/bundle/candidate/R5-link checks, input audit, and explicit incomplete-analysis stamp. | Real inputs must pass it. |
| C03 | **COMPLETED** | Content-addressed scientific bundle in every required row; all-row resume/grade refusal; prompt, testcase, checkpoint, and secret-invariance tests. | None in code. |
| C04 | **BLOCKED — REPOSITORY OWNER ACTION** | Root .gitignore, environment record, Git state in bundles, and clean/tracked frozen-run enforcement are implemented. | Review files, create baseline commit and annotated/signed freeze tags, then verify a clean checkout. |
| H01 | **COMPLETED** | Explicit Boolean repeat flags and frozen full-plan request estimate test: 408,700. | None. |
| H02 | **COMPLETED** | Zero-preserving finite/range-checked primary p-value collection and Holm regression tests. | None. |
| H03 | **COMPLETED** | Joint world resampling within dimension/level-signature strata; covariance and row-order tests. | None. |
| H04 | **COMPLETED** | Versioned query_rules_v1.1 numeric/word/date regexes; all 16,000 R2 rows tested, including 2,000 decimal_5 rows. | Archive assignment distribution before test release. |
| H05 | **COMPLETED** | CPR compound grouping by run, model, and observation with collision tests. | None. |
| H06 | **COMPLETED** | Missing declared confidence stays missing; confirmatory mixed/unavailable methods fail preflight; availability table exported. | None. |
| H07 | **COMPLETED** | Frozen candidate_draw_budget, fixed missing rank, budget validation, recall/fallback/set-size/subgroup exports, and exchangeable simulation. | None. |
| H08 | **COMPLETED** | One-provider/no-fallback config validation and per-response model/provider fail-closed checks. | Real provider identity must match the frozen route. |
| H09 | **COMPLETED** | New-only atomic analysis publication, complete source hashes/code/Python provenance, manifest-last behavior, no-partial-output and hash tests. | None. |
| M01 | **COMPLETED** | Actual request top-p/token cap/model logged for greedy, stochastic, repeat, and P(True); tested. | None. |
| M02 | **COMPLETED** | Whole-response exact-key JSON parser, conditional contracts, and retained answer-presence signal; adversarial tests. | None. |
| M03 | **COMPLETED** | Role/stage/suite/level/checkpoint/provider relationships validated in runner and analytics. | None. |
| M04 | **COMPLETED** | Separate forced_clarification_recovery and end_to_end_clarification_success fields plus dedicated analytics table and wording. | None. |
| M05 | **COMPLETED** | Candidate creation requires parser_status=ok and ANSWER; prose/extra/type/smuggling tests. | None. |
| M06 | **COMPLETED** | CPR recall, coverage CI, fallback, mean/median/p90/p95 size, singleton, and suite/level diagnostic coverage tables. | None. |
| M07 | **COMPLETED** | Hypothesis figure now plots signed probability-point distance from each hypothesis-specific success boundary. | None. |
| M08 | **COMPLETED** | Renamed all-repeats identity rate and added pairwise exact agreement. | None. |
| R01 | **COMPLETED** | R0 runner/config roles, T0/T2 gate templates, development-only preflight gate table, and explicit exclusion from H/CPR. | Real checkpoints must pass the gates. |
| R02 | **RESOLVED — DEMOTED** | Continuous R6 shift features/regression are future secondary work; categorical H5 remains required. | Do not claim continuous shift explanations in protocol v1.2. |
| R03 | **RESOLVED — DEMOTED** | Exact answer entropy retained under its exact name; semantic entropy/NLI clustering removed from required scope. | Do not relabel it semantic entropy. |
| R04 | **RESOLVED — DEMOTED** | Exact agreement is sole primary; P(True)/token scores are optional diagnostics; verbal/learned scorers removed. | Reintroduction would be post-hoc/future work. |
| R05 | **RESOLVED — DEMOTED** | Deterministic query-only query_rules_v1.1 is primary; trained and ground-truth oracle profilers removed. | Reintroduction cannot affect H4. |
| R06 | **PARTIAL — HUMAN EXECUTION PENDING** | Existing 200-row sample is validated fail-closed by validate_human_audit_gates.py. | Humans must fill/review/adjudicate it and reach at least 98% acceptance. |
| R07 | **PARTIAL — HUMAN EXECUTION PENDING** | Deterministic blinded 100-R0/200-R1–R7 sampler, separate automated key, rubric fields, and 98% gate validator are implemented/tested. | Run after development outputs exist; humans must grade and adjudicate all 300 rows. |
| R08 | **COMPLETED** | CSV templates generated from executable constants with shared schema manifest; run manifest uses 64 tokens and actual bundle/request key; drift test added. | None. |
| R09 | **COMPLETED** | Disk-backed deterministic sort by SHA-256 shuffle key then document ID; ordered corpus is atomically written/hashed and order-invariance tested. | Tokenizer-aware equalization remains separately acknowledged, not claimed. |
| R10 | **COMPLETED** | Checked-in Draft-2020-12 schema is executed by a fail-on-unsupported-keyword internal validator before bespoke checks; malformed nested values are collected safely. | None. |

## 3. Release gates

### Gate A — before any large or paid development run

- [x] C01 cluster-valid risk bounds are implemented and simulation-tested.
- [x] C02 confirmatory input validation is implemented.
- [x] C03 scientific bundle hashing and resume refusal are implemented.
- [ ] C04 the code is committed and tagged — **repository owner action**.
- [x] H01 request estimation no longer crashes.
- [x] H02 zero p-values survive Holm correction.
- [x] H06 confidence methods cannot be silently mixed.
- [x] H08 provider/model drift is fail-closed for frozen runs.

### Gate B — before calibration freeze

- [x] H03, H04, H05, H07, and H09 are repaired.
- [x] R0 checkpoint gates are executable.
- [ ] Every real primary configuration passes an offline preflight audit —
  awaiting real T0/T2/R0 outputs.
- [x] The analysis output directory and source-manifest rules are frozen.
- [x] The prompt, grader, schema, profile rules, thresholds, and statistical code are
  content-hashed.

### Gate C — before opening the locked test split

- [ ] Human testcase and grader audits have passed their preregistered thresholds.
- [ ] All expected fit/tune/calibrate row counts and hashes have been reconciled.
- [ ] The signed preregistration and scientific bundle have been archived.
- [ ] The repository is clean at the frozen tag.
- [ ] No unresolved critical or high-priority process issue remains.

## 4. Critical blockers

### C01 — aggregate risk bound ignores repeated-world dependence

**Severity:** Critical  
**Solvable:** **Yes — method repair**

#### Problem

The aggregate contract gives equal weight to R1–R6, equal weight to levels
within a suite, and then applies a weighted Hoeffding interval to individual
rows:

- `calibread_analytics/src/calibread_analytics/policy.py`,
  `mixture_weights()` and `risk_interval()`;
- R2 creates eight level observations from one world;
- R4 creates four level observations from one world;
- R5 creates five depth observations from one world.

Rows from the same world are dependent. Treating their weights as independent
artificially increases effective sample size and can make the aggregate upper
confidence bound too optimistic. This affects H3, H4, exported policy
certificates, and `c_policy_error_upper`.

The exact-binomial hard-group bounds are generally safer because each frozen
hard group contains at most one observation per world. The implementation must
verify that condition instead of assuming it.

#### Repair

1. Retain the existing scientific mixture weights at the row level.
2. Define the independent sampling cluster as `(run_id, world_id)`.
3. For each cluster `g`, calculate:

   ```text
   Z_g = sum_i_in_g w_i L_i
   W_g = sum_i_in_g w_i
   0 <= Z_g <= W_g
   ```

4. Calculate aggregate risk as `sum_g Z_g`.
5. Use the cluster-level weighted Hoeffding radius:

   ```text
   sqrt(log(1/alpha) * sum_g W_g^2 / 2)
   ```

   This treats independent worlds, rather than dependent rows, as the bounded
   random variables.
6. Report cluster effective sample size as `1 / sum_g W_g^2`.
7. Use exact binomial intervals only after asserting that every cluster
   contributes exactly one Bernoulli observation with equal weight.
8. Update the methodology, contract tables, README, SOP, and paper claim notes to
   say “independent-world cluster bound.”

#### Acceptance tests

- Duplicating a level row within the same world must not double effective sample
  size or narrow the bound.
- Permuting rows must not change the bound.
- If every world has one equal-weight row, the result must reduce to the current
  exact-binomial path.
- Monte Carlo coverage under perfect within-world correlation must be at least
  the configured confidence level within simulation error.
- H3/H4 mock analyses must use the new bound in calibration and test exports.

### C02 — analytics does not enforce the confirmatory input contract

**Severity:** Critical  
**Solvable:** **Yes — code repair**

#### Problem

`calibread_analytics.data.validate_config()` checks only that each source has a
`scored_results.csv`. Candidate, component-link, raw-generation, summary,
resolved-config, model-metadata, and observation-spec files are optional in
code, although the analysis SOP says they are required for the paper.

The loader also does not enforce:

- unique input directories;
- unique `(run_id, observation_id)` scored rows;
- unique raw generation keys;
- one configuration/scientific bundle per source;
- expected row counts;
- consistent model and provider identity;
- `analysis_role=primary` **and** `checkpoint_stage=checkpoint_t2` for primary
  results;
- the restricted T0/R3 scope for `secondary_temporal` rows;
- uniform confidence method;
- complete candidate and component-link coverage;
- absence of malformed numeric/JSON values.

`normalize_scored()` currently converts malformed integers to zero, malformed
JSON to empty structures, and malformed floats to missing values. That can turn
data corruption into apparently valid observations.

#### Repair

Create a mandatory `preflight.py` or `audit_inputs()` stage that runs before any
analysis asset is written.

It should:

1. canonicalize and deduplicate source directories;
2. require all paper artifacts for confirmatory analysis;
3. validate required columns and types without silent coercion;
4. validate uniqueness for scored, raw, candidate, and link keys;
5. reconcile observation counts against `observation_specs.jsonl` and
   `run_summary.csv`;
6. verify one `run_id`, config hash, scientific bundle hash, analysis model ID,
   and expected checkpoint stage per source;
7. require primary rows to be `checkpoint_t2` and
   `scientific_status=confirmatory_parametric`;
8. allow secondary temporal rows only for the frozen T0/R3 scope;
9. reject mixed or missing `confidence_method` values in a declared primary
   score analysis;
10. produce `input_audit.json` and `input_audit.csv` before proceeding;
11. abort on every confirmatory violation rather than issuing a warning.

Add a development-only configuration flag for incomplete exploratory analysis.
That mode must stamp every output `NONCONFIRMATORY_INCOMPLETE_INPUT` and must not
produce confirmatory decisions.

#### Acceptance tests

- Listing the same source twice must fail.
- A duplicate scored observation must fail.
- A T0 row labelled primary must fail.
- A missing candidate/link/raw file must fail in confirmatory mode.
- A malformed `false_commit_loss` value must fail instead of becoming zero.
- A source with the wrong config, prompt, testcase, or checkpoint hash must fail.
- A valid primary T2 plus secondary T0 temporal pair must pass and keep the
  secondary rows out of every primary table.

### C03 — resume identity does not include all scientific input contents

**Severity:** Critical  
**Solvable:** **Yes — code repair**

#### Problem

The runner configuration hash includes resolved file paths, but it does not hash
the contents of prompts, testcase JSONL files, the testcase manifest, the
checkpoint manifest, the injected corpus/checkpoint, the schema, or grader code.
Successful requests are considered complete using only:

```text
(observation_id, sample_kind, sample_index)
```

If a prompt, testcase, or checkpoint manifest is edited in place, an existing
output directory can silently reuse generations made under the old content.
Only the first raw row is checked when validating output identity.

#### Repair

1. Build a canonical `scientific_bundle_manifest.json` before `estimate`, `run`,
   or `grade`.
2. Include SHA-256 hashes for:

   - redacted canonical configuration;
   - every selected testcase JSONL and testcase manifest;
   - testcase schema;
   - Read and P(True) prompts;
   - checkpoint manifest and the checkpoint/corpus hashes it declares;
   - grader version and preferably the relevant source-tree hash;
   - model/provider route restrictions;
   - generation schema and profile-rule version.

3. Hash the canonical manifest to obtain `scientific_bundle_sha256`.
4. Store that hash in every raw, scored, candidate, link, and summary row.
5. Lock the output directory to the bundle hash.
6. Include the bundle hash in the completed-request identity or refuse resume
   before completed keys are read.
7. Validate every existing raw row, not only the first.
8. Make `grade` refuse to rebuild results if the current prompts, testcases,
   grader, or bundle differ from the raw run.

#### Acceptance tests

- Editing one prompt byte must make resume fail.
- Editing one testcase label or query must make resume fail.
- Editing the checkpoint manifest contents without changing its path must fail.
- Changing only the API secret or locked-test acknowledgement must not alter the
  scientific bundle hash.
- Every output row must carry the same bundle hash.

### C04 — the project has no immutable code revision

**Severity:** Critical process blocker  
**Solvable:** **Yes — process repair**

#### Problem

The proposal and all CalibRead packages currently appear as untracked files in
Git. The run manifest expects a commit, dirty-state flag, and source-tree hash,
but an untracked working tree cannot be reproduced from a commit.

#### Repair

1. Review secrets and add private configs/output directories to `.gitignore`.
2. Track the proposal, source, tests, schemas, plans, prompts, and testcase
   manifest. Decide whether large JSONL files are normal Git objects, Git LFS
   objects, or reproducibly generated release artifacts with archived hashes.
3. Commit the audited baseline.
4. Create signed or annotated tags for pilot, calibration freeze, and locked-test
   release.
5. Save `git rev-parse HEAD`, `git status --porcelain`, source-tree hash, Python
   version, dependency lock, and environment metadata in every run manifest.
6. Make frozen-run preflight fail when the repository is dirty or required
   files are untracked.

#### Acceptance tests

- A clean checkout at the recorded tag regenerates the same testcase hashes.
- `git status --porcelain` is empty at frozen-run start.
- The recorded source-tree hash matches the checked-out files.

## 5. High-priority implementation issues

### H01 — request estimation crashes when R5 component probes are enabled

**Severity:** High operational defect  
**Solvable:** **Yes — code repair**

#### Problem

Repeatability flags are added to final tasks, after which component tasks without
that field are appended. `estimate_requests()` sums `task.get(...)`, producing
`None` for component tasks and raising:

```text
TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
```

The full current R1–R7 plan with P(True) disabled should estimate:

| Quantity | Count |
|---|---:|
| Final observations | 62,000 |
| R5 component observations | 18,000 |
| R4 clarification turns | 18,000 |
| Generation requests before repeats | 408,000 |
| Repeatability requests | 700 |
| Total requests | 408,700 |

#### Repair

Use an explicit Boolean/default:

```python
sum(bool(task.get("repeatability_selected", False)) for task in tasks)
```

Also initialize `repeatability_selected=False` on every task constructor.

#### Acceptance tests

- Estimate default R1–R7 configuration successfully.
- Estimate R5-only with components on and off.
- Check the frozen full-plan total against 408,700 when current defaults apply.
- Check P(True), auxiliary stochastic samples, and selection overrides
  independently.

### H02 — a valid zero p-value becomes 1.0 before Holm correction

**Severity:** High statistical defect  
**Solvable:** **Yes — code repair**

#### Problem

The expression:

```python
float(item.get("p_value_raw", 1.0) or 1.0)
```

converts a valid `0.0` to `1.0`. Exact tails or zero-variance tests can produce a
numerical zero, so strong evidence can be converted into no evidence.

#### Repair

Treat only `None` or a missing field as unavailable:

```python
value = item.get("p_value_raw")
p = 1.0 if value is None else float(value)
```

Validate that every p-value is finite and in `[0,1]`.

#### Acceptance tests

- Holm adjustment preserves `p=0.0`.
- Missing/`None` becomes 1.0.
- NaN, infinity, and out-of-range p-values fail loudly.

### H03 — H4 bootstrap breaks cross-level world pairing

**Severity:** High statistical defect  
**Solvable:** **Yes — method repair**

#### Problem

`_mixture_bootstrap()` resamples clusters independently inside every
`(dimension, level)` cell. For R2, R4, and R5, the same world appears at multiple
levels, so independent cell resampling breaks the covariance and contradicts
the reported “paired world-cluster comparison.”

#### Repair

1. Construct one vector of policy differences for every independent world.
2. Preserve all level rows belonging to that world when it is resampled.
3. To maintain the frozen level mixture, stratify clusters by
   `(dimension, set_of_levels_present_for_world)` and resample a world once
   within its stratum.
4. Recompute cell means and then the equal-suite/equal-level mixture for each
   bootstrap replicate.
5. Use the same joint resample for global and CCRC outcomes.

#### Acceptance tests

- Every sampled R2/R4/R5 world contributes all its linked levels together.
- With identical global and CCRC decisions, every bootstrap difference is zero.
- Perfectly correlated levels retain their covariance.
- Row order does not change intervals.

### H04 — the H4 query-profile rule misclassifies five-decimal queries

**Severity:** High because H4 uses the profile  
**Solvable:** **Yes — code repair**

#### Problem

The profile rule searches for the words `five decimal`, but R2 queries say
`Round to 5 decimal places`. All 2,000 `decimal_5` records were classified as
`ordinary` instead of `precision` during the audit.

#### Repair

Use frozen regular expressions that recognize numeric and word forms, such as:

```text
round to [0-9]+ decimal place
exact date
YYYY-MM-DD
day, month, and year
```

Create a checked-in profile-rule specification and version its hash. The rule
must use query-visible information only.

#### Acceptance tests

- Every generated R2 level has an explicitly expected predicted profile.
- `decimal_5` is `precision` for all records.
- Profile assignment does not access dimension, level, factors, answer, loss, or
  split.
- Freeze and archive the assignment distribution before test release.

### H05 — CPR candidate groups can collide across runs

**Severity:** High for multi-run analysis  
**Solvable:** **Yes — code repair**

#### Problem

CPR groups candidate rows using only `observation_id`. Two seeds or runs using
the same paper-facing `analysis_id` and testcase observation IDs can therefore
be merged into one candidate set.

#### Repair

Group candidates by:

```text
(run_id, model_id, observation_id)
```

If seed-level candidate pooling is scientifically desired, implement it as a
separate, explicitly named analysis with a preregistered pooling rule.

#### Acceptance tests

- Two runs with the same observation ID remain two CPR examples.
- Repeated input directories are rejected before CPR.
- Calibration/test grouping counts match unique compound keys.

### H06 — confidence-score fallback silently mixes different methods

**Severity:** High when likelihood or P(True) is primary  
**Solvable:** **Yes — code repair**

#### Problem

When token probability or P(True) is missing, the runner silently substitutes
exact agreement and changes `confidence_method` only for that row. Analytics
then combines all `confidence_score` values as if they had one meaning.

#### Repair

Choose one of these frozen behaviors:

1. **Fail-closed primary analysis:** if the declared primary score is missing,
   mark the row invalid and abort the run/analysis completeness gate.
2. **Explicit missingness analysis:** retain a missing score and analyze method
   availability separately; never substitute it into the primary curve.
3. Keep exact-agreement fallback only for nonconfirmatory debugging in a
   separately labelled column.

Require exactly one primary `confidence_method` per analysis population.

#### Acceptance tests

- A missing logprob/P(True) cannot silently enter a primary risk curve.
- Mixed methods cause confirmatory preflight failure.
- Feature-availability counts are exported by model/provider/suite.

### H07 — CPR rank-family support is inferred from calibration observations

**Severity:** High formal-method concern  
**Solvable:** **Yes — method repair**

#### Problem

`maximum_samples` is calculated from the largest observed number of answer
samples in the calibration set. It is not the frozen maximum supported by the
generation protocol. The nested family and missing-answer rank therefore depend
on the calibration sample itself and can differ from test support.

#### Repair

1. Pass a frozen `candidate_draw_budget` from the scientific configuration.
2. Define the score/rank support and universal-fallback rank from that fixed
   budget before calibration data are inspected.
3. Count abstention/non-answer draws according to a preregistered candidate-set
   rule.
4. Export candidate recall, fallback rate, coverage, finite set size,
   singleton rate, and subgroup coverage.
5. State explicitly that minimality is only within the frozen
   top-k-plus-universal nested family.

#### Acceptance tests

- Removing high-rank calibration examples does not redefine family support.
- A correct answer absent from sampled candidates receives the frozen missing
  rank.
- Exchangeable simulation attains marginal coverage.
- Run/seed separation from H05 is preserved.

### H08 — returned model/provider drift is recorded but not rejected

**Severity:** High for frozen runs  
**Solvable:** **Yes — code and configuration repair**

#### Problem

The runner records returned model/provider metadata, but the frozen analysis is
not automatically invalidated if the route changes. `allow_fallbacks=false` is
helpful but should not be the only protection.

#### Repair

1. Require a specific provider route for confirmatory runs.
2. Compare every successful response’s returned model/provider against the
   frozen allowed identity.
3. Mark mismatches invalid and abort the run before grading.
4. Audit supported parameters, system fingerprint, and route metadata.
5. Add explicit, nonconfirmatory handling for providers that cannot expose
   stable identity.

#### Acceptance tests

- A mocked provider/model mismatch fails the frozen run.
- A fallback response cannot enter scored results.
- Model/provider distributions contain one allowed route per frozen source.

### H09 — analysis output reuse and source hashing are unsafe

**Severity:** High reproducibility defect  
**Solvable:** **Yes — code repair**

#### Problem

Analysis writes into existing output directories, overwrites known files, and
leaves unrelated old assets in place. Its manifest hashes generated outputs but
records only the paths—not hashes—of source runner directories.

#### Repair

1. Require a new or empty output directory for every scientific analysis hash.
2. Prefer writing to a temporary staging directory and atomically publishing
   after success.
3. Hash every input CSV, JSON, JSONL, resolved configuration, model metadata,
   and source scientific bundle.
4. Record Python version, source commit, analysis config hash, and analysis code
   hash.
5. Write `analysis_manifest.json` last.
6. Refuse to overwrite an existing analysis with a different source/config
   bundle.

#### Acceptance tests

- Reusing a nonempty output directory with different input fails.
- Modifying one source CSV changes the manifest identity.
- A failed analysis publishes no partial final directory.
- Every listed output exists and matches its manifest hash.

## 6. Medium-priority correctness and provenance issues

### M01 — P(True) request parameters are logged incorrectly

**Severity:** Medium provenance defect  
**Solvable:** **Yes — code repair**

P(True) is sent with `top_p=1.0` and `max_completion_tokens=24`, but the raw CSV
records the main generation configuration’s `top_p` and token cap. Pass actual
request parameters into `_raw_row()` for every request type, rather than reading
global defaults during logging. Test greedy, stochastic, repeat, and P(True)
rows independently.

### M02 — the parser is not as strict as its name and documentation claim

**Severity:** Medium measurement defect  
**Solvable:** **Yes — code repair**

The parser extracts the first JSON object from surrounding prose and does not
reject extra keys. A non-string answer is replaced by `None`, which can hide a
smuggled answer on an `ABSTAIN`/`CLARIFY` response.

Repair by parsing the entire stripped response, rejecting extra properties,
requiring the exact conditional action contract, and retaining an
`answer_field_present` flag even when its type is invalid. Any supplied answer
on a declared non-answer action must receive the frozen malformed/smuggling
grade. Candidate extraction must require `parser_status=ok` and
`action=ANSWER`.

### M03 — configuration does not enforce role/stage/suite relationships

**Severity:** Medium before C02, covered partly by C02  
**Solvable:** **Yes — code repair**

Runner config validation should reject impossible combinations, including:

- primary confirmatory run not at `checkpoint_t2`;
- `secondary_temporal` containing a suite other than R3;
- secondary temporal selection containing levels other than the frozen paired
  level;
- parametric mode without valid checkpoint/corpus hashes;
- R7 being included in the R1–R6 primary mixture.

### M04 — simulated R4 recovery is not an observed interactive success rate

**Severity:** Medium interpretation issue  
**Solvable:** **Yes — code and wording repair**

The runner creates forced second-turn clarification tasks for ambiguous records
whenever the first raw generation exists, even if the model did not emit
`CLARIFY`. This is useful as a recovery-capability experiment, but it is not an
end-to-end interactive success metric.

Keep both measures:

- `forced_clarification_recovery`: second turn supplied regardless of first
  action;
- `end_to_end_clarification_success`: first action was valid `CLARIFY` and the
  selected second-turn answer was correct.

Make the distinction explicit in tables and paper prose.

### M05 — candidate extraction can admit parser-invalid answers

**Severity:** Medium CPR input issue  
**Solvable:** **Yes — code repair**

`candidate_rows()` checks parsed action and nonempty answer but not
`parser_status`. Require a valid contract or define a separate candidate-repair
ablation. Add tests for surrounding prose, extra fields, invalid answer type,
and action/answer smuggling.

### M06 — CPR reporting is too aggregate for the planned paper claims

**Severity:** Medium analytics completeness  
**Solvable:** **Yes — code repair**

Add tables for candidate recall before conformalization, empirical coverage,
coverage confidence intervals, universal fallback rate, finite set-size
distribution, mean/median/quantiles, singleton rate, and subgroup coverage by
R1–R6 suite/level. Clearly separate marginal coverage from subgroup diagnostics.

### M07 — the hypothesis overview figure mixes incomparable effect scales

**Severity:** Medium presentation issue  
**Solvable:** **Yes — plotting repair**

H1–H5 effects and margins have different meanings. Do not place raw effects on
one apparently common quantitative axis. Use small multiples, one panel per
hypothesis, or plot standardized signed distance from each preregistered margin
with clear labels.

### M08 — repeatability metric naming is ambiguous

**Severity:** Low/medium reporting issue  
**Solvable:** **Yes — naming repair**

The current repeatability rate is the fraction of observations for which all
greedy repeats match, not an average pairwise repeat-match probability. Rename
it to `all_repeats_exactly_identical_rate` and optionally add pairwise agreement
and action-only agreement.

## 7. Research-roadmap and package completeness gaps

### R01 — no executable R0 checkpoint acceptance gate

**Severity:** High before checkpoint acceptance  
**Solvable:** **Yes — code repair**

The runner CLI supports R1–R7, while the training plan requires a policy-free R0
gate for every checkpoint. Add R0 to runner selection without adding it to the
R1–R6 H mixture. Implement a dedicated R0 gate table for known-direct,
paraphrase, unknown-entity, and false-premise behavior using preregistered
thresholds and development partitions only.

Acceptance requires tests proving that R0 can run and grade while never entering
H1–H5 or CPR unless a specific secondary analysis requests it.

### R02 — planned R6 continuous shift analysis is absent

**Severity:** Secondary-analysis completeness  
**Solvable:** **Yes — implement or demote**

The R6 protocol calls for frozen embedding distance, domain-classifier log odds,
prompt perplexity, relation/template novelty, and answer-token rarity. It also
calls for pooled/domain calibration transfer and a 5-by-4 matrix.

Either implement a versioned feature package with frozen models, normalization,
fit-only training, and cached hashes, or explicitly mark these analyses as
future/secondary and remove them from required paper deliverables before freeze.
They are not required for the categorical H5 endpoint, but the current roadmap
says they will be produced.

### R03 — semantic entropy is planned but only exact answer entropy exists

**Severity:** Secondary feature completeness  
**Solvable:** **Yes — implement or demote**

`exact_answer_entropy` clusters normalized strings, not semantically equivalent
answers. Do not label it semantic entropy. Either add a frozen semantic
clustering/NLI pipeline with a manually audited clustering sample, or keep exact
entropy and formally demote semantic entropy to omitted/future work.

### R04 — verbal confidence and learned correctness scorer are incomplete

**Severity:** Secondary feature completeness  
**Solvable:** **Yes — implement or demote**

P(True), agreement, and token features exist, but the roadmap’s distinct verbal
confidence and learned correctness scorer do not. Implement them with strict
fit/tune/calibrate separation and cross-fitting, or revise the paper plan and
feature tables before test release.

### R05 — the planned trained query profiler and ground-truth oracle are absent

**Severity:** H4/documentation consistency issue  
**Solvable:** **Yes — implement or revise the frozen method**

The current H4 primary profiler is a deterministic query-text rule set with
fit/tune-learned penalties. The week plan describes trained ambiguity, domain,
hop, temporal, and precision classifiers plus a ground-truth oracle diagnostic.

Choose and preregister one primary approach. A deterministic query-only rule is
acceptable and easier to audit, but then the week plan must be updated. The
ground-truth factor profiler may be added only as a clearly labelled oracle
diagnostic and must never select the primary H4 policy.

### R06 — the human testcase audit is not completed

**Severity:** Required process gate  
**Solvable:** **Yes — process repair**

The 200-row `human_audit_sample.csv` exists, but reviewer and acceptance fields
are blank. Complete the blind audit, adjudicate rejections, regenerate/version
the corpus if required, and demonstrate at least the planned 98% acceptance.
Any regeneration must occur before the scientific bundle and test split are
frozen.

### R07 — the planned 300-output grader audit is not represented

**Severity:** Required process gate  
**Solvable:** **Yes — process and tooling repair**

Create a reproducible sampler for the planned 100 R0 and 200 stratified R1–R7
development outputs. Store blinded human grades, automated grades, agreement,
issue codes, adjudication, and final rubric version. Parser/grader changes after
this audit must trigger a new grader hash and, if after freeze, a declared
deviation.

### R08 — legacy CSV and run-manifest templates drift from executable schemas

**Severity:** Medium provenance/documentation issue  
**Solvable:** **Yes — code/document repair**

The research templates contain fields not emitted by the runner, omit newer
runner fields, use `max_new_tokens=32` while current examples use 64, and define
a unique key different from the actual raw/resume key.

Generate templates from the runner’s field constants and a shared schema
version. Delete or explicitly label obsolete templates. Add a test comparing
template headers and manifest decoding settings with executable configuration.

### R09 — materialized corpus ordering is not fully enforced by the materializer

**Severity:** Medium training reproducibility issue  
**Solvable:** **Yes — code or protocol repair**

The materializer emits deterministic shuffle keys but does not itself produce a
fully shuffled/token-balanced training order. Either sort/materialize the final
order in code and hash it, or make the downstream trainer’s required sort and
tokenization steps explicit and independently verified. The existing plan
already acknowledges that tokenizer-aware filler/equalization is not yet done.

### R10 — testcase validation is bespoke rather than complete JSON Schema validation

**Severity:** Low/medium robustness issue  
**Solvable:** **Yes — code repair**

The existing validator currently passes all 70,000 cases and performs valuable
custom leakage/balance checks. Add actual validation against
`testcase.schema.json`—using a pinned validator library or a complete internal
implementation—and ensure malformed/missing nested values produce collected
errors rather than secondary exceptions.

## 8. Items that are consistent and should be preserved

The repair work should not disturb the following verified properties:

- `H(theta,Q)` is implemented as false commits divided by incoming queries.
- `commit_correct` requires a valid Answer action, factually correct content,
  and an operationally unique singleton.
- R4 ambiguous singleton answers are false commits even if they are one
  plausible interpretation.
- R7 is a policy stress suite and is excluded from the primary R1–R6 mixture.
- H1–H5 broadly implement the final crosswalk rather than the superseded P03
  hypothesis wording.
- Testcase IDs and exact query strings are unique.
- Cross-split subject/relation keys do not leak.
- Generated answer text is not directly leaked into queries.
- All 70,000 records pass the current validator and manifest hashes.
- Deterministic regeneration is byte-identical.
- The runner, analytics, and materializer unit tests currently pass.

## 9. Recommended repair sequence

### Phase 1 — scientific validity and immutability

1. C01 cluster-valid aggregate certificate.
2. C02 strict confirmatory input audit.
3. C03 scientific bundle hashing and resume lock.
4. C04 commit/tag/environment provenance.
5. H09 analysis input/output manifest protection.

### Phase 2 — result-changing defects

1. H01 estimator crash.
2. H02 zero-p Holm bug.
3. H03 paired H4 bootstrap.
4. H04 query-profile rule.
5. H05/H07 CPR identity and frozen family.
6. H06 confidence-method enforcement.
7. H08 model/provider fail-closed behavior.

### Phase 3 — measurement correctness

1. M01 P(True) provenance.
2. M02/M05 strict parsing and candidate validity.
3. M03 role/stage validation.
4. M04 clarification metric separation.
5. M06 CPR diagnostic expansion.
6. M07/M08 reporting labels and plots.

### Phase 4 — roadmap completion

1. R01 executable R0 gate.
2. Decide implement-versus-demote for R02–R05.
3. Complete R06/R07 human audits.
4. Repair R08–R10 schemas, ordering, and validation.

### Phase 5 — final verification

1. Run all unit tests and new regression/property tests.
2. Run deterministic testcase regeneration and manifest validation.
3. Run a no-network full request estimate.
4. Run a 10-case-per-suite mocked end-to-end generation and analysis.
5. Run a small real development pilot; do not use locked test.
6. Reconcile every source/output row and hash.
7. Archive the preregistration and scientific bundle.
8. Tag the frozen release.

## 10. Definition of “ready for confirmatory execution”

CalibRead should be called ready only when all of the following are true:

- zero unresolved critical/high issues;
- cluster-valid certificates have simulation evidence;
- every scientific input is content-addressed;
- runner resume refuses any changed scientific bundle;
- confirmatory analytics rejects incomplete, duplicated, mixed-stage, mixed-score,
  or malformed input;
- R0 acceptance gates pass for every evaluated checkpoint;
- human testcase and grader audits pass;
- the repository is clean and tagged;
- development/calibration outputs reconcile exactly with manifests;
- the locked test attestation is still unset until all preceding conditions are
  archived.

Only after this definition is satisfied should the locked test split be opened
and the final ICLR-style paper assets generated.
