# CalibRead paper analytics

This is the second, independent package. It reads the CSV artifacts produced by
`calibread_openrouter`, executes the frozen H1–H5 analyses, computes the full
R1–R7 reliability surface, calibrates CPR and risk-controlled read policies,
and produces vector figures plus CSV/LaTeX tables for an ICLR-style paper.

It deliberately uses only the Python standard library. The figures are native
SVG, so a clean machine can reproduce publication-quality vector assets without
NumPy, pandas, R, or a plotting backend.

## Setup and run

~~~shell
cd calibread_analytics
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
cp analysis_config.example.json analysis_config.json
~~~

For the two-checkpoint confirmatory study, copy
`analysis_config.parametric.example.json` instead; it already lists the primary
T2, secondary temporal T0, and both development R0 checkpoint-gate run
directories.

Edit `inputs`, `output_dir`, and optionally `primary_model_id`, then run:

~~~shell
calibread-analyze --config analysis_config.json
~~~

Confirmatory input directories must contain every runner artifact: raw, scored,
candidate, component-link, summary, observation-spec, redacted-config,
model-metadata, and scientific-bundle files. Preflight validates their types,
keys, counts, hashes, roles, stages, confidence method, returned route, and
coverage before creating scientific assets. Incomplete artifacts are permitted
only with the explicit exploratory flag; the entire analysis is then stamped
`NONCONFIRMATORY_INCOMPLETE_INPUT`. Multiple directories can combine
frozen stages/seeds/models. The primary model is used for H1–H5; descriptive
tables retain every model.

Rows with `analysis_role=primary` are the only rows admitted to H1–H5, the H
surface, calibration, contracts, and CPR. To obtain the R3 controlled-update
diagnostic, also supply the secondary T0 run described in the runner README.
Its `secondary_temporal` rows are used only for the paired T0/T2 table and
figure. Both checkpoint endpoints must share the preregistered
`model.analysis_id`; their actual endpoint IDs and stages remain in provenance.

## What H(θ,Q) means in this code

The primary hallucination index is:

~~~text
H_false_commit(theta, Q)
  = count(action == ANSWER and commit_correct == 0) / count(incoming queries)
~~~

This is false-commit risk per incoming query. It is not the bibliometric
h-index and is not wrong answers divided only by attempted answers. The latter
is exported separately as `H_selective`.

The effective action is ANSWER whenever either the declared action is ANSWER or
the response leaks a non-empty answer payload. This prevents malformed
`ABSTAIN`-with-answer outputs from escaping the false-commit numerator; for
schema-valid responses it is identical to the declared action.

For R4 ambiguity levels 2–4, a singleton ANSWER is a false commit even if the
string matches one plausible interpretation, because the operationally correct
action is CLARIFY. Every H cell includes a world-cluster bootstrap interval.

The generated `H_INDEX_AND_CONFIDENCE.md` contains the exact equations and text
that should be used in the methodology section.

## Confidence and CPR

The package keeps three concepts separate:

1. `raw_confidence_score`: an uncalibrated ordering score such as exact sampled
   agreement;
2. `c_point_estimate`: an isotonic correctness estimate fitted on fit/tune;
3. `policy_false_commit_risk_upper`: a simultaneous policy-level marginal risk
   bound computed on calibration data.

The Read-pair CSV also exports `estimated_error_probability=1-c_point_estimate`
and the explicit alias `c_policy_error_upper`. Only the latter is a formal bound,
and only at the policy-mixture level described below—not for one individual
answer.

The third value is not a posterior error probability for one answer. Its
complement is a policy-level lower bound on avoiding a false commit over the
declared query mixture; abstentions count as non-false-commits. It is not the
accuracy of committed answers. `individual_error_bound_available` is therefore
always zero.

CPR uses a frozen nested family consisting of top-k sampled answer clusters and
an all-answers (vacuous) fallback, on which the deployed system abstains.
Calibration chooses the smallest conformal rank cutoff at target `1-alpha`. If
the fallback is needed, the set is valid but vacuous; `fallback_rate` makes this
visible. The guarantee is marginal under exchangeability and applies to the
frozen candidate-generation mechanism. CPR is evaluated only on operationally
unique targets; R4 ambiguity levels 2–4 are excluded because they do not define
a single ground-truth answer label.

## Executed hypotheses

- **H1:** one-sided isotonic Bernoulli likelihood-ratio statistic with
  exposure-label permutation; the exposure-16 minus exposure-1 practical
  effect receives a fact-bootstrap lower bound.
- **H2:** graph-level error among depth-2–5 final questions whose complete set
  of R5 component probes was answered correctly. The independence product is
  not applied inside this conditioned subset.
- **H3:** an aggregate-only threshold is certified on calibration, then tested
  for aggregate validity and simultaneous failure over the 13 frozen hard
  groups.
- **H4:** deterministic query-rules CCRC and a global joint-safe policy must both pass
  the same aggregate-plus-13-group calibration gate before a paired world
  bootstrap tests a coverage gain above three points.
- **H5:** the maximum of four frozen cross-domain minus within-domain
  false-commit gaps is tested against the two-point margin.

One raw p-value from each hypothesis enters the five-way Holm correction.
Unsupported policies produce `UNSUPPORTED`; they are never replaced with a
least-bad threshold.

The H4 profile is inferred from query text only. The rule set in
`policy.inference_profile` must be frozen before opening the test split; it does
not inspect test answers, losses, factors, or suite labels. Profile-specific
penalties are learned on fit/tune only, thresholds are selected on calibrate,
and test is used once for the frozen comparison. `profile_assignment_audit.csv`
exports every predicted profile and penalty so this separation is auditable.

The equal-mixture aggregate gives equal total weight to R1–R6 and equal level
weight within each suite. Guarantees use an independent-world
cluster-weighted Hoeffding interval; exact binomial bounds are used only when
each world contributes one equal-weight row.

## Scientific-status guard

By default, H1–H5 are marked confirmatory only when every primary row has
`scientific_status=confirmatory_parametric`. Public OpenRouter zero-shot and
contextual-debug results still produce all diagnostic plots, but their
hypothesis decisions are `NOT_CONFIRMATORY`.

Do not disable this guard in a paper simply to obtain favorable hypothesis
labels.

## Generated assets

~~~text
paper_assets/<run>/
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
    clarification_recovery.csv
    confidence_feature_availability.csv
    r0_checkpoint_gate.csv
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
    cpr_subgroup_diagnostics.csv
    calibrated_read_pairs.csv
    table_hypotheses.tex
    table_main_metrics.tex
    policy_diagnostics.json
  suites/R1 ... suites/R7/
    metrics.csv
    hallucination_index.csv
    risk_coverage.csv
    linked_confirmatory_hypothesis.csv
  suites/R3/
    temporal_confusion.csv
    paired_update_effect.csv
~~~

The analysis manifest hashes every generated asset. Tables always retain
numerators/denominators in their source CSV, and every plot is regenerated from
those artifacts rather than hand-edited values.
