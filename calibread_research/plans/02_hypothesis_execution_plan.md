# Hypothesis-by-hypothesis execution plan

## General rules

- Five confirmatory hypotheses.
- One primary endpoint per hypothesis.
- Nulls, exclusions, models, and tests frozen before locked test evaluation.
- Holm correction across H1–H5.
- The confirmatory mixture gives equal total weight to R1–R6 and equal level weight within each suite. R7 is a separate policy stress suite.
- All factor interactions are optional exploratory extensions outside the 70,000-record core.
- Effect sizes and confidence intervals are primary; corrected p-values are secondary.
- Each hypothesis contributes exactly one result to the Holm family, as specified below.

---

## H1 — exposure-frequency reliability

### Claim

Accuracy has a positive monotone association with log exposure count under the fixed exposure assignment and unified training schedule.

### Null

After controls, exposure count has no positive monotone association with correctness.

### Data

- Primary: R1.
- Gate/control: R0.
- External observational validation: natural long-tail dataset if added.

### Inclusion

- all R1 locked-test cases;
- all prespecified models that pass R0;
- all training seeds completed before test opening.

### Exclusion

- corrupt/missing generation;
- parser failure caused by infrastructure, reported separately;
- duplicate testcase ID;
- model run not matching the frozen manifest.

Do not exclude wrong formatting answers from factual error unless the read API contract explicitly allows repair.

### Primary endpoint

Binary exact factual retrieval correctness: an exact committed answer is 1;
wrong answers, abstentions, clarifications, rejections, and malformed outputs
are 0. Correct abstention at exposure 0 remains a separate action endpoint and
does not count as successful fact retrieval for H1.

### Primary model

Before locked-test access, select the controlled model in
`analysis_config.primary_model_id`. Fit a monotone step-spline logistic curve
over the seven ordered exposure levels (the Bernoulli isotonic MLE), compare it
with a constant-rate null using a likelihood-ratio statistic, and obtain the
one-sided p-value by permuting the fixed exposure labels at the fact-cluster
level while preserving the seven cell counts. This executable monotonicity
omnibus is H1's single Holm-family result. Training-seed repetitions for the
same fact stay in the same cluster. Model-scale interaction and a smoother
mixed-logistic curve are secondary sensitivity analyses.

### Practical-effect check

The lower 95% graph/fact-cluster bootstrap confidence bound for accuracy at exposure 16 minus accuracy at exposure 1 must exceed 5 percentage points. This is a prespecified interpretation threshold, not a second Holm test.

### Secondary analyses

- exposure × model-scale interaction and segmented change point;
- Brier and AURC curves;
- false commits at exposure zero;
- answer coverage under the primary 5% false-commit contract.

### Falsification

H1 is not supported if:

- the one-sided monotone omnibus result is not significant after Holm correction;
- the practical-effect interval does not clear 5 percentage points;
- direction reverses persistently;
- apparent effect disappears after seed or token-length controls.

### Required figure/table

- failure curve by exposure and model;
- exposure thresholds at selected accuracy levels, only when identifiable;
- coefficient/interaction table.

### Week checkpoints

- Week 5: injection pilot.
- Week 17: main controlled model training.
- Week 18: R1 development-side generation and grading.
- Week 23: locked analysis.

---

## H2 — conditional synthesis penalty

### Claim

Even when every supporting component question is answered correctly, multihop final-answer error remains above a prespecified 5% practical floor.

### Null

Conditional multihop final-answer error is at most 5%.

### Data

- Primary: R5.
- Supporting: component_queries stored in every R5 record.

### Inclusion

- locked graphs;
- primary subset: all required component questions correct for the evaluated depth.

### Primary endpoint

Multihop error among graph-depth observations for which all required component
probes receive exact committed answers, summarized across preregistered depths
2–5. Final wrong answers, non-answer actions, and malformed outputs are errors.
The one-sided test against 5% is H2's single Holm-family result.

### Test

- one-sided graph-cluster bootstrap or graph-clustered score test against the 5% floor;
- depth-specific simultaneous intervals and a mixed logistic depth model as supporting analyses.

### Required sensitivity analyses

- on all graphs, estimate component-success probabilities by cross-fitting that excludes the evaluated graph, then compare observed multihop error with \(1-\prod_j\widehat p_{j,-g}\);
- answer-only versus structured-path prompt;
- control for question token length;
- use per-component empirical probabilities rather than one pooled \(H_1\).

### Falsification

H2 is not supported if the one-sided conditional-error result does not reject the 5% floor after Holm correction.

### Interpretation restrictions

- Positive residual does not prove a particular internal reasoning mechanism.
- Component probe success does not prove the model used that fact internally.
- Results concern behavioral composition only.
- Never apply the independence-product formula after conditioning on all component answers being correct; that would mix two different estimands.

### Required output

- conditional composition-error estimate and interval;
- secondary all-graphs observed versus cross-fitted independence-predicted curve;
- conditional versus unconditional accuracy;
- first-failed-hop distribution.

---

## H3 — marginal validity hides group failure

### Claim

A globally calibrated policy can meet aggregate false-commit risk while violating the same target for a preregistered hard group.

### Null

Whenever the aggregate 5% false-commit target is met, every preregistered group remains at or below 7% under the simultaneous procedure.

### Data

The confirmatory hard-group list is fixed as:

| Group ID | Membership |
|---|---|
| `r1_low_exposure` | R1 exposure 0, 1, or 2 |
| `r2_exact_date` | R2 `exact_date` |
| `r2_decimal_5` | R2 `decimal_5` |
| `r3_superseded_stale` | R3 `superseded_stale` |
| `r3_post_cutoff_unknown` | R3 `post_cutoff_unknown` |
| `r4_interpretations_3` | R4 `interpretations_3` |
| `r4_interpretations_4` | R4 `interpretations_4` |
| `r5_hops_4` | R5 `hops_4` |
| `r5_hops_5` | R5 `hops_5` |
| `r6_general` | R6 `general` |
| `r6_biomedical` | R6 `biomedical` |
| `r6_legal` | R6 `legal` |
| `r6_technical` | R6 `technical` |

Every listed group has at least 400 calibration and 500 test independent units;
the pooled R1 group has 600 and 750 respectively.

R7 hard profiles are a secondary stress evaluation and do not define confirmatory groups.

### Primary policy

Aggregate-only global policy calibrated on the declared mixture. It is not the
joint-safe global baseline used in H4.

### Primary endpoint

Maximum hard-group false-commit excess:

\[
\max_{g\in\mathcal G}(\hat R_{\mathrm{fc},g}-0.05)
\]

This maximum, evaluated with a simultaneous interval, is H3's single Holm-family result. The global aggregate contract must first pass with an upper 95% confidence bound at most 0.05.

### Tests

- simultaneous group intervals;
- multiplicity correction over the preregistered group list;
- exact binomial/cluster bootstrap depending on loss;
- development-only repeated fit/tune/calibrate stability as appendix; the sealed test is never repartitioned.

### Success condition

The aggregate upper 95% bound is at most 0.05 and the simultaneous lower bound for the maximum group risk exceeds 0.07, the target plus the prespecified 2-point margin.

### Falsification

No aggregate/group divergence, or divergence appears only in an exploratory tiny intersection.

### Required output

- aggregate target line with group points;
- worst-group table;
- heatmap over factor levels.

---

## H4 — complexity-conditioned utility

### Claim

Among policies passing the same joint false-commit contract, predicted-profile CCRC retains more answers than a single global joint-safe policy.

### Null

After the common validity gate, the predicted-profile CCRC answer-coverage gain over the global joint-safe baseline is at most 3 percentage points.

### Data

- primary: R1–R6 calibration/test data under the equal-suite/equal-level mixture;
- R7: secondary policy stress data;
- profiles predicted only from information available at inference time are primary;
- ground-truth factor profiles are omitted under protocol v1.2.

### Primary endpoint

Paired answer-coverage difference at false-commit target 0.05 and calibration confidence 0.95. This paired difference is H4's single Holm-family result. The meaningful-improvement threshold is 3 percentage points.

Both policies must be supported under one joint family containing the aggregate
mixture and all 13 H3 hard groups. The global baseline applies one policy to all
queries but is calibrated against that joint family; it is deliberately more
conservative than H3's aggregate-only diagnostic policy.

### Comparison

- global risk-controlled policy;
- recent continuous adaptive/conditional method;
- CCRC.

### Test

- both policies must pass the same prespecified simultaneous aggregate-plus-13-group false-commit validity gate first;
- one-sided paired world-cluster bootstrap test of coverage gain against the 3-point margin second;
- if no method passes risk, report infeasible rather than compare invalid policies.

### Ablations

- no complexity features;
- each factor removed;
- deterministic query-only profile assignment audit;
- global versus domain-only versus full hierarchy;
- calibration sample size.

### Falsification

- CCRC fails risk;
- utility interval includes a practically negligible gain;
- benefit disappears with predicted profiles;
- benefit is due only to much higher generation cost.

### Required output

- validity/utility Pareto frontier;
- answer-coverage gain table;
- compute-normalized comparison.

---

## H5 — calibration transfer under domain shift

### Claim

At least one prespecified cross-domain calibration direction degrades false-commit reliability by more than 2 percentage points compared with within-target calibration.

### Null

All four cross-minus-within target gaps are at most the preregistered 2-percentage-point margin.

### Data

- Primary controlled: R6.
- Secondary temporal stress: R3.
- External observational validation: selected natural-domain datasets.

### Primary endpoint

The maximum of the four cross-minus-within false-commit target gaps. Its simultaneous one-sided interval/test is H5's single Holm-family result.

### Primary comparisons

Freeze four:

- general → biomedical;
- general → legal;
- biomedical → general;
- legal → technical.

These directions are fixed before calibration and test access. Any fit/tune-only amendment must be dated and preregistered before the final calibration run.

For direction \(s\rightarrow t\), define degradation as
\(D_{s,t}=R_{fc}^{s\rightarrow t}-R_{fc}^{t\rightarrow t}\). The 0.05 target
cancels algebraically, but both constituent target gaps must still be reported.

### Superseded secondary model (not executed in protocol v1.2)

The following historical regression is retained only to document the earlier
roadmap. Protocol v1.2 does not fit or report it. H5 is the categorical
four-direction maximum-gap test, and continuous shift explanations are future
work.

Hierarchical regression:

\[
|\text{gap}_{s,t}|
=
\beta_0+\beta_1\text{embedShift}_{s,t}
+\beta_2\text{perplexityShift}_{s,t}
+u_s+v_t
\]

Here `gap` is the signed/absolute transfer gap as explicitly labeled in each
secondary regression. The small number of domain pairs limits strong causal
interpretation. Treat the shift-feature regression as secondary; it is not part
of H5's Holm-family result.

### Adaptation comparison

- unchanged global calibration;
- domain-specific calibration;
- importance weighting;
- small target sample recalibration;
- CCRC fallback.

### Falsification

- all transfer directions stay within margin;
- only natural/confounded data show degradation.

No continuous shift-feature claim is made in protocol v1.2.

### Required output

- transfer heatmap;
- target-label sample-size recovery curve.

---

## Decision table after analysis

| Result pattern | Paper interpretation |
|---|---|
| H1–H3 supported, H4 weak | strong benchmark/measurement paper |
| H3–H4 supported | method plus benchmark paper |
| H5 supported strongly | reliability-under-shift emphasis |
| Only H1/H2 supported | causal complexity/failure-surface paper |
| Most null | report feasibility boundaries, scorer limits, and high-quality artifact; do not manufacture novelty |
