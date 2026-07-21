# R0 protocol — baseline and negative controls

## Purpose

R0 establishes that the entire pipeline behaves sensibly before any scientific claim is tested. It separates four abilities:

1. retrieve a directly phrased stored fact;
2. retrieve the same fact under an unseen paraphrase;
3. abstain when a synthetic fact was never stored;
4. reject a query containing a false premise.

If a model fails R0, results for the R1–R6 factors and the R7 stress suite are not interpretable.

## Testcase file and sample size

File: ../../testcases/r0_baseline_controls.jsonl

- 8,000 query records.
- 2,000 paired micro-worlds.
- Four records per world: known direct, known paraphrase, unknown entity, false premise.
- Per stratum: 800 fit, 300 tune, 400 calibrate, 500 locked test.
- Locked test: 2,000 records from 500 worlds.

The paired design is more efficient than 8,000 unrelated questions because direct and paraphrased questions share the same stored fact and split. With 500 test worlds, an error rate near 10% has an ordinary binomial 95% half-width around 2.6 percentage points. Pairing further improves the direct-versus-paraphrase comparison.

## Controlled variables

Fixed:

- single-hop query;
- categorical entity answer;
- stable temporal status;
- one interpretation;
- general-domain wording;
- 16 knowledge exposures for known cases;
- same answer-length and entity-name generator.

Varied:

- direct versus paraphrased query;
- stored versus not stored;
- valid versus false premise.

## Knowledge injection

For every world, inject the true director and true location facts 16 times through balanced declarative templates. Do not inject the unknown observatory or the false location premise. Use the same unified document stream and token budget across confirmatory seeds/models.

Run at least three training seeds for the controlled model. Preserve:

- checkpoint hash;
- data manifest hash;
- data order;
- optimizer state/configuration;
- tokenizer revision;
- random seed.

## Inference procedure

1. Load the frozen model and frozen prompt.
2. Generate one greedy read response.
3. Generate five stochastic samples for uncertainty features.
4. Parse answer and action.
5. Cache raw text and token log probabilities.
6. Grade the action first, then factual content.
7. Never substitute the expected action after seeing the answer.

The allowed actions are answer, abstain, clarify, and reject premise.

## Data to collect

Per query/model/seed:

- testcase ID and world ID;
- model and prompt revisions;
- greedy answer and parsed action;
- five samples;
- token log probabilities;
- optional P(True) and token-score availability;
- exact agreement and exact answer entropy;
- factual correctness;
- action correctness;
- latency, generated tokens, GPU seconds;
- grader version.

## Metrics

Primary:

- known-direct factual accuracy;
- known-paraphrase factual accuracy;
- abstention recall on unknown entities;
- false-premise rejection recall.

Secondary:

- known-query answer coverage;
- unknown-query false-commit rate;
- action macro-F1;
- paraphrase accuracy drop;
- Brier score and risk-coverage curve;
- cost per query.

## Statistical tests

- Direct versus paraphrase: paired McNemar test and paired bootstrap by world.
- Known versus unknown score separation: AUROC plus bootstrap interval.
- Action type: multinomial confusion matrix with Wilson intervals.
- Model comparison: mixed-effects logistic regression with world random intercept and fixed effects for condition, model, and their interaction.

Use Holm correction for the four R0 gate comparisons.

## Early checkpoint gate criteria

Every checkpoint included in downstream analysis must pass these policy-free
pipeline gates on fit/tune/calibrate only:

- raw known-direct accuracy is above 70%;
- direct-to-paraphrase loss is below 20 absolute points;
- automated grading agrees with manual review on at least 98 of 100 audited records;
- no world crosses data partitions.

Also report raw unknown false commits and raw false-premise rejection, but do not
make an arbitrary pre-calibration threshold on either a checkpoint-exclusion
rule. If the fixed gate fails, repair prompting, injection, parsing, or grading
using development partitions before any sealed-test generation.

## Post-calibration policy sanity check

After calibrating the final controller, evaluate R0 unknown and false-premise
behavior under the same frozen 5% false-commit contract. Report answer coverage,
false-commit risk, rejection/abstention recall, and whether the contract is
supported. This later policy check cannot retroactively change the early
checkpoint gate.

## Required output

- Table: four strata × models with accuracy/action rates.
- Figure: score distributions for known and unknown queries.
- Figure: R0 risk-coverage curves.
- Appendix: 100 manually inspected examples and error taxonomy.
