# R7 protocol — confidence threshold and operating policy

## Status of R7

R7 is retained because it was in the original proposal, but it is not a query-complexity dimension. It is a secondary decision-policy stress suite applied after one uncertainty score has been collected per query. Confirmatory H3/H4 mixtures and hard groups come from R1–R6.

Never regenerate the model separately for every threshold. Generate and score once, then sweep thresholds post hoc.

## Testcase file and sample size

File: ../../testcases/r7_threshold_policy.jsonl

- 5,000 unique query worlds.
- Five difficulty profiles, 1,000 each:
  - easy known;
  - low frequency;
  - high precision;
  - stale unknown;
  - three-hop synthesis.
- Per profile: 400 fit, 150 tune, 200 calibrate, 250 test.
- Locked test total: 1,250.
- Threshold grid: 0.00 to 1.00 in steps of 0.01.

The 101 operating points are repeated policies on the same queries, not 126,250 independent observations. All intervals and comparisons cluster by query/world.

## Procedure

1. Generate one greedy answer and five samples per query.
2. Compute every uncertainty score.
3. Fit any declared calibration transform on fit; exact agreement remains the
   primary score.
4. Select score transformations and the finite policy grid on tune.
5. On calibrate, validate thresholds/rules using the selected risk-control procedure.
6. Lock the chosen configurations.
7. Apply all curves and the chosen policy to test.

Do not choose the final threshold by looking at test.

## Threshold semantics

Normalize confidence so larger means more likely correct.

For threshold \(\tau\):

\[
\text{commit if }s(q,a)\ge\tau;\quad\text{otherwise abstain}
\]

For set policies, threshold candidate inclusion or the conformal stopping rule as defined in the method.

## Metrics

The project-wide primary contract metric is false-commit risk per incoming query
at target 0.05 with calibration confidence 0.95. Answer coverage is primary
utility. The following R7 curves and selective quantities are secondary stress
diagnostics:

- selective risk:

\[
\#\text{wrong commits}/\#\text{commits}
\]

- answer coverage:

\[
\#\text{commits}/N
\]

- false-commit risk per incoming query;
- risk-coverage curve and AURC;
- answer coverage at false-commit targets 5%, 10%, and 20%, with 5% primary;
- worst-profile selective risk;
- cost-adjusted utility.

## Policy selection

Compare:

- naive fixed confidence values 0.5, 0.7, 0.9, 0.95, 0.99;
- threshold minimizing tune error;
- threshold maximizing tune utility;
- global risk-controlled threshold;
- profile-specific threshold;
- recent conditional/adaptive conformal method;
- CCRC.

Only call a policy “valid” for the precise risk proven or tested. Prediction-set coverage does not automatically establish selective-risk control.

## Statistical analysis

- Paired bootstrap by world for AURC and coverage-at-risk.
- Exact intervals at frozen operating points.
- Worst-profile gap with simultaneous multiplicity correction.
- Repeated calibration splits as stability analysis.
- Report unattainable target risk when no threshold answers enough examples.

Avoid picking the visually best point from a test curve and presenting it as a deployed policy.

## Utility

Predefine:

\[
U=\text{correct commit reward}
-c_w(\text{wrong commit})
-c_a(\text{abstention})
-c_g(\text{generation cost})
\]

Report multiple transparent cost settings rather than one arbitrary utility. Primary utility should remain answer coverage at the fixed 5% false-commit risk.

## Hypothesis relationship

- R7 stress-tests the mechanisms used in H3/H4 but supplies no confirmatory H3/H4 observations.
- Its shift-like profiles are illustrative stress cases, not confirmatory H5 domain-transfer data.

## Required output

- Risk-coverage curves for every scorer.
- Aggregate and worst-profile risk curves.
- Coverage at target-risk table.
- Threshold stability across calibration splits.
- Utility-validity-cost Pareto plot.
