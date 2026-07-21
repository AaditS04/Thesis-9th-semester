# Prompt for an agent to write the CalibRead ICLR-level paper

Document ID: `CALIBREAD-PROMPT-PAPER-001`  
Use only after the test and analysis SOPs are complete and the paper-asset
directory is immutable.

## How to use this file

Give the following prompt to the writing agent. Replace angle-bracket
placeholders with the real paths if they differ from the defaults. Do not remove
the scientific claim restrictions.

---

## Copy-paste agent prompt

You are the primary research-writing agent for an anonymous ICLR submission.
Your task is to write a rigorous, reproducible paper from the completed
CalibRead experiment. You must inspect the local research design, executable
code, accepted result CSVs, figures, and bibliography before drafting. Do not
invent a number, citation, experiment, baseline, ablation, guarantee, or result.

### Project identity

Working title:

> CalibRead: Parametric Complexity Analysis of Probabilistic Read Reliability
> in LLM Knowledge Systems

Core question:

> How does the reliability of an LLM parametric Read operation vary with
> controlled query/knowledge complexity, and what marginal or policy-level
> reliability guarantees can be supplied without pretending to have an
> individual posterior error bound?

Workspace root:

`/Users/aadit.shah@zomato.com/Documents/thesis`

Primary paper assets:

`<PAPER_ASSET_DIR>`

Default expected path:

`/Users/aadit.shah@zomato.com/Documents/thesis/calibread_analytics/paper_assets/calibread_parametric_001`

Primary T2 runner directory:

`<PRIMARY_T2_RUN_DIR>`

Secondary temporal T0 runner directory:

`<SECONDARY_T0_RUN_DIR>`

### Mandatory work sequence

Do not start prose immediately. Complete these phases in order.

#### Phase 1 — verify inputs

Confirm that every required path exists. If the paper-asset directory or
primary result tables are absent, stop and report exactly what is missing.

Read these research/design documents completely:

1. `CalibRead_research_blueprint.md`
2. `calibread_research/plans/00_p03_to_final_crosswalk.md`
3. `calibread_research/plans/00_master_execution_index.md`
4. `calibread_research/plans/01_sample_size_and_power_plan.md`
5. `calibread_research/plans/02_hypothesis_execution_plan.md`
6. `calibread_research/plans/03_results_collection_and_analysis_plan.md`
7. `calibread_research/plans/05_complete_research_paper_plan.md`
8. `calibread_research/plans/06_operational_runbook_and_data_dictionary.md`
9. `calibread_research/plans/07_preregistration_template.md`
10. `calibread_research/plans/08_unified_training_and_checkpoint_plan.md`
11. every R1–R7 protocol under `calibread_research/plans/dimensions/`
12. `calibread_analytics/PAPER_CLAIM_GUARDRAILS.md`
13. `calibread_analytics/README.md`
14. `calibread_openrouter/README.md`
15. `calibread_research/operating_protocols/04_TESTING_CODE_LOGIC_AND_H_INTERPRETATION.md`

Read these executable modules sufficiently to verify the Methods description:

- runner: `config.py`, `prompting.py`, `parsing.py`, `grading.py`, `tasks.py`,
  `uncertainty.py`, `client.py`, and `runner.py`;
- analytics: `metrics.py`, `stats.py`, `policy.py`, `cpr.py`,
  `hypotheses.py`, `diagnostics.py`, `analysis.py`, and `plots.py`.

Do not manually rewrite code behavior from memory. Cite the actual implementation
and the generated methodology note.

Read every generated artifact in `<PAPER_ASSET_DIR>`, including:

- `H_INDEX_AND_CONFIDENCE.md`;
- `PAPER_ASSET_REPORT.md`;
- `analysis_manifest.json`;
- every CSV in `tables/`;
- every per-suite CSV in `suites/R1` through `suites/R7`;
- every SVG in `figures/`;
- both generated TeX tables.

Read accepted redacted configs, model metadata, run summaries, and checkpoint
manifests from both runner directories. You may inspect raw generations only
for targeted examples or audits; do not use raw test outputs to create an
unpreregistered selection rule.

Read the bibliography sources:

- `calibread_research/references/ANNOTATED_BIBLIOGRAPHY.md`;
- `calibread_research/references/calibread_references.bib`.

#### Phase 2 — create a result ledger

Before drafting the paper, create `calibread_paper/RESULTS_LEDGER.md`. For every
number that might appear in the paper, record:

- proposed statement;
- exact numerical value;
- uncertainty interval and confidence level, if any;
- numerator and denominator where applicable;
- model/analysis ID;
- suite, level, split, and checkpoint role;
- source CSV filename;
- row identifier or filtering rule;
- whether the result is confirmatory, secondary, diagnostic, or exploratory;
- whether multiplicity correction applies;
- any caveat required beside the number.

At minimum include:

- H1–H5 effect estimates, raw p-values, Holm p-values, margins, and decisions;
- all 37 H cells for the primary model, with main-text cells identified;
- answer coverage and selective risk beside H;
- aggregate and hard-group contract bounds;
- H4 coverage comparison;
- all four H5 transfer directions;
- CPR target/empirical coverage, interval, cutoff, set size, and fallback rate;
- aggregate and per-suite confidence metrics;
- R3 paired T0/T2 current and stale effects;
- repeatability, cost, and latency;
- error-taxonomy counts and denominators.

Do not round values in the ledger. Decide paper rounding only after the ledger
is verified.

#### Phase 3 — create a claim-evidence matrix

Create `calibread_paper/CLAIM_EVIDENCE_MATRIX.md` with columns:

```text
claim_id | proposed_claim | evidence_artifact | result_status |
estimand | population | assumptions | allowed_wording | forbidden_wording
```

Every Abstract, Introduction contribution, and Conclusion claim must appear in
this matrix. A claim with no direct artifact must be removed or labeled as
motivation/future work.

#### Phase 4 — plan the paper

Create `calibread_paper/PAPER_OUTLINE.md` containing:

- one-sentence thesis;
- three to five contribution bullets;
- section hierarchy;
- figure/table placement;
- expected evidence in every subsection;
- appendix map;
- space/page-budget priorities based on the supplied ICLR template.

If no official ICLR template is present locally, write a complete content draft
without claiming compliance with a specific current page limit. Do not download
or install a template unless authorized.

#### Phase 5 — write the manuscript

If a local ICLR LaTeX template exists, create a compilable paper under
`calibread_paper/`. Otherwise create `calibread_paper/main.md` plus separate
section files and a LaTeX-ready outline. Preserve anonymous submission status.

Required manuscript structure:

1. Abstract
2. Introduction
3. Related Work
4. Problem Formulation
5. CalibRead Benchmark Design
6. Confidence and Conformal Parametric Read
7. Experimental Protocol
8. Results
9. Diagnostics and Error Analysis
10. Limitations and Validity Scope
11. Broader Impact / Ethics as required by the venue
12. Conclusion
13. Reproducibility statement/checklist
14. Appendices

### Exact conceptual distinctions to preserve

#### Six complexity factors, not seven causal factors

R1–R6 are controlled complexity factors:

1. exposure frequency;
2. required precision;
3. temporal availability/update state;
4. ambiguity;
5. synthesis depth;
6. domain specificity/shift.

R7 is a threshold-policy stress suite. It is not a seventh independently
randomized cause. R0 is a control/gating suite outside the R1–R6 aggregate.

Forbidden wording:

> seven independently controlled complexity dimensions

Allowed wording:

> six controlled complexity factors and a separate threshold-policy stress
> suite

#### H is a false-commit surface

Define the primary index exactly as:

\[
H_{fc}(\theta,Q)=\frac{1}{|Q_\theta|}\sum_{i\in Q_\theta}
\mathbf 1\{D_i^{\mathrm{eff}}=\mathrm{ANSWER}\land C_i=0\}.
\]

Explain:

- denominator is incoming queries, not attempted answers;
- `D_eff=ANSWER` includes a declared ANSWER or a substantive leaked answer
  payload;
- `C_i` is operational commit correctness;
- R4 singleton answers at ambiguity levels 2–4 are false commits even if they
  match one possible interpretation;
- world-cluster intervals accompany each H cell;
- answer coverage and selective H must be shown beside H.

Do not call this the bibliometric h-index.

#### The Read output and c

The exported Read record distinguishes:

- raw confidence score;
- isotonic correctness point estimate;
- descriptive estimated error probability;
- policy-level false-commit risk upper bound;
- CPR answer set with marginal coverage.

Never write that standard split conformal prediction supplies a posterior bound
on the probability that one particular answer is wrong. The code explicitly
sets `individual_error_bound_available=0`.

Recommended wording:

> CalibRead returns an answer with a calibrated score and an explicit
> policy-level reliability certificate. CPR constructs answer sets with
> finite-sample marginal coverage under exchangeability.

#### CPR guarantee and minimality

State:

\[
\Pr\{Y_{new}\in S(X_{new})\}\ge 1-\alpha
\]

under exchangeability for the frozen candidate-generation mechanism.

CPR selects the smallest certified set only within a prespecified nested family
of sampled top-k answer clusters plus an all-answers vacuous fallback. It does
not prove globally minimum set size. The system abstains on the vacuous
fallback, whose rate must be reported.

CPR excludes R4 ambiguity levels 2–4 because no single ground-truth label is
defined.

#### Primary versus secondary checkpoint rows

All primary benchmark/hypothesis results use final T2 checkpoint rows. T0
`current_after_update` rows are secondary paired diagnostics only. Do not pool
T0 rows into the primary H surface.

#### Scientific status

If the primary rows do not all carry `confirmatory_parametric`, describe the
study as non-confirmatory diagnostics and do not present H1–H5 as confirmatory.
Do not suppress the status guard.

### Required H1–H5 descriptions

#### H1

- R1 locked test;
- operational committed retrieval outcome;
- one-sided isotonic Bernoulli likelihood-ratio statistic;
- exposure-label permutation at the fact/world level;
- practical exposure-16 minus exposure-1 gain with one-sided 95% bootstrap
  lower bound above five percentage points;
- one p-value in the Holm family.

Do not claim a universal memorization threshold.

#### H2

- R5 depths 2–5;
- condition on every required component probe being correct;
- graph/world-cluster analysis;
- final composition error tested against a 5% floor;
- independence-product analysis is a separate diagnostic, not primary H2.

If supported, describe it as evidence of composition failure even when direct
facts are available.

#### H3

- threshold selected for aggregate risk on calibrate;
- evaluated on test aggregate and 13 frozen hard groups;
- simultaneous bounds;
- endpoint is worst hard-group excess beyond aggregate target;
- supported H3 is a subgroup-failure finding, not a safety success.

#### H4

- compare global joint-safe policy with query-predicted-profile CCRC;
- profile rules use query text only;
- penalties fit on fit/tune;
- threshold selected on calibrate;
- both policies pass the same 14-scope gate;
- test comparison is paired by world;
- practical coverage-gain margin is three percentage points.

If either policy is unsupported, report that rather than inventing a fallback
threshold.

#### H5

- four frozen source-to-target domain directions;
- compare transferred calibration with within-target calibration;
- paired target-query loss gap;
- simultaneous direction control;
- practical degradation margin is two percentage points;
- supported H5 is a transfer-fragility finding.

#### Multiplicity

Exactly one p-value from each H1–H5 enters five-way Holm correction. Report raw
and adjusted p-values. Within-hypothesis direction/group multiplicity remains
separately controlled as implemented.

### Required benchmark-design details

Describe:

- 70,000 total R0–R7 records;
- 62,000 R1–R7 primary benchmark records;
- fit/tune/calibrate/test world-level partitioning;
- locked-test final-query total;
- unified knowledge corpus and exposure assignment;
- T0 initial storage and T2 controlled update;
- answer morphology and paired-world controls where implemented;
- deterministic suite-aware grading;
- R4 simulated clarification turns;
- deduplicated R5 component probes;
- stochastic generations as uncertainty samples, never independent testcases;
- repeated same-seed greedy subset for systems nondeterminism;
- provider/model/prompt/config/checkpoint provenance.

### Required results presentation

The Results section must lead with findings, not implementation chronology.
Use the result ledger to decide exact statements.

At minimum include:

1. primary H surface across R1–R6;
2. H1 exposure curve and practical contrast;
3. H2 conditional composition failure/success;
4. H3 aggregate-versus-hard-group contracts;
5. H4 global versus CCRC coverage at common safety scope;
6. H5 domain transfer matrix;
7. CPR coverage–set-size–fallback operating point;
8. confidence quality and risk–coverage;
9. R3 paired checkpoint update effect;
10. error taxonomy and repeatability.

For every headline H value show or cross-reference answer coverage. For every
certificate state the population, loss, mixture, confidence level, and
calibration split.

### Figure and table mapping

Use or adapt only presentation aspects of these generated assets; do not change
their numerical content:

- `fig_h_complexity.svg` — main complexity surface;
- `fig_risk_coverage.svg` — selectivity;
- `fig_calibration.svg` — reliability;
- `fig_hard_groups.svg` — H3 hard groups;
- `fig_domain_transfer.svg` — H5;
- `fig_cpr.svg` — CPR;
- `fig_hypotheses.svg` — hypothesis summary;
- `fig_error_taxonomy.svg` — diagnostics;
- `fig_r3_update_effect.svg` — temporal update;
- `table_hypotheses.tex`;
- `table_main_metrics.tex`.

Every caption must be self-contained and define abbreviations, denominator,
split, interval type, model/checkpoint, and direction of better/worse.

### Statistical reporting rules

- Report estimates with intervals, not p-values alone.
- Report numerator/denominator for central binary risks.
- State whether an interval is bootstrap, exact binomial, or
  independent-world cluster-weighted Hoeffding.
- State clustering unit.
- Report raw and Holm-adjusted p-values.
- Use percentage points for absolute probability differences.
- Use consistent rounding; retain more precision in tables than prose when
  useful.
- Do not use “significant” without naming the test and multiplicity control.
- Do not infer absence of effect from a nonsignificant result.
- Do not claim causality beyond randomized/controlled factors and the declared
  training design.
- Do not hide vacuous coverage, unsupported policies, empty groups, or missing
  metadata.

### Related-work requirements

Use the supplied `.bib` and annotated bibliography. Cover at least:

- hallucination/factuality benchmarks;
- abstention and selective prediction;
- optional availability-labelled P(True) and token-based confidence;
- calibration and ECE limitations;
- exact-answer entropy/self-consistency, explicitly not semantic entropy;
- conformal prediction and conformal risk control;
- knowledge editing, model memory, temporal knowledge, and parametric storage;
- multihop reasoning and compositional failure;
- domain shift;
- inference nondeterminism and batch/backend effects.

Do not cite Fxis as evidence of batch-invariant deterministic inference. Follow
the bibliography’s recorded decision about that repository.

Never fabricate BibTeX metadata. If a claim lacks a verified reference, mark it
`[CITATION NEEDED]` in the draft and report it in the handoff.

### Narrative discipline for all possible outcomes

Do not force a positive story. Select the narrative from the actual result
pattern:

- H1 supported: controlled exposure–reliability structure;
- H2 supported: composition failure beyond direct fact availability;
- H3 supported: scalar aggregate calibration hides group failure;
- H4 supported: complexity-conditional control improves safe coverage;
- H5 supported: domain-transfer fragility;
- unsupported policy: certification feasibility/coverage limitation;
- null hypothesis: boundary of the proposed mechanism;
- high CPR fallback: coverage is obtained vacuously and utility is limited;
- non-confirmatory status: benchmark/pipeline evidence only.

The paper can be strong with mixed or negative results if the estimands and
diagnostics are rigorous.

### Required limitations

Discuss at least:

- synthetic knowledge and ecological validity;
- checkpoint training dependence;
- model/provider coverage;
- exchangeability assumptions;
- marginal rather than individual CPR coverage;
- fixed candidate mechanism and family-relative minimality;
- group/mix dependence of risk contracts;
- ambiguity labeling and unique-target restriction;
- exposure count as a controlled proxy rather than universal memory strength;
- finite domains and temporal interventions;
- query-text profile heuristic;
- deterministic grader scope and human-audit requirements;
- backend nondeterminism and incomplete fingerprint metadata;
- compute/API cost and reproducibility constraints.

### Anonymity and tone

- Keep author identity anonymous.
- Remove local usernames, company email addresses, private endpoints, API keys,
  and internal paths from manuscript prose and supplementary material.
- Use precise, restrained language.
- Avoid marketing words such as “revolutionary”, “guaranteed safe”, “solves
  hallucination”, or “human-level”.
- Prefer active voice and short technical sentences.
- Define all notation once and reuse it consistently.

### Reproducibility appendix

Include:

- run/config/checkpoint/testcase/analysis hashes;
- software and Python versions;
- exact split counts;
- prompts and response schema;
- model/provider controls;
- generation and repeatability settings;
- grader definitions;
- H formula;
- hard groups and aggregate mixture;
- threshold grid;
- all H1–H5 formulas/margins;
- CPR algorithm and fallback;
- full confidence metric definitions;
- complete null/unsupported result table;
- cost and latency;
- deviations, if any.

### Final quality-control phase

Before declaring completion:

1. Recheck every manuscript number against `RESULTS_LEDGER.md`.
2. Recheck every major claim against `CLAIM_EVIDENCE_MATRIX.md`.
3. Search for forbidden claims:
   - seven independent factors;
   - individual conformal posterior guarantee;
   - global minimum set size;
   - public model called parametric-confirmatory;
   - T0 rows pooled into primary analysis;
   - H called wrong answers per attempted answer;
   - H3/H5 failure evidence described as model success.
4. Confirm all five hypotheses are reported regardless of outcome.
5. Confirm CPR fallback rate is beside coverage.
6. Confirm answer coverage is beside H.
7. Confirm all citations resolve in the supplied `.bib`.
8. Compile LaTeX if a template exists and fix all warnings that affect content,
   references, tables, or figures.
9. Produce `calibread_paper/FINAL_PAPER_AUDIT.md` listing:
   - files created;
   - unresolved placeholders;
   - missing citations;
   - deviations;
   - claims intentionally weakened;
   - compilation status;
   - final figure/table inventory.

### Required deliverables

Create at least:

```text
calibread_paper/
  RESULTS_LEDGER.md
  CLAIM_EVIDENCE_MATRIX.md
  PAPER_OUTLINE.md
  main.tex or main.md
  sections/
  figures/ or figure references
  tables/ or table references
  references.bib
  appendix/
  FINAL_PAPER_AUDIT.md
```

Do not declare the paper complete while placeholders such as `TBD`, `XX`,
`[CITATION NEEDED]`, invented numbers, unresolved paths, or missing hypothesis
rows remain. If an input is genuinely missing, stop and list the exact blocker
instead of filling it with a plausible value.

---

## End of agent prompt

The writing agent’s result ledger and claim matrix should be independently
checked against the analysis manifest before submission.
