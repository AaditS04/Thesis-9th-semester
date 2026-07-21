# R6 protocol — domain specificity and domain shift

## Scientific question

How well do confidence calibration and reliability contracts transfer between domains when logical structure and exposure are held constant?

## Testcase file and sample size

File: ../../testcases/r6_domain_shift.jsonl

- 8,000 independent records.
- Four parallel domains: general, biomedical, legal, technical.
- 2,000 per domain.
- Per domain: 800 fit, 300 tune, 400 calibrate, 500 test.
- Locked test total: 2,000.

Five hundred test queries per domain support domain error estimates with roughly 2.6-point half-width near a 10% error rate.

## Controlled design

All domains use:

- one-hop entity answer with matched designation morphology;
- one interpretation;
- stable facts;
- 16 exposures;
- parallel template complexity.

Only the domain vocabulary framing of the subject varies. Query grammar,
registered-designation relation, answer morphology, exposure, and grading stay
fixed. This removes answer-type/relation-format confounding from the controlled
domain contrast. Natural datasets are a separate external-validity analysis.

## Continuous shift features

Omitted from protocol v1.2. Embedding distance, domain-classifier log odds,
prompt perplexity, relation/template novelty, and answer-token rarity are future
secondary work and are not needed for the categorical H5 endpoint.

## Procedure

1. Inject all domain facts in a balanced mixture.
2. Verify equal exposure and token totals by domain.
3. Run identical decoding.
4. Fit one pooled uncertainty scorer.
5. Fit domain-specific scorers as an ablation.
6. Calibrate on each domain separately and on the pooled mixture.
7. Test every calibration source against every target domain.

This produces the required pooled/domain transfer matrix.

## Hypothesis

H5: the maximum of four prespecified cross-minus-within false-commit target gaps exceeds the 2-point practical margin. The shift-feature explanation is secondary.

The four directions are general→biomedical, general→legal,
biomedical→general, and legal→technical. For each \(s\rightarrow t\), compare
\(R_{fc}^{s\rightarrow t}\) with \(R_{fc}^{t\rightarrow t}\).

## Metrics

- factual accuracy by domain;
- Brier/log loss;
- calibration slope/intercept;
- AURC;
- answer coverage under the 5% false-commit contract;
- prediction-set size;
- worst-domain risk gap;
- contract pass rate;

## Statistical analysis

- Domain × model mixed logistic model.
- Transfer matrix with exact/cluster-bootstrap intervals.
- Leave-one-domain-out analysis.
- One simultaneous maximum-gap result enters the H1–H5 Holm family; do not enter four direction-wise p-values separately.

Report directionality: general-to-biomedical and biomedical-to-general are different transfers.

## Natural external-validation track

Recommended mapping:

- general: SimpleQA Verified/Natural Questions;
- biomedical: BioASQ;
- multihop general: MuSiQue, analyzed separately;
- legal: use a factual short-answer subset with auditable sources, not a generic legal classification benchmark;
- current facts: FreshQA, analyzed as temporal shift.

Freeze exact dataset snapshots and licenses. Natural results are observational because exposure and pretraining mix are unknown.

## Contract methods

Compare:

- pooled global threshold;
- domain-specific/Mondrian calibration;
- continuous adaptive conformal baseline;
- importance-weighted method where density ratios are credible;
- CCRC hierarchical fallback;
- small labeled target-domain recalibration.

If a held-out domain has no supported guarantee, output contract unsupported.

## Required output

- Domain accuracy/calibration table.
- Calibration-source × target-domain heatmap.
- Worst-group coverage figure.
- Shift score versus coverage-gap plot.
- Target recalibration sample-size curve.
