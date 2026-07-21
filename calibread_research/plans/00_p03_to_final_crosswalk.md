# P03-to-final protocol crosswalk

## Status and authority

This document records the scientifically necessary revision from the original
P03 concept to the executable six-month CalibRead study. The P03 HTML is the
archival proposal; this crosswalk, the master blueprint, and the preregistration
are the active protocol. If they conflict, the signed preregistration controls.

Protocol version: **CalibRead design v1.2**

## Final thesis goal

> Measure how the factual reliability of closed-book parametric reads changes
> across six controlled query/knowledge factors, audit when aggregate risk
> control hides hard-group failures, and evaluate whether a
> complexity-conditioned controller retains more useful answers under the same
> declared risk contract.

The contribution is a controlled benchmark, a conditional-reliability audit,
and a contract layer. It is not a claim to be the first conformal method for
LLM generation.

## Primary contract

The primary loss is **false-commit risk per incoming query**:

\[
L_{fc}=\mathbb 1\{D=\text{commit and the committed response is not
operationally correct}\}.
\]

The CalibRead design v1.2 target is:

- expected false-commit risk \(r^\star=0.05\);
- calibration confidence \(1-\delta=0.95\);
- primary utility: answer coverage;
- secondary outcomes: selective risk, set miscoverage, set size, action
  accuracy, and compute.

The fit/tune pilot may justify a v1.2 amendment to sample sizes or minimum
practical effects before the week-6 signed preregistration, but the primary
loss, 0.05 target, 0.95 calibration confidence, and answer-coverage utility are
fixed. Any later change is a dated deviation and loses confirmatory status. A
certificate never means that an individual answer has a 95% posterior
probability of being true.

## Output and action mapping

The base read prompt emits:

- `ANSWER` → `commit`;
- `ABSTAIN` → `abstain`;
- `CLARIFY` → `clarify`;
- `REJECT_PREMISE` → `reject`.

Candidate answer sets are assembled by the external controller from frozen
sampled candidates; the base model is not required to serialize a set. Reject,
clarify, and abstain are non-commit actions for the primary false-commit loss,
but each also receives a separate action-correctness label.

`commit_correct` requires both correct content and a uniquely valid singleton
under the query contract. Thus any R4 level-2–4 singleton `ANSWER` has
`commit_correct=false`, even when its text is one plausible office-specific
role.

## Experimental suite terminology

- **R0:** baseline, negative, and infrastructure controls.
- **R1–R6:** six query/knowledge complexity factors.
- **R7:** policy-operating stress suite; not a seventh complexity factor and
  not part of the primary R1–R6 mixture.

Primary cross-suite analyses use a declared mixture that gives each of R1–R6
equal total weight and each level equal weight within its suite. R7 is reported
separately as a policy stress test.

## Original-to-final hypothesis crosswalk

| Original P03 hypothesis | Final status | Reason |
|---|---|---|
| H1 universal normalized frequency threshold | Replaced by final H1 exposure effect | A universal threshold is unsupported; exact exposure and model interaction remain. |
| H2 multiplicative compounding as expected truth | Split into final H2 plus a secondary independence analysis | Independence is a falsifiable reference model, not an assumption. |
| H3 CPR set size ≤3 and >30% efficiency | Removed as confirmatory | The constants lack pilot support and closely related conformal methods already exist. Set validity/size remain secondary outcomes. |
| H4 within-domain but not cross-domain transfer | Final H5 | Preserved, generalized, and renumbered. |
| H5 optimal CPR abstention | Final H4 and R7 | “Optimal” is undefined without a cost and policy class; the final study compares utility at equal validated risk. |

## Final confirmatory hypotheses and one-result rules

### H1 — exposure-frequency reliability

Accuracy improves monotonically with log exposure count after prespecified
controls.

- Primary result: for the model named in `primary_model_id` before test access,
  a one-sided monotone step-spline logistic likelihood-ratio statistic with
  exposure labels permuted at the fact-cluster level. This is the executable
  isotonic Bernoulli test in `calibread_analytics`; other model sizes and
  exposure-by-model interactions are secondary.
- Practical support: the lower 95% interval for the accuracy difference between
  exposure 1 and exposure 16 exceeds 5 percentage points.
- Model-scale interaction and change-point estimates are prespecified
  secondary analyses.

### H2 — synthesis failure despite component availability

Among graphs whose required component questions are all answered correctly,
the final composition error exceeds a practically meaningful rate.

- Primary endpoint: conditional composition-error rate over depths 2–5.
- Primary result: one graph-clustered one-sided test of the pooled conditional
  composition-error rate over depths 2–5 against a 5% practical floor.
- Depth-specific estimates and simultaneous intervals are secondary.
- Secondary independence analysis: on **all** graphs, compare final success
  with the product of cross-fitted per-component success probabilities. Do not
  apply the multiplicative formula after conditioning on observed component
  success.

### H3 — aggregate validity hides hard-group failure

A frozen **aggregate-only global policy** passes the aggregate 5% false-commit
contract while at least one prespecified R1–R6 hard group exceeds it
materially. This diagnostic policy is distinct from H4's joint-safe global
baseline.

The authoritative 13-group membership list is in
`02_hypothesis_execution_plan.md`; R7 profiles and intersections are excluded.

- Aggregate gate: one-sided upper confidence bound is at most 0.05.
- Group endpoint: worst-group false-commit gap.
- Group violation: a simultaneous lower bound exceeds 0.05 by the frozen
  practical margin of 2 percentage points.
- One Holm-family result: multiplicity-adjusted maximum-group test, evaluated
  only if the aggregate gate passes.

### H4 — deployable complexity conditioning improves utility

Among policies that pass the same **joint** 5% false-commit contract—aggregate
plus all 13 hard groups under one simultaneous procedure—predicted-profile CCRC
retains more answers than a single global joint-safe policy.

- Validity is a gate; invalid or unsupported policies are not compared for
  superiority.
- The global baseline uses one policy for every query but is calibrated against
  the full joint family. It is not H3's aggregate-only diagnostic policy.
- Primary endpoint: paired answer-coverage difference on R1–R6.
- Minimum useful gain: 3 percentage points.
- One Holm-family result: paired world-cluster superiority test after the
  validity gate.
- The deployable profile is the frozen deterministic query-only rule
  query_rules_v1.1. A trained profiler and ground-truth oracle are omitted
  under the protocol-v1.2 scope decision.

### H5 — asymmetric cross-domain transfer degradation

At least one prespecified cross-domain direction has a materially larger
absolute false-commit target gap than within-target-domain calibration.

- Primary endpoint: maximum of the four prespecified cross-minus-within target
  gap differences.
- One Holm-family result: simultaneous/max-statistic test over the four
  directions with a 2-point practical margin.
- Continuous embedding/perplexity shift features are future secondary work
  under protocol v1.2 and are not required or claimed by H5.

## Multiplicity

Each final hypothesis produces one primary p-value or equivalent one-sided
decision statistic. Apply Holm correction across H1–H5. Planned within-H3 and
within-H5 multiplicity is handled by simultaneous/max-statistic procedures
before the five-way Holm correction. H2's depth-specific results are secondary.

## Interaction scope

Frequency × depth and ambiguity × depth are optional stretch analyses. They are
not confirmatory, not required for thesis completion, and must not be described
as part of the 70,000-record core suite unless separately generated and
preregistered before test access.
