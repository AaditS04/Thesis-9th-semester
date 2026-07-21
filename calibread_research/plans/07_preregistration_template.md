# CalibRead preregistration template

Complete and timestamp this document before opening the locked test results.
Replace every bracketed field; unresolved fields mean the study is not frozen.

## 1. Administrative information

- Title: [ ]
- Authors and roles: [ ]
- Registration date and immutable location: [ ]
- Planned start/end dates: [ ]
- Testcase manifest hash: [ ]
- Code revision: [ ]
- Environment lock hash: [ ]
- Funding/conflicts: [ ]

## 2. Research question and scope

- Primary question: [ ]
- Definition of parametric read: [ ]
- Included output actions: [ ]
- Excluded retrieval/tools/long-form settings: [ ]
- Target deployment population: [ ]
- Unit of observation: testcase query.
- Unit of resampling/inference: world/fact/graph, as declared below.

## 3. Models and training

For every model:

- exact model and tokenizer revision: [ ]
- base/instruction status: [ ]
- training method and hyperparameters: [ ]
- corpus and order hashes: [ ]
- training seeds: [ ]
- checkpoint-selection rule using fit/tune only: [ ]
- R0 acceptance/exclusion gate: development-side raw known-direct accuracy >70%, direct-to-paraphrase loss <20 absolute points, grading agreement ≥98/100, and no split crossing; applied separately to every analyzed checkpoint.

## 4. Prompts and inference

- system prompt hash: [ ]
- user-template hash: [ ]
- response schema: [ ]
- greedy settings: [ ]
- stochastic settings: [ ]
- primary sample count: [ ]
- sampling ablation subset/counts: [ ]
- retry and infrastructure-failure rule: [ ]

## 5. Outcomes

- Primary commit-correctness definition: frozen exact/type-specific factual grader plus a uniquely valid singleton action; every R4 level-2–4 singleton `ANSWER` is commit-incorrect.
- Primary action-loss definition: false commit per incoming query, \(L_{fc}=1\{D=\text{ANSWER}\land C=0\}\).
- Primary risk/coverage contract: false-commit risk per incoming query.
- Target risk: 0.05.
- Calibration confidence level: 0.95.
- Primary utility: answer coverage.
- Minimum practically important effects: H1 5-point exposure-16 minus exposure-1 accuracy gain; H2 5% conditional composition-error floor; H3 2-point group violation above target; H4 3-point answer-coverage gain; H5 2-point cross-minus-within transfer gap.
- Secondary metrics: selective risk, set miscoverage and size, calibration, ranking, cost, action confusion, and R7 stress behavior.

## 6. Partition use

- fit use: [ ]
- tune use: [ ]
- calibration use: [ ]
- test access date and responsible person: [ ]
- technical mechanism preventing test tuning: [ ]

Confirm: worlds never cross partitions; stochastic samples are not counted as
independent testcases; threshold sweeps are not counted as independent cases.

## 7. Confirmatory hypotheses

### H1 exposure-frequency reliability

- Dataset: R1, with R0 gate.
- Primary endpoint: binary exact committed factual retrieval; every non-answer action is 0 for H1 retrieval, with exposure-zero abstention scored separately as action correctness.
- Primary model ID: [must match `analysis_config.primary_model_id`].
- Exposure model: ordered Bernoulli step-spline/isotonic MLE over 0/1/2/4/8/16/32.
- Model-scale interaction: secondary.
- Cluster/permutation unit: fact world; all training-seed repetitions stay together.
- Primary contrast/test: one-sided likelihood-ratio monotonicity omnibus with exposure-label permutation preserving cell counts; this is H1's single Holm result.
- Support criterion: Holm-adjusted monotonicity result plus lower 95% cluster-bootstrap bound for exposure 16 minus exposure 1 exceeding 5 points.
- Falsification criterion: [ ].
- Planned figure/table: [ ].

### H2 conditional synthesis penalty

- Dataset: R5.
- Component-availability conditioning rule: retain a graph-depth observation only when every required component question is correct.
- Primary endpoint/test: conditional multihop error tested one-sided against 5%; this is H2's single Holm result.
- Secondary independent-hop diagnostic: all graphs only, with graph-excluded cross-fitted component probabilities and \(1-\prod_j\widehat p_{j,-g}\).
- Depths included: 2–5, pooled for the single primary graph-clustered result.
- Graph-cluster bootstrap settings: [ ].
- Depth-specific simultaneous interval method: [secondary; ].
- Support/falsification criteria: [ ].
- Sensitivity analyses: [ ].

### H3 marginal validity hides group failure

- Global policy and target: false-commit risk 0.05 at calibration confidence 0.95.
- Exact preregistered group list: `r1_low_exposure` (0/1/2), `r2_exact_date`, `r2_decimal_5`, `r3_superseded_stale`, `r3_post_cutoff_unknown`, `r4_interpretations_3`, `r4_interpretations_4`, `r5_hops_4`, `r5_hops_5`, `r6_general`, `r6_biomedical`, `r6_legal`, `r6_technical`.
- Minimum group calibration/test size: [ ].
- Parent fallback hierarchy: [ ].
- Worst-group endpoint: maximum false-commit excess over 0.05; this is H3's single Holm result.
- Simultaneous/multiplicity method: [ ].
- Practically meaningful violation: simultaneous lower bound for maximum hard-group risk exceeds 0.07 while aggregate upper bound is at most 0.05.
- Support/falsification criteria: [ ].

### H4 complexity-conditioned utility

- CCRC policy family: [ ].
- Global and recent conditional baselines: [ ].
- Primary validity gate: each compared policy is supported for the aggregate mixture plus all 13 hard groups at false-commit target 0.05 under the same simultaneous procedure. H4's global baseline is joint-safe and distinct from H3's aggregate-only global policy.
- Primary utility endpoint: paired answer-coverage difference; this is H4's single Holm result.
- Minimum useful gain: 3 percentage points.
- Primary H4 null: paired answer-coverage gain is at most 3 percentage points.
- Profiler analyses: deterministic query_rules_v1.1 assignment is primary;
  trained and ground-truth oracle profilers are omitted in protocol v1.2.
- Compute-normalization rule: [ ].
- Support/falsification criteria: [ ].

### H5 calibration transfer under shift

- Dataset/domains: R6 plus [ ].
- Four primary source→target directions: general→biomedical, general→legal, biomedical→general, legal→technical, each compared with within-target calibration.
- Target-gap endpoint: maximum of four cross-minus-within false-commit target gaps; this is H5's single Holm result.
- Equivalence/degradation margin: 2 percentage points.
- Shift features/encoders: [ ].
- Adaptation baselines: [ ].
- Support/falsification criteria: [ ].

## 8. Multiple testing and intervals

- Family: H1–H5.
- Primary correction: Holm at alpha 0.05, one result from each hypothesis.
- Interval types: [exact binomial / world-cluster bootstrap / model-based].
- Bootstrap replicates and seed: [minimum 2,000].
- Treatment of model-training seeds: [ ].
- Simultaneous group/depth procedure: [ ].

## 9. Exclusions and missingness

Allowed exclusions only:

- duplicate testcase ID;
- demonstrably corrupt input;
- infrastructure failure under the frozen retry rule;
- model checkpoint failing the preregistered R0 gate.

Specify:

- malformed model output scoring: [normally incorrect/action failure];
- timeout rule: [ ];
- missing logprob rule: [ ];
- partial run rule: [ ];
- maximum acceptable missing rate: [ ];
- whether a failed model remains in an intention-to-evaluate summary: [ ].

Never exclude a row because it is difficult, surprising, or unfavorable.

## 10. Human annotation

- Sampling rule: [ ]
- Annotator count/training: [ ]
- Blinding: [ ]
- Rubric revision/hash: [ ]
- Agreement statistic and acceptance threshold: [ ]
- Adjudication rule: [ ]
- Automatic versus human precedence: [ ]

## 11. Baselines and ablations

- likelihood score: [ ]
- P(True): [ ]
- exact agreement: [ ]
- exact answer entropy (secondary diagnostic): [ ]
- verbal confidence: [OMITTED IN PROTOCOL V1.2]
- semantic entropy: [OMITTED IN PROTOCOL V1.2]
- learned scorer: [OMITTED IN PROTOCOL V1.2]
- global conformal/risk policy: [ ]
- adaptive/conditional baseline: [ ]
- no-complexity ablation: [ ]
- factor-removal ablations: [ ]
- calibration-size ablation: [ ]
- sampling-cost ablation: [ ]

For each, record exact repository commit, configuration, tuning space, and the
fit/tune criterion used to select it.

## 12. Sample size and stopping

- Final cases per dimension/level: [or manifest v1 counts].
- Power calculation assumptions/result: [ ].
- Training seeds: [ ].
- Pilot data permitted: fit/tune only.
- Compute ceiling: [ ].
- Predefined stop/reduce-scope conditions: [ ].
- Rule for retaining unused cases: [future locked challenge set].

Stopping cannot depend on confirmatory effect direction or p-value.

## 13. Deviations

For every change after registration, append:

| Date | Original decision | Change | Reason | Test data accessed? | Effect on confirmatory status | Approver |
|---|---|---|---|---|---|---|

Analyses added after test access are explicitly exploratory.

## 14. Sign-off

- Lead researcher/date: [ ]
- Supervisor/date: [ ]
- Independent leakage/configuration check/date: [ ]
- Immutable preregistration checksum: [ ]
