# R1 protocol — parametric exposure frequency

## Scientific question

How does exact exposure count affect factual recall, confidence, calibration, and contract utility?

This is the causal version of “knowledge frequency.” Natural web-document counts may be used later only as observational validation.

## Testcase file and sample size

File: ../../testcases/r1_exposure_frequency.jsonl

- 7,000 independent fact worlds.
- Exposure levels: 0, 1, 2, 4, 8, 16, 32.
- 1,000 cases per level.
- Per level: 400 fit, 150 tune, 200 calibrate, 250 locked test.
- Locked test total: 1,750.

The seven-point log-spaced design can identify a nonlinear transition without assuming its location. At a 10% error rate, 250 test examples per level give an approximate 95% half-width of 3.7 points; the regression uses all 1,750 test cases. Three independent training seeds are necessary because one model-training trajectory is not a population of models.

## Hypothesis

H1: accuracy has a positive monotone association with log exposure. The one-sided monotonicity omnibus test is primary; the lower 95% cluster-bootstrap bound for exposure-16 minus exposure-1 accuracy exceeding 5 points is the practical-effect check. Ranking, transition location, and model-scale interaction are secondary.

Do not claim one universal threshold across model families.

## Training-corpus construction

For each record:

1. Read exposure_count and training_templates from injection_spec.
2. For exposure zero, materialize no document.
3. For positive exposure, cycle evenly over the four templates.
4. Shuffle only with the recorded seed.
5. Randomize and balance relation and answer token lengths across exposure bins once, then reuse that exact exposure assignment across all seeds and model sizes.
6. Ensure no evaluation query template appears in training.

Training should contain all exposure levels in one mixed run. Do not train a separate model per frequency level; that would confound exposure with checkpoint.

## Model design

Minimum:

- transparent 1B-scale model, three training seeds;
- transparent 7B-scale model, three LoRA/continued-pretraining seeds if resources allow;
- one instruction model for observational external validity.

Keep adapter rank, optimizer, learning rate, epochs, and total tokens identical across exposure levels.

## Inference

- one greedy response;
- five sampled responses;
- frozen prompt and 32-token answer cap;
- no retrieval or tools;
- collect log probabilities before answer normalization.

## Primary outcomes

- factual accuracy by exposure;
- false-commit rate for exposure zero;
- AURC by exposure;
- answer coverage under the primary 5% false-commit contract, with selective-risk targets reported secondarily;
- worst-level conformal coverage gap.

For H1 factual accuracy, only an exact committed answer is correct; abstention
at exposure zero is scored separately as correct action behavior, not as fact
retrieval.

## Secondary outcomes

- mean answer negative log-likelihood;
- exact answer entropy;
- optional P(True) and token-score availability;
- calibration slope/intercept;
- Brier score;
- prediction-set size;
- number of generations and latency.

## Analysis

Primary executable monotone step-spline logistic model:

\[
P(C=1\mid e_j)=p_j,
\qquad p_0\le p_1\le\cdots\le p_6
\]

Estimate the ordered Bernoulli probabilities with PAVA, compute the
likelihood-ratio improvement over a constant-rate null, and permute exposure
labels at the fact-cluster level while preserving cell counts. The configured
primary model supplies the confirmatory result. Exposure × model interaction,
a smooth monotone mixed-logistic curve, and segmented logistic curves are
sensitivity analyses.

Report:

- marginal predicted accuracy with 95% intervals;
- estimated exposure at 50%, 80%, and 90% accuracy when identifiable;
- model-by-frequency interaction;
- seed variability;
- monotonicity violations.

For a proposed change point, bootstrap the entire fitting procedure by fact and training seed. If the change point is unstable or outside the tested range, report it as not identifiable.

## Contract experiment

Calibrate:

1. one global threshold;
2. low/medium/high exposure-group thresholds;
3. continuous adaptive score;
4. CCRC.

Compare utility at the same validated risk. R1 supports H1 and contributes to H3/H4.

## Confound checks

- answer token count by level;
- template frequency by level;
- position in training stream;
- relation distribution;
- entity morphology;
- training loss by level;
- duplicate documents beyond the designed exposure;
- accidental occurrence of nonce answer strings in base tokenizer text tests.

## Required output

- Figure: accuracy versus log exposure by model.
- Figure: confidence and calibration versus exposure.
- Figure: answer coverage at fixed risk versus exposure.
- Table: change-point estimates and interactions.
- Error table: memorized wrong answer, abstention, random guess, formatting error.
