# R3 protocol — temporal availability, supersession, and freshness

## Scientific question

Can a parametric read distinguish a current stored fact from a stale fact or a fact that was never written?

This protocol does not interpret the passage of calendar time as memory decay. It separates storage state and external truth.

## Testcase file and sample size

File: ../../testcases/r3_temporal.jsonl

- 8,000 records.
- Four temporal states, 2,000 each:
  - stable pre-cutoff;
  - superseded but model contains only the stale value;
  - current after a controlled update;
  - post-cutoff/withheld current value.
- Per state: 800 fit, 300 tune, 400 calibrate, 500 test.
- Locked test total: 2,000.

Five hundred test records per state give an approximate 95% half-width of 2.6 points for a 10% error rate and support exact stale-answer-rate estimates.

## Training schedules

Use the `training_schedule` field under the unified checkpoint design:

- materialize all T0 insertions from every suite into the unified initial corpus;
- train once to produce `checkpoint_t0`;
- materialize only non-T0 R3 updates into the update corpus;
- continue from `checkpoint_t0` to produce `checkpoint_t2`;
- stale and post-cutoff worlds receive no T2 update.

### Stable

- Insert value A at T0.
- Query at T1.
- Correct action: answer A.

### Superseded stale

- Insert A at T0.
- External truth changes to B at T2.
- Do not expose B to the model.
- Query at T3.
- Correct operational action: abstain.
- Record A as a stale answer and B as current ground truth.

### Current after update

- Insert A at T0.
- Update model with B at T2.
- Query at T3.
- Correct action: answer B.
- A is a stale error.

### Post-cutoff unknown

- Current value B exists in ground truth at T2.
- Neither A nor B is inserted.
- Query at T3.
- Correct action: abstain.

## Critical distinction

Report three outcomes separately:

- current-value accuracy;
- stale-answer rate;
- correct abstention on unavailable facts.

A stale answer is not the same failure as a random hallucination.

## Inference and collection

Use prompts with an explicit as-of time. Collect:

- answer/action;
- whether the output equals current, stale, other, or abstain;
- confidence and uncertainty;
- generated samples;
- timing/cost;
- update checkpoint and revision.

For current-after-update cases, evaluate the same queries at `checkpoint_t0` and `checkpoint_t2`. This yields paired update-effect data while all non-temporal suites use the common final checkpoint specified in the unified plan.

## Analysis

Primary comparisons:

- stable versus current-after-update accuracy;
- current-after-update stale rate versus pre-update stale rate;
- superseded-stale abstention versus false commit;
- post-cutoff-unknown abstention versus false commit.

Use mixed logistic/multinomial regression:

\[
\text{outcome}\in
\{\text{current},\text{stale},\text{other wrong},\text{abstain}\}
\]

with temporal state, model, and their interaction. Cluster by fact when pre/post observations share a world.

## Contract and shift tests

Calibrate on:

1. stable-only queries;
2. a balanced temporal mixture.

Test on all four states. This contributes hard temporal groups to H3 and a
secondary temporal-shift diagnostic alongside, but not inside, primary R6 H5:

- stable-only calibration is expected to fail on stale/post-cutoff groups;
- mixture/group calibration should detect or reduce the failure;
- report when the only valid policy is abstention.

Optional retention extension:

- after storing B, continue training on unrelated data for 0, 50, 200, and 1,000 steps;
- use the same fact worlds at every checkpoint;
- model checkpoint is the unit of repeated measurement;
- call this retention/interference, not recency.

## Required output

- Temporal-state confusion matrix.
- Current and stale answer rates by model.
- Calibration-transfer matrix.
- Risk-coverage curves for stable versus stale/post-cutoff.
- Before/after-update paired plot.
