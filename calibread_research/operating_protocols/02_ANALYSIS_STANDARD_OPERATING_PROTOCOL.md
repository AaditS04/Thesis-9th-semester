# CalibRead analysis standard operating protocol

Document ID: `CALIBREAD-SOP-ANALYSIS-001`  
Protocol version: `1.0`  
Applies to: accepted CalibRead runner CSVs, H(θ,Q), H1–H5, calibration,
risk-controlled policies, CPR, diagnostics, figures, tables, and paper-asset
archiving

## 1. Purpose

This SOP begins after inference data has passed
`01_TEST_EXECUTION_STANDARD_OPERATING_PROTOCOL.md`. It converts immutable runner
artifacts into the statistical results and figures used by the paper.

The analytics package is deliberately separate from the inference package. It
does not call OpenRouter, does not alter model responses, and does not create
new test answers. It reads CSV artifacts, executes the frozen analysis, and
writes a new paper-asset directory.

## 2. Non-negotiable analysis rules

1. Use only accepted, immutable runner output directories.
2. Keep the primary T2 and secondary temporal T0 roles intact.
3. Never tune thresholds, groups, bins, hypotheses, or exclusions on test.
4. Never rerun with several analysis settings and report only the favorable
   version.
5. Never treat stochastic generations as independent queries.
6. Never interpret a public-model/contextual run as confirmatory parametric
   evidence.
7. Never report the CPR marginal certificate as a posterior guarantee for one
   answer.
8. Never call the policy-level error bound an individual-answer bound.
9. Report `UNSUPPORTED`, `NOT_SUPPORTED`, `NOT_CONFIRMATORY`, and null results
   exactly as produced.
10. Preserve the original analysis config, source hashes, output manifest, and
    every generated table—not only figures used in the main text.

## 3. Required inputs

For the confirmatory experiment, the analysis config should point to:

1. primary T2 runner directory, normally
   `../../calibread_openrouter/outputs/calibread_parametric_t2_001`;
2. secondary T0 temporal runner directory, normally
   `../../calibread_openrouter/outputs/calibread_parametric_t0_temporal_001`.

Each input must contain:

- `scored_results.csv` — required;
- `candidate_sets.csv` — required for CPR;
- `component_links.csv` — required for H2 and R5 error attribution;
- `raw_generations.csv` — required for cost, latency, and repeatability audits;
- `run_summary.csv` — required for pre-analysis acceptance review;
- `resolved_config.redacted.json`;
- `model_metadata.json`;
- `observation_specs.jsonl`.

The package technically loads optional candidate/link/raw files when present,
but their absence makes the corresponding paper analysis incomplete. Treat
missing files as a blocker for the confirmatory paper.

## 4. Understand primary versus secondary rows

Primary rows must satisfy:

```text
analysis_role = primary
checkpoint_stage = checkpoint_t2
```

Only these rows enter:

- H(θ,Q);
- aggregate metrics;
- H1–H5;
- reliability and confidence quality;
- H3/H4 contracts;
- CPR;
- calibrated Read pairs;
- main figures and tables.

Secondary rows must satisfy:

```text
analysis_role = secondary_temporal
checkpoint_stage = checkpoint_t0
dimension_id = R3
level = current_after_update
```

They enter only the R3 temporal confusion table and paired T0/T2 update-effect
analysis. This filtering is enforced by code, but must also be checked manually.

## 5. Prepare the analytics environment

```shell
cd /Users/aadit.shah@zomato.com/Documents/thesis/calibread_analytics
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
calibread-analyze --help
```

The package has no third-party runtime dependency. SVG figures and statistical
calculations are generated with the Python standard library.

Record Python version and `pip freeze` in the analysis log.

## 6. Verify analytics code before reading test results

```shell
cd /Users/aadit.shah@zomato.com/Documents/thesis

PYTHONPYCACHEPREFIX=/private/tmp/calibread-pycache \
PYTHONPATH=calibread_analytics/src \
python3 -m unittest discover -s calibread_analytics/tests -v

PYTHONPYCACHEPREFIX=/private/tmp/calibread-pycache \
PYTHONPATH=calibread_analytics/src \
python3 -m compileall -q calibread_analytics/src calibread_analytics/tests
```

Acceptance condition: all tests report `OK`; compilation reports no error.

Do not modify analytics code after seeing confirmatory test results unless the
change is an openly documented correction. Preserve original and corrected
outputs if such a correction becomes necessary.

## 7. Complete the analysis config

Create a private analysis config:

```shell
cd /Users/aadit.shah@zomato.com/Documents/thesis/calibread_analytics
cp analysis_config.parametric.example.json analysis_config.json
```

Edit:

- `inputs`: exact accepted T2 and T0 output directories;
- `output_dir`: a new, unique paper-asset directory;
- `primary_model_id`: exact shared `model.analysis_id` written into scored
  rows;
- `paper.analysis_version`: frozen analysis version if it differs from the
  example.

The private `analysis_config.json` and `paper_assets/` are git-ignored.

## 8. Freeze and understand analysis parameters

Default confirmatory parameters are:

| Field | Default | Meaning |
|---|---:|---|
| `confidence_column` | `confidence_score` | Frozen score used for ordering/calibration/policies |
| `target_false_commit_risk` | 0.05 | Target H-like policy loss per incoming query |
| `calibration_confidence` | 0.95 | Confidence level for risk certificates |
| `cpr_alpha` | 0.05 | CPR target miscoverage |
| `threshold_start` | 0.00 | First finite threshold |
| `threshold_stop` | 1.00 | Last finite threshold |
| `threshold_step` | 0.01 | Threshold-grid increment |
| `bootstrap_replicates` | 2,000 | Cluster/paired bootstrap replicates |
| `permutation_replicates` | 5,000 | H1 exposure-label permutations |
| `random_seed` | 20260722 | Reproducible analytics RNG seed |
| `ece_bins` | 10 | Equal-width reliability bins |
| `minimum_group_n` | 100 | Minimum calibration rows for a certified group |

These values must be frozen before test access. Changing them after test is a
new, non-confirmatory analysis unless the preregistration explicitly permits
the change.

## 9. Pre-analysis data acceptance

### 9.1 Confirm both directories exist

```shell
ls -lh ../calibread_openrouter/outputs/calibread_parametric_t2_001
ls -lh ../calibread_openrouter/outputs/calibread_parametric_t0_temporal_001
```

### 9.2 Confirm roles, stages, models, and statuses

```shell
python3 -c 'import csv,collections; paths=["../calibread_openrouter/outputs/calibread_parametric_t2_001/scored_results.csv","../calibread_openrouter/outputs/calibread_parametric_t0_temporal_001/scored_results.csv"]; [print(p,collections.Counter((r["model_id"],r["analysis_role"],r["checkpoint_stage"],r["scientific_status"]) for r in csv.DictReader(open(p)))) for p in paths]'
```

Confirm:

- shared analysis model ID is identical;
- T2 role/stage is primary/checkpoint_t2;
- T0 role/stage is secondary_temporal/checkpoint_t0;
- confirmatory rows say `confirmatory_parametric`;
- actual model/provider provenance remains distinct where expected.

### 9.3 Confirm primary final-query counts

```shell
python3 -c 'import csv,collections; p="../calibread_openrouter/outputs/calibread_parametric_t2_001/scored_results.csv"; c=collections.Counter((r["dimension_id"],r["split"]) for r in csv.DictReader(open(p)) if r["observation_kind"]=="final" and r["analysis_role"]=="primary"); print(*sorted(c.items()),sep="\n")'
```

Expected totals are listed in the test-execution SOP. The primary locked-test
total must be 15,500 final queries.

### 9.4 Confirm T0 contains only the paired level

```shell
python3 -c 'import csv,collections; p="../calibread_openrouter/outputs/calibread_parametric_t0_temporal_001/scored_results.csv"; print(collections.Counter((r["dimension_id"],r["level"],r["split"]) for r in csv.DictReader(open(p)) if r["observation_kind"]=="final"))'
```

Expected level: R3 `current_after_update` only, including 500 locked-test
worlds.

### 9.5 Confirm candidate and link artifacts are nonempty

```shell
python3 -c 'import csv; root="../calibread_openrouter/outputs/calibread_parametric_t2_001"; print("candidates",sum(1 for _ in csv.DictReader(open(root+"/candidate_sets.csv")))); print("links",sum(1 for _ in csv.DictReader(open(root+"/component_links.csv"))))'
```

### 9.6 Confirm no unexplained missing scored observations

Compare `run_summary.csv` fields:

- `observations_expected`;
- `observations_scored`;
- `raw_rows`;
- `success_rows`;
- `error_rows`.

Failure rows may remain as audit history, but every planned observation must
have the successful greedy response required for scoring.

### 9.7 Confirm no duplicate primary observation identity

Across primary inputs, `(run_id, observation_id)` must be unique. Distinct model
runs may reuse testcase IDs, but they must retain distinct run IDs and model
IDs. Do not accidentally list the same output directory twice.

## 10. Run analysis

```shell
cd /Users/aadit.shah@zomato.com/Documents/thesis/calibread_analytics
source .venv/bin/activate
calibread-analyze --config analysis_config.json
```

The command prints a JSON summary containing:

- output directory;
- primary model ID;
- models found;
- primary scored-row count;
- H1–H5 decisions;
- CPR summary;
- number of generated files.

Save this terminal summary in the analysis log. The command performs no API
calls and incurs no inference cost.

## 11. Analysis pipeline performed by the command

In order, the package:

1. loads and type-normalizes runner CSVs;
2. excludes secondary rows from all primary analyses;
3. selects the preregistered primary model ID;
4. computes H(θ,Q) by model, suite, and controlled level;
5. computes aggregate factual/action/coverage/risk/cost summaries;
6. constructs risk–coverage curves over the frozen threshold grid;
7. computes reliability bins and confidence-quality metrics;
8. creates auxiliary, error-taxonomy, cost, latency, and repeatability tables;
9. computes the paired R3 T0/T2 diagnostic;
10. executes H1–H5 and five-way Holm correction;
11. calibrates CPR on the calibrate split and evaluates once on test;
12. fits the descriptive isotonic confidence mapping on fit/tune;
13. exports calibrated Read pairs and policy certificates;
14. writes per-suite outputs;
15. generates SVG figures and LaTeX tables;
16. writes methodology/claim notes;
17. hashes generated assets into `analysis_manifest.json`.

## 12. Primary H(θ,Q) output

File: `tables/hallucination_index.csv`

For each primary model and each R1–R7 level it reports:

- queries and worlds;
- commits and false commits;
- `H_false_commit`;
- world-cluster bootstrap interval;
- `H_selective`;
- factual-wrong commits per query;
- answer coverage;
- factual accuracy;
- controlled factor name and value.

For one model, the complete surface has 37 level cells:

```text
R1 7 + R2 8 + R3 4 + R4 4 + R5 5 + R6 4 + R7 5 = 37
```

If fewer cells appear, stop and investigate missing primary rows.

## 13. Confidence-quality analysis

File: `tables/confidence_quality.csv`

Computed on attempted final answers, both aggregate and by suite:

- accuracy and mean confidence;
- Brier score;
- log loss;
- ECE and MCE;
- AUROC for correctness ranking;
- average precision for correctness;
- area under the selective risk–coverage curve (AURC);
- excess AURC above the oracle ordering.

Interpretation:

- lower Brier/log loss/ECE/MCE is better;
- higher AUROC/AP is better;
- lower AURC/excess AURC is better;
- a strong AUROC with poor ECE means the score ranks answers but is not
  probability calibrated;
- a low ECE caused by nearly constant scores is not sufficient evidence of
  useful selectivity—inspect AUROC/AP and risk–coverage together.

## 14. Reliability output

Files:

- `tables/reliability_bins.csv`;
- `tables/calibration_summary.csv`;
- `figures/fig_calibration.svg`.

The reliability curve compares average reported confidence with empirical
commit correctness. Positive `calibration_gap` means overconfidence; negative
means underconfidence.

Do not compare ECE values computed with different bins as if they were the same
estimand. The main paper uses the frozen bin count and may put alternative bins
only in a labeled sensitivity appendix.

## 15. H1 execution and interpretation

Primary data: R1 locked-test final rows.  
Outcome: exact operationally correct committed retrieval.  
Factor: exposure `{0,1,2,4,8,16,32}`.

The code:

1. aggregates by fact/world;
2. fits a nondecreasing isotonic Bernoulli curve;
3. compares it with the pooled-accuracy null using a likelihood-ratio statistic;
4. permutes exposure labels across fact clusters while preserving exposure
   counts;
5. obtains one one-sided omnibus p-value;
6. bootstraps the exposure-16 minus exposure-1 accuracy contrast;
7. requires its one-sided 95% lower bound to exceed 0.05;
8. sends the single H1 p-value into Holm correction.

`SUPPORTED` means both statistical monotonicity and the preregistered practical
gain are supported. It does not prove one universal exposure threshold across
models.

## 16. H2 execution and interpretation

Primary data: R5 locked-test depths 2–5.  
Eligibility: every required direct component probe for that graph/depth was
answered correctly.  
Endpoint: final composition-error probability conditional on component
availability.

The code:

1. joins final rows to component rows through `component_links.csv`;
2. keeps graph/depth rows with all components correct;
3. computes final operational error;
4. clusters/bootstraps by graph/world;
5. tests whether conditional composition error exceeds 5%.

`SUPPORTED` is evidence of a composition failure beyond missing component
facts. It is a failure-mode result, not a success claim about the model.

The separate `h2_independence_diagnostic.csv` compares observed final error with
a graph-excluded product reference on all graphs. It is explicitly diagnostic,
not the confirmatory H2 estimand.

## 17. H3 execution and interpretation

H3 asks whether a threshold certified only for aggregate false-commit risk can
still fail on prespecified hard groups.

The code:

1. uses calibrate data only to select a threshold satisfying aggregate target
   risk;
2. evaluates the frozen threshold on test;
3. checks aggregate test validity;
4. audits 13 frozen hard groups with simultaneous exact bounds;
5. tests whether the worst group exceeds target by more than two percentage
   points.

`SUPPORTED` means aggregate calibration masked a meaningful hard-group failure.
It is evidence for the need for parametric/group-aware reliability contracts,
not evidence that the aggregate policy is safe.

Inspect `tables/h3_contracts.csv` and `figures/fig_hard_groups.svg`.

## 18. H4 execution and interpretation

H4 compares:

- a global joint-safe threshold policy; and
- predicted-profile complexity-conditional risk control (CCRC).

The predicted profile is inferred from query text only. It never reads test
answers, correctness, factors, or suite labels. Profile penalties are learned
on fit/tune, thresholds are selected on calibrate, and test is used once.

Both policies must pass the same aggregate-plus-13-group calibration gate. If
either cannot be certified, H4 is `UNSUPPORTED`; the code does not substitute a
least-bad threshold.

When both are certified, the code performs a paired world-cluster comparison
of answer coverage. `SUPPORTED` requires a gain above three percentage points
with the preregistered one-sided test and Holm-adjusted significance.

Inspect:

- `tables/h4_contracts.csv`;
- `tables/profile_assignment_audit.csv`;
- `tables/policy_diagnostics.json`.

## 19. H5 execution and interpretation

H5 evaluates four frozen calibration-source to test-target domain directions.
For every direction it compares:

- a threshold calibrated in the source domain and transferred to target; and
- a threshold calibrated within the target domain.

The endpoint is cross-domain minus within-domain false-commit risk. Directional
tests and simultaneous intervals are multiplicity controlled. H5 uses the
maximum prespecified directional degradation.

`SUPPORTED` means domain transfer worsened false-commit risk by more than two
percentage points. It is a domain fragility result, not a robustness success.

Inspect:

- `tables/h5_domain_directions.csv`;
- `figures/fig_domain_transfer.svg`.

## 20. Holm-family interpretation

File: `tables/hypothesis_results.csv`

There must be exactly five rows: H1–H5. Each contains:

- raw p-value;
- Holm-adjusted p-value;
- effect estimate and interval;
- preregistered margin;
- confirmatory flag;
- scientific status note;
- final decision.

Decision meanings:

| Decision | Meaning |
|---|---|
| `SUPPORTED` | Preregistered effect/margin and Holm criteria are satisfied |
| `NOT_SUPPORTED` | Confirmatory run, but evidence did not satisfy all criteria |
| `UNSUPPORTED` | Required policy/eligible population could not be constructed or certified |
| `NOT_CONFIRMATORY` | Input status does not permit confirmatory interpretation |

Do not convert `UNSUPPORTED` to `NOT_SUPPORTED`, or vice versa. The first says
the planned statistical object was unavailable; the second says it was
available but did not pass.

## 21. Hard-group and aggregate weighting logic

The aggregate mixture gives:

1. equal total weight to each of R1–R6; and
2. equal weight to every level within a suite.

This prevents a large suite, such as R2, from dominating merely because it has
more rows or levels.

The row-level mixture weights are retained, but uncertainty is calculated over
independent (run_id, world_id) clusters. For cluster g, sum its weighted losses
and weights, then use the independent-world weighted Hoeffding radius based on
the squared cluster weights. Report both the number of clusters and
cluster-effective sample size. Use an exact binomial bound only after asserting
that every cluster contributes exactly one equal-weight Bernoulli observation.
Threshold selection accounts for the finite threshold-by-group family. Do not
reinterpret these certificates under a different deployment mixture without
recalibration.

## 22. CPR execution and interpretation

Files:

- `tables/cpr_summary.csv`;
- `tables/cpr_test_sets.csv`;
- `figures/fig_cpr.svg`.

CPR uses calibrate rows to choose a rank cutoff in a frozen nested family of
top-k sampled answer clusters. It evaluates that cutoff once on test.

The CPR population includes only operationally unique R1–R6 targets. R4
ambiguity levels 2–4 are excluded because they have no single correct label.

When sampled candidates do not contain enough correct labels for the required
quantile, the family reaches an all-answers vacuous set. The deployed system
abstains in this case. This is formally covering but uninformative, so always
report fallback rate beside coverage.

Required reporting:

- target coverage `1-alpha`;
- calibration sample size;
- empirical test coverage and interval;
- rank cutoff;
- mean non-vacuous set size;
- all-answers fallback rate;
- exchangeability and frozen-candidate-mechanism assumptions.

Never claim globally minimum set size. Minimality holds only within the frozen
nested candidate family.

## 23. Calibrated Read-pair interpretation

File: `tables/calibrated_read_pairs.csv`

Important columns:

- `y`: answer returned only when the frozen policy selects the model commit;
- `returned_action`: ANSWER or policy ABSTAIN;
- `raw_confidence_score`: uncalibrated ordering score;
- `c_point_estimate`: isotonic descriptive correctness estimate;
- `estimated_error_probability`: `1-c_point_estimate`;
- `c_policy_error_upper`: formal policy-mixture false-commit upper bound;
- `policy_non_false_commit_lower`: its complement;
- `individual_error_bound_available`: always zero;
- `formal_scope`: explicit guarantee scope.

The same policy-level bound is repeated beside selected rows for operational
use; repetition does not turn it into a conditional individual-answer bound.

## 24. R3 paired checkpoint analysis

Files:

- `tables/r3_temporal_confusion.csv`;
- `tables/r3_paired_update_effect.csv`;
- `figures/fig_r3_update_effect.svg`;
- copies under `suites/R3/`.

For `current_after_update`, rows are paired by analysis model ID, split, and
world. The table reports:

- T0 current-value accuracy;
- T2 current-value accuracy;
- paired T2-minus-T0 gain and bootstrap interval;
- T0/T2 stale-answer rates;
- paired stale-rate change and interval.

This is a secondary controlled-update diagnostic. It must not be pooled into
the main T2 H surface.

## 25. Error taxonomy

Files:

- `tables/error_taxonomy.csv`;
- `figures/fig_error_taxonomy.svg`.

Automatic categories include:

- formatting/parser failure;
- stale value;
- ambiguity forced answer;
- precision/rounding failure;
- synthesis failure with available components;
- component fact unavailable;
- refusal/abstention despite known target;
- wrong entity/value;
- wrong action.

The automatic taxonomy covers the full test output, but the paper should also
report the frozen blinded human audit protocol where applicable. Do not treat
automatic categories as human-adjudicated semantic labels.

## 26. Cost, latency, and repeatability

Files:

- `tables/cost_and_latency.csv`;
- `tables/repeatability_audit.csv`.

Cost/latency is separated by actual requested endpoint, role, stage, suite, and
split. Repeatability reports:

- exact byte/text agreement rate;
- canonical parsed-output agreement rate;
- same-seed/parameter verification rate;
- same returned model/provider/fingerprint rate;
- fingerprint availability rate.

A missing fingerprint does not prove backend instability; report it as missing
metadata. A stable seed does not prove deterministic inference; use the measured
repeatability rates.

## 27. Generated figures

The expected main vector figures are:

1. `fig_h_complexity.svg` — H across R1–R6 controlled levels;
2. `fig_risk_coverage.svg` — false-commit risk versus answer coverage;
3. `fig_calibration.svg` — reliability;
4. `fig_hard_groups.svg` — subgroup risk and target line;
5. `fig_domain_transfer.svg` — H5 direction matrix;
6. `fig_cpr.svg` — target/empirical coverage and fallback;
7. `fig_hypotheses.svg` — H1–H5 effects;
8. `fig_error_taxonomy.svg` — failure counts;
9. `fig_r3_update_effect.svg` — paired T0/T2 current-value accuracy.

Open every SVG and verify labels, axis limits, number of panels, and absence of
truncated text. Never edit plotted numerical values by hand. If layout changes
are needed, modify plotting code before the freeze or report a post-freeze
presentation-only change that leaves data and estimands unchanged.

## 28. Generated LaTeX tables

- `tables/table_hypotheses.tex`;
- `tables/table_main_metrics.tex`.

These use escaped text and `booktabs` commands. Ensure the paper preamble loads
`booktabs`. Source CSV files remain authoritative; the TeX tables are display
artifacts.

## 29. Per-suite outputs

Every `suites/R1` through `suites/R7` directory contains:

- `metrics.csv`;
- `hallucination_index.csv`;
- `risk_coverage.csv`;
- `linked_confirmatory_hypothesis.csv`.

R3 also contains temporal checkpoint diagnostics. R7 has no linked
confirmatory hypothesis because it is a policy stress suite, not a seventh
independently randomized causal factor.

## 30. Post-analysis acceptance checks

### 30.1 Confirm exactly five hypothesis rows

```shell
python3 -c 'import csv; p="paper_assets/calibread_parametric_001/tables/hypothesis_results.csv"; rows=list(csv.DictReader(open(p))); print(len(rows),[r["hypothesis_id"] for r in rows],[(r["hypothesis_id"],r["decision"]) for r in rows])'
```

Expected IDs: H1, H2, H3, H4, H5.

### 30.2 Confirm the complete H surface

```shell
python3 -c 'import csv,collections; p="paper_assets/calibread_parametric_001/tables/hallucination_index.csv"; rows=list(csv.DictReader(open(p))); print(collections.Counter(r["model_id"] for r in rows)); print(collections.Counter(r["dimension_id"] for r in rows))'
```

Expected for one complete primary model: 37 cells.

### 30.3 Confirm primary status

All H1–H5 rows should have `confirmatory=1` and an observed status set contained
in `confirmatory_parametric`. If not, the package correctly prevents a
confirmatory label.

### 30.4 Confirm CPR population

For a complete one-model run, the expected unique-target locked-test population
is 12,750 observations:

```text
R1 1,750 + R2 4,000 + R3 2,000 + R4(unique only) 500
+ R5 2,500 + R6 2,000 = 12,750
```

If test N differs, investigate missing candidate rows or unintended ambiguity
inclusion/exclusion.

### 30.5 Confirm R3 pairs

The T0 and T2 `current_after_update` locked test should produce 500 matched
worlds for one model/seed. A smaller `n_pairs` means an endpoint, split, world,
or analysis ID mismatch.

### 30.6 Confirm manifest integrity

Open `analysis_manifest.json` and confirm it records:

- analysis config hash;
- analysis version;
- primary model;
- source directories;
- row count;
- file path, byte count, and SHA-256 for every generated asset.

## 31. Sanity checks that do not change the preregistration

These checks detect mistakes; they are not opportunities to choose a better
result.

- H values must lie in [0,1].
- H interval endpoints must lie in [0,1].
- answer coverage must lie in [0,1].
- false commits cannot exceed commits or incoming queries.
- H selective is undefined/blank when commits are zero.
- reliability bin counts must sum to attempted test answers.
- CPR empirical coverage and fallback rate must lie in [0,1].
- risk UCB must not be below risk LCB.
- source/target H5 directions must match the four frozen directions.
- H4 profile audit must never depend on test correctness fields.
- secondary temporal rows must not appear in the main H table.
- R4 ambiguity 2–4 must not appear in CPR sets.
- R7 thresholds must not inflate query count.

## 32. What to do when a policy is unsupported

If H3 or H4 calibration cannot certify any threshold:

1. keep the `UNSUPPORTED` result;
2. report zero/limited achievable coverage and calibration diagnostics;
3. do not select the threshold with the smallest violation;
4. do not lower the confidence level after seeing test;
5. do not remove hard groups;
6. discuss abstention/certificate feasibility as a result.

An unsupported non-vacuous policy can be a central negative finding.

## 33. Sensitivity and exploratory analyses

Only run prespecified sensitivity analyses after the primary output is archived.
Write them to a new output directory and label them exploratory or secondary.

Examples that require explicit labeling:

- alternative ECE bins;
- alternative confidence score;
- different target risk;
- different threshold resolution;
- other domain directions;
- other hard groups;
- model-size or training-seed pooling;
- optional retention/interference checkpoints;
- alternative CPR candidate mechanisms.

Never overwrite the primary paper-asset directory with a sensitivity run.

## 34. Archive analysis outputs

Archive:

- accepted runner source directories or their immutable hashes;
- exact `analysis_config.json` with no secrets;
- analytics source version;
- console summary/log;
- complete `paper_assets` directory;
- `analysis_manifest.json`;
- all CSVs, not only headline results;
- all SVGs and TeX tables;
- any deviations and corrections.

Create a read-only archive copy before beginning paper drafting.

## 35. Analysis-to-paper handoff checklist

- [ ] Input roles/stages/statuses were verified.
- [ ] Primary final-query counts match.
- [ ] Secondary T0 contains only R3 current-after-update.
- [ ] Analytics tests passed before analysis.
- [ ] Analysis config matches preregistration.
- [ ] Exactly five H1–H5 rows exist.
- [ ] Complete 37-cell H surface exists per primary model.
- [ ] Confidence-quality and reliability tables exist.
- [ ] H3/H4 policy diagnostics and contracts exist.
- [ ] Four H5 domain directions exist.
- [ ] CPR coverage, interval, set size, and fallback are present.
- [ ] R3 T0/T2 pairing count is correct.
- [ ] Error, cost, latency, and repeatability tables exist.
- [ ] All nine SVG figures were visually inspected.
- [ ] LaTeX tables compile.
- [ ] Analysis manifest hashes all assets.
- [ ] No test-dependent tuning occurred.
- [ ] Null, negative, unsupported, and non-confirmatory findings remain in the
  result package.

After this checklist is complete, use
`03_ICLR_PAPER_WRITING_AGENT_PROMPT.md` to produce the manuscript.
