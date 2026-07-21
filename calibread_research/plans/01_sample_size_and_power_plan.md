# Sample-size and power plan

## 1. Final generated scale

| Suite | Scientific role | Total records | Levels/profiles | Records per level | Locked test records |
|---|---|---:|---:|---:|---:|
| R0 | pipeline controls | 8,000 | 4 | 2,000 | 2,000 |
| R1 | exposure frequency | 7,000 | 7 | 1,000 | 1,750 |
| R2 | answer precision | 16,000 | 8 paired | 2,000 | 4,000 |
| R3 | temporal status | 8,000 | 4 | 2,000 | 2,000 |
| R4 | ambiguity | 8,000 | 4 paired | 2,000 | 2,000 |
| R5 | synthesis depth | 10,000 | 5 paired | 2,000 | 2,500 |
| R6 | domain shift | 8,000 | 4 | 2,000 | 2,000 |
| R7 | threshold policy | 5,000 | 5 profiles | 1,000 | 1,250 |
| **Total** |  | **70,000** |  |  | **17,500** |

Every requested suite has 5,000–16,000 records. The larger R2 and R5 files are necessary because the independent units are worlds and graphs, not their eight or five correlated query rows. These counts are chosen for balanced cell estimates, conformal calibration, paired contrasts, and a feasible generation budget.

## 2. Fixed split

Every level uses:

- 40% fit;
- 15% tune;
- 20% calibrate;
- 25% locked test.

The split is assigned by world index modulo 20. Every related query from a fact or graph remains in the same split.

Uses:

- fit trains learned uncertainty scorers;
- tune selects features, prompts, and fixed candidate policy grids;
- calibrate computes conformal quantiles or risk-control tests;
- test is used once for final results.

No data can move between partitions after model results are inspected.

## 3. Precision of binomial estimates

For a binary rate \(\hat p\), the rough ordinary standard error is:

\[
\sqrt{\hat p(1-\hat p)/n}
\]

At \(p=0.10\):

| Independent test units in a cell | Approximate 95% half-width |
|---:|---:|
| 250 | 3.7 percentage points |
| 375 | 3.0 points |
| 500 | 2.6 points |
| 1,000 | 1.9 points |

Exact binomial or cluster-bootstrap intervals, not this approximation, will be reported.

Paired suites R2, R4, and R5 compare conditions within the same world or graph. R0 uses four separate control strata, with paired direct/paraphrase prompts only inside the known-fact stratum. Precision must always be calculated from the relevant independent units rather than raw question-row counts.

## 4. Why each count is adequate

### R0: 2,000 paired worlds

- 500 locked worlds support direct-versus-paraphrase paired tests.
- Four action strata provide stable confusion-matrix estimates.
- The remaining 1,500 worlds support scorer fitting, tuning, and calibration.

### R1: 1,000 independent facts per exposure

- Seven levels give a 1,750-record test curve.
- 200 calibration cases per exposure support group diagnostics, while the primary continuous method may pool across exposure.
- Three training seeds are required; record count does not replace seed replication.

### R2: 2,000 worlds × eight precision queries

- 500 locked worlds produce eight repeated measurements.
- 400 calibration worlds meet the preferred minimum for every precision level.
- Pairing supports precise planned contrasts.
- It avoids treating 16,000 correlated questions as independent while retaining causal within-world comparisons.

### R3: 2,000 facts per state

- 500 locked facts per temporal state support stale-answer estimates.
- 400 calibration facts per state allow temporal-group policies without extreme quantile instability.

### R4: 2,000 worlds × four ambiguity levels

- 500 locked worlds permit trend analysis and second-turn clarification evaluation.
- Set precision/recall is evaluated on 1,500 ambiguous locked questions as a secondary answer-set analysis.

### R5: 2,000 graphs × five depths

- 500 locked graphs yield a 2,500-query depth curve.
- 400 calibration graphs meet the preferred minimum at every depth.
- Each graph supplies component probes and five final queries.
- Graph—not query—is the bootstrap unit.

### R6: 2,000 facts per domain

- 500 locked queries per domain.
- 400 calibration queries per domain.
- Enough for a full source-domain × target-domain matrix without sharing test labels.

### R7: 1,000 unique queries per profile

- 1,250 locked queries across five profiles.
- Scores are swept through 101 thresholds after generation.
- Threshold rows are not treated as new samples.

## 5. Pilot-based power calculation

The generated counts are the maximum planned pool. Before the locked run:

1. Draw only fit/tune pilot data.
2. Estimate:
   - baseline error;
   - within-world outcome correlation;
   - seed-to-seed variation;
   - cluster design effect;
   - anticipated effect size.
3. Compute power for each primary contrast.
4. If more records are required, increase counts before any test labels are viewed.
5. If fewer are needed, retain the unused cases as a future challenge set rather than silently dropping unfavorable examples.

Primary minimum detectable effect calculation:

- one-sided alpha 0.05 allocated through the five-way Holm procedure;
- 80% or 90% power;
- paired test where applicable;
- cluster/world as unit;
- model seed as a higher-level source of variation.

## 6. Conformal calibration considerations

The finite-sample resolution of an ordinary split-conformal quantile depends on calibration \(n\). For target miscoverage 0.05:

- calibration \(n=200\) permits a quantile resolution around 0.5 percentage points but group coverage is still noisy;
- calibration \(n=400\) is preferred for declared group contracts;
- intersections with fewer than the preregistered minimum must back off to a parent group.

Do not make dozens of intersecting 95% guarantees from cells containing only tens of examples.

## 7. Training seeds and inference samples

Minimum controlled replication:

- three training seeds for the 1B model;
- three seeds for 7B if compute permits;
- at least one frozen run plus repeated decoding seeds for external models.

Inference:

- one greedy result;
- five stochastic samples for main uncertainty features;
- sampling-budget ablation at 1, 3, 5, 10, and 20 on a fixed subset.

Multiple sampled answers are repeated observations for uncertainty estimation; they are not additional independent testcases.

## 8. Approximate output volume

For 70,000 primary testcase queries, three model/checkpoint/seed configurations,
and one greedy plus five stochastic samples, the base main-table volume is:

\[
70{,}000\times3\times6=1{,}260{,}000
\]

In general replace 3 by the actual number \(K\) of evaluated
model/checkpoint/training-seed configurations. This is not a project-wide upper
bound: add deduplicated R5 component probes (18,000 unique prompts), R4
clarification turns (18,000 chosen-option turns if all planned choices are
executed), natural datasets, retries, and ablations with their own declared
sample budgets. Therefore:

- cache outputs;
- pilot 1% first;
- use batched inference;
- do not run all suites on all model seeds until the R0 gate passes;
- use a preregistered subset for expensive semantic/NLI scoring if necessary.

## 9. Stopping rules

Stop or reduce scope if:

- R0 is degenerate;
- confidence scores contain no discrimination on tune;
- generation cost exceeds the documented compute budget;
- human grading disagreement exceeds 10%;
- calibration groups fall below minimum size;
- a dataset license prevents release.

Stopping cannot depend on which hypothesis looks favorable.
