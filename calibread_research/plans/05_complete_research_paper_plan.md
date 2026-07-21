# Complete research-paper plan

## Working title

**CalibRead: Complexity-Conditioned Reliability Contracts for Parametric Reads in Large Language Models**

## One-sentence paper claim

Aggregate calibration and marginal coverage can conceal predictable failures across parametric-read complexity regimes; controlled complexity-aware contracts expose and partially mitigate these failures while quantifying the cost in abstention, set size, and compute.

## Contribution hierarchy

Primary:

1. controlled benchmark;
2. subgroup/shift audit;
3. contract methodology and artifact.

Secondary:

- uncertainty estimator comparison;
- failure taxonomy;
- model-scale analysis;
- natural external validation.

Do not lead with a new conformal theorem unless it is proved to be distinct from 2024–2026 work.

## Paper audience and venue

Best fit depends on final result:

- EMNLP/ACL: benchmark, factuality, calibration, ambiguity, multihop emphasis;
- ICLR: methodological reliability/control contribution with strong experiments;
- NeurIPS Datasets and Benchmarks: artifact and controlled benchmark emphasis;
- VLDB: only if the database contract/system abstraction and systems evaluation are substantially developed.

Select a provisional primary venue by week 2, then recheck the current formatting, ethics, reproducibility, anonymity, and submission calendar before week 12 and again before submission.

## Abstract template

Sentence 1: state why a forced LLM answer is not an adequate database read.

Sentence 2: identify the gap—aggregate factuality/calibration does not specify reliability by workload complexity.

Sentence 3: introduce CalibRead’s six controlled factors, separate policy stress suite, and 70,000 case specifications.

Sentence 4: introduce the exact contract/policy contribution without overstating the guarantee.

Sentence 5: give the strongest measured aggregate-versus-worst-group result.

Sentence 6: give the utility or shift result.

Sentence 7: state artifact release.

Write numbers only after the locked analysis.

## Section 1 — introduction

### Paragraph 1

Concrete failure: same LLM answers an easy known fact and a stale/high-precision/multihop query with similarly confident language.

### Paragraph 2

Define parametric read and the operational need for answer, abstention, clarification, or set.

### Paragraph 3

Explain why scalar hallucination rate and global calibration are insufficient.

### Paragraph 4

Explain why standard conformal marginal coverage does not automatically protect hard groups or shifted deployments.

### Paragraph 5

Present CalibRead benchmark and contract layer.

### Contributions list

Use exactly three or four measurable contributions. Avoid marketing adjectives and “first” unless verified.

## Section 2 — related work

Subsections:

1. factual knowledge and long-tail exposure;
2. LLM confidence/calibration;
3. semantic uncertainty and hallucination detection;
4. selective prediction and abstention;
5. conformal language generation/factuality;
6. conditional validity and distribution shift;
7. factual, ambiguity, and multihop benchmarks.

End each subsection with the precise remaining gap, not a generic statement that prior work is limited.

Required comparison table columns:

- output type;
- guarantee/loss;
- short/free/long form;
- conditional/group audit;
- shift;
- controlled memory exposure;
- ambiguity action;
- multihop component availability;
- open code.

## Section 3 — formal setup

Define:

- query and valid-answer set;
- correctness label;
- uncertainty score;
- read action;
- answer coverage;
- selective risk;
- false-commit risk;
- prediction-set miscoverage;
- contract tuple;
- deployment group;
- exchangeability and labeler assumptions.

Include one boxed warning:

> The certificate is a repeated-use guarantee over a declared population, not a posterior probability that this individual sentence is true.

## Section 4 — CalibRead benchmark

### Controlled micro-worlds

- schema;
- nonce entities;
- injected facts;
- held-out query templates;
- exact exposures;
- temporal versions;
- graphs.

### R0–R7

Summarize R0 as controls, R1–R6 as the six manipulated complexity factors, and R7 as a separate policy stress suite. Refer full cases to artifact/appendix.

### Splits

- 40/15/20/25;
- grouped by world;
- immutable test.

### Correctness

- deterministic graders;
- ambiguity/action grading;
- path grading;
- human audit.

### Dataset statistics

Use manifest-generated counts.

## Section 5 — methods

### Uncertainty features

Exact agreement is primary. P(True) and token probability are optional,
availability-labelled secondary diagnostics. Report exact-answer entropy under
that exact name. Verbal confidence, semantic entropy, and a learned scorer are
outside protocol v1.2.

### Candidate construction

Generation, strict parsing, exact normalization, and a frozen finite candidate
draw budget.

### Baseline policies

H3 aggregate-only global threshold, H4 global joint-safe threshold, standard
conformal/LTT, and a recent adaptive/conditional method. Name the two global
policies separately in every table so H3's subgroup failure is not confused
with H4's stricter baseline.

### CCRC

- complexity profiler;
- fixed groups;
- finite policy family;
- risk tests;
- hierarchical fallback;
- unsupported-contract action.

### Guarantee

State exact loss, probability, confidence, and assumptions.

If using selective-risk control, cite/instantiate an established method or include a complete proof.

## Section 6 — experimental setup

### Models

Exact IDs, revisions, base/instruction status, sizes, quantization.

### Training

One unified initial knowledge corpus, one R3 temporal-update stage, fixed exposure assignment across seeds/model sizes, checkpoints T0/T2, optimizer, LoRA/full tuning, tokens, and checkpoint gates. Do not describe suite-specific adapters as the confirmatory design.

### Decoding

Greedy + five samples, temperature, top-p, token cap.

### Baselines

List and implementation source/commit.

### Metrics

Factual, calibration, selection, contract, utility, cost.

### Statistical design

World cluster, tests, intervals, Holm, locked split.

### Compute

Hardware and total GPU hours.

## Section 7 — results

### 7.1 R0 gates

One compact table; move detail to appendix.

### 7.2 Complexity failure curves

H1 and H2 first. Show R1–R6 factual curves.

### 7.3 Uncertainty quality

Compare ranking and calibration, including exact-answer entropy’s
consistent-wrong limitation.

### 7.4 Marginal versus group reliability

H3: aggregate-only global policy passes the mixture target but violates the worst hard group.

### 7.5 CCRC utility

H4: predicted-profile answer-coverage gain over the global joint-safe policy,
with both supported for the aggregate plus all 13 groups at the 5%
false-commit target. Ground-truth-profile routing is an oracle diagnostic.

### 7.6 Shift

H5: domain transfer and target recalibration.

### 7.7 Cost and ablations

Sampling budget, profiler error, model scale, calibration size.

## Section 8 — error analysis

Audit:

- 200 highest-confidence wrong answers;
- random 200 wrong answers;
- 100 abstentions on known facts;
- ambiguity clarification failures;
- stale-value errors.

Report taxonomy proportions with uncertainty and examples that do not expose private/copyrighted content.

## Section 9 — limitations

Mandatory:

- synthetic ecology;
- open-model selection;
- English only;
- closed-book scope;
- finite candidate sampling;
- labeler dependence;
- marginal/group versus individual guarantees;
- exchangeability;
- target-domain labels needed for recalibration;
- compute cost;
- model revision dependence;
- possible benchmark contamination for natural data.

## Section 10 — conclusion

State:

- which factors predict failure;
- where contracts work;
- where they become vacuous;
- what future parametric read APIs should expose.

Do not say hallucination is solved.

## Main figures

1. Read-controller pipeline.
2. R1 exposure failure curves.
3. R2/R4/R5 paired complexity curves.
4. Conditional composition error, with the all-graphs independence diagnostic distinguished explicitly.
5. Aggregate versus worst-group validity.
6. Risk-coverage/utility Pareto frontier.
7. Domain transfer heatmap.
8. Calibration sample-size and compute tradeoff.

## Main tables

1. Related work.
2. Suite counts and factors.
3. Models/training/decoding.
4. H1–H5 decisions and effect sizes.
5. Contract validity and utility.
6. Required ablations.

## Appendix

- full testcase-generation algorithms;
- prompt text;
- schemas;
- complete per-level results;
- all models/seeds;
- exact group list;
- theorem/proof or method derivation;
- development-only repeated-calibration-split results;
- human rubric/agreement;
- compute;
- licenses;
- additional natural benchmarks;
- failure examples.

## Writing workflow

- Write methods and benchmark during weeks 3–16.
- Insert placeholder figure captions before experiments.
- Maintain one claim-evidence table: every abstract/introduction claim maps to one result artifact.
- Generate numerical text fragments programmatically where practical.
- Freeze terminology: answer coverage is not conformal coverage.
- Use one bibliography source and DOI/venue verification.

## Internal review checklist

- Can a reviewer reproduce every count from manifest?
- Is every baseline reasonably tuned without test access?
- Does every guarantee name its loss and assumptions?
- Are failure cases and unsupported scopes visible?
- Are natural results labeled observational?
- Does the abstract avoid subgroup-to-individual inference?
- Are compute and human-label costs reported?
- Does artifact include frozen model/prompt hashes?

## Release package

- generator and validator;
- 70,000 case specifications;
- split and checksum manifest;
- materialized knowledge-corpus recipe;
- raw-output release where licenses permit;
- graders;
- uncertainty features;
- calibration/contract code;
- analysis scripts;
- paper figure/table commands;
- data card;
- model/run cards;
- license and citation file.
