# CalibRead research blueprint

## A six-month, paper-ready methodology for complexity-conditioned reliability contracts in parametric LLM reads

Literature and repository audit current through **22 July 2026**.

---

## 0. Executive decision

The P03 proposal contains a strong thesis problem, but it is not yet an executable or fully novel research plan.

The strongest defensible version of the project is:

> **CalibRead: Stress-Testing and Enforcing Complexity-Conditioned Reliability Contracts for Parametric Reads in Large Language Models**

The project should make three contributions:

1. **A controlled benchmark** in which the causes of read failure are independently manipulated: exposure frequency, answer precision, temporal status/retention, ambiguity, synthesis depth, and domain shift.
2. **A reliability audit** showing when global calibration or marginal conformal coverage hides systematic failures in hard subgroups and intersections of subgroups.
3. **A contract layer** that returns an answer, a set of answers, a clarification request, or abstention, while giving a precisely stated population-level risk guarantee for a declared deployment scope.

Do **not** make “we are the first to apply conformal prediction to open-ended LLM generation” the novelty claim. That claim is no longer true. Conformal Language Modeling already calibrated sampling/stopping rules for open-ended generation at ICLR 2024; conformal factuality already supplied back-off-based factuality guarantees at ICML 2024; later work addresses conditional validity, prompt adaptation, and covariate shift.

The thesis remains publishable if its center is changed from “invent conformal prediction for LLM reads” to:

> **measure, explain, and control how reliability guarantees fail across causally controlled query-complexity regimes.**

This is a realistic six-month thesis if the scope is frozen early. Ten model families, all seven original dimensions, long-form generation, natural and synthetic data, and a new conformal theorem are too much for one student in six months. The minimum publishable study should use three to four model configurations, short-form factual reads as the primary task, six well-defined factors, and one carefully validated contract method.

---

## 1. Detailed audit of the original P03

### 1.1 What is strong

- It treats hallucination as a structured function of the query and knowledge regime rather than one scalar property of a model.
- It connects calibration to an operational read decision.
- It recognizes abstention and prediction sets as useful alternatives to forced single-answer generation.
- It proposes failure curves rather than leaderboard-only evaluation.
- It targets a meaningful systems question: when may a caller safely “commit” an LLM answer as a database read?

### 1.2 What must be corrected

| Original element | Problem | Required correction |
|---|---|---|
| A confidence value \(c\) “bounds the probability that this particular answer is wrong” | Standard conformal prediction does not normally provide an individual posterior probability of correctness. Its basic guarantee is marginal over future examples under exchangeability. | Define exactly whether the certificate controls prediction-set miscoverage, false commits per incoming query, or error among committed reads. State the population and assumptions. |
| CPR as a new conformal wrapper for open-ended generation | This is substantially covered by prior work. | Reproduce these methods as baselines. Put novelty in controlled complexity, subgroup auditing, read contracts, or a rigorously distinct method. |
| “Minimal set size” | Conformal validity does not automatically imply globally minimal prediction sets. | Say “empirically minimizes expected set size over a prespecified validated policy family.” |
| R1 training-corpus frequency | Frequency is unknown for most closed models and only approximately measurable for many open models. | Use a controlled exposure track for causal claims and an open-corpus frequency proxy only for ecological validation. |
| R3 months after cutoff | Post-cutoff facts were never stored; this is not memory decay. Exact cutoff dates may also be uncertain. | Separate temporal availability, stale-value/supersession, and retention after continued training. |
| R4 number of valid interpretations | If multiple interpretations are valid, a single one may not be a hallucination. | Define the correct action as returning all valid interpretations, asking a clarification question, or abstaining. Score each action separately. |
| R5 multiplicative compounding | \(1-(1-H_1)^d\) assumes independent, equal per-hop errors. | Treat it as a null model. Measure each component fact and test deviations caused by dependence. |
| R6 “distance from training distribution center” | This is not operationally defined. | Use prespecified domains plus measurable covariate-shift scores such as prompt embedding distance, domain-classifier odds, or model perplexity. |
| R7 confidence threshold as a complexity dimension | Threshold is chosen by the decision policy; it is not a property of the query. | Remove R7 from the benchmark axes. Plot it as the operating point of the risk-coverage curve. |
| ECE and ACE as main metrics | Binned calibration metrics can hide local and subgroup errors and vary with binning. | Use Brier score, log loss, calibration intercept/slope, reliability diagrams, risk-coverage curves, AURC, and worst-group coverage gaps; retain ECE only as a secondary familiar metric. |
| Ten model families | This will multiply inference, scorer training, calibration, and analysis beyond a six-month project. | Use a transparent scaling family and two externally valid instruction models. Add a fourth only after the main pipeline is stable. |

### 1.3 What should be dropped from the core paper

- Long-form generation as a primary task.
- Claims that conformal prediction solves hallucination generally.
- Claims of per-instance factual probabilities without a stronger model and proof.
- “Universal constants” across all model families.
- A promised average prediction-set size of at most three before pilot evidence exists.
- A claim of an “optimal” threshold without defining a cost function and policy class.
- API-only models in the core reproducibility claim.

Long-form factuality can be a small appendix experiment if time remains. The core should remain short-form, closed-book, factual question answering with exact or carefully adjudicated labels.

---

## 2. Final thesis statement

### 2.1 Recommended title

**CalibRead: Complexity-Conditioned Reliability Contracts for Parametric Reads in Large Language Models**

Alternative benchmark-centered title:

**CalibRead: A Controlled Stress Test of Calibration and Selective Reliability in LLM Parametric Knowledge**

### 2.2 Central research question

> Can a closed-book LLM read interface maintain a declared factual-error contract across known sources of query complexity and distribution shift, and how much answer coverage and compute must it sacrifice to do so?

### 2.3 Subquestions

- **RQ1 — Failure surfaces:** How do factual error and miscalibration vary with exposure frequency, requested precision, temporal status, ambiguity, synthesis depth, and domain?
- **RQ2 — Hidden subgroup failure:** Do methods with valid aggregate calibration or marginal conformal coverage under-cover hard complexity groups?
- **RQ3 — Uncertainty signal:** Which white-box and black-box uncertainty signals most reliably rank correct versus incorrect parametric reads?
- **RQ4 — Contract enforcement:** Can a complexity-aware read policy satisfy prespecified error bounds while retaining more useful answers than a global threshold?
- **RQ5 — Shift:** How quickly do contracts fail when calibration and deployment differ, and which diagnostics or recalibration strategies recover validity?

### 2.4 Primary contribution claim

The safe primary claim is:

> Existing uncertainty and conformal methods are evaluated on aggregate benchmark distributions, but a parametric database read contract must remain interpretable across identifiable workload regimes. CalibRead provides controlled read-complexity interventions, audits conditional reliability, and evaluates contract-aware action policies under matched and shifted deployment.

### 2.5 Candidate method claim

Use a conservative name until the literature review is signed off:

> **Complexity-Conditioned Read Control (CCRC)** selects among single-answer, answer-set, clarification, and abstention policies using prespecified query groups and a held-out risk-control set. It optimizes utility only among configurations that pass a finite-sample risk test for the declared groups.

This should initially be described as an application and composition of conformal/Learn-then-Test ideas, not as a wholly new theorem. A new theoretical claim should be made only if the final method is mathematically distinct from Conformal Language Modeling, conformal factuality, conditional factuality control, adaptive conformal score transformation, CoFact, multivalid conformal prediction, and recent selective conformal risk-control work.

The authoritative mapping from the archival P03 wording to the final confirmatory design is in `calibread_research/plans/00_p03_to_final_crosswalk.md`. If this blueprint or any operational file conflicts with that crosswalk, the crosswalk controls until a dated preregistration amendment supersedes it.

---

## 3. Formal problem definition

### 3.1 Parametric read

A **parametric read** is a query answered from model parameters and the prompt only:

\[
q \longrightarrow M_\theta(q) \longrightarrow a
\]

No web search, retriever, database lookup, tool call, or hidden reference passage is allowed in the core condition. RAG may be included only as an explicitly labeled upper-bound or external-memory comparison.

### 3.2 Data-generating objects

- \(Q\): query.
- \(Z=(Z_1,\ldots,Z_6)\): observed or controlled complexity profile.
- \(\mathcal{Y}(Q)\): set of semantically valid answers.
- \(A\): generated answer.
- \(C(Q,A)\in\{0,1\}\): frozen operational commit-correctness label. It requires factual correctness and a uniquely valid committed response under the query contract; an arbitrary singleton on R4 ambiguity levels 2–4 has \(C=0\).
- \(U(Q,A)\): uncertainty or nonconformity score; larger values must consistently mean more uncertain.
- \(D\in\{\text{commit},\text{set},\text{clarify},\text{abstain},\text{reject-premise}\}\): read action. In machine-readable outputs, `ANSWER` maps to commit, `ABSTAIN` to abstain, `CLARIFY` to clarify, and `REJECT_PREMISE` to reject-premise. Answer sets are assembled by the external controller rather than requested as a fifth model-response label.
- \(G\): declared deployment group or collection of groups.

### 3.3 Read output

The system should return:

\[
\texttt{ReadResult} =
(a \text{ or } \mathcal{A}, D, s, \texttt{contract\_id},
\texttt{scope}, \texttt{model\_revision})
\]

The certificate must never be displayed as an unconditional statement such as “this answer is 95% correct.” It should state:

- the controlled risk;
- the target level;
- the confidence level of the calibration procedure;
- the calibration sample and deployment scope;
- whether the current query falls within that scope;
- the model, scorer, prompt, and calibration revisions.

### 3.4 Distinct risks that must not be conflated

For \(N\) queries:

- **Raw error rate**

\[
R_{\mathrm{raw}}=\frac{\#\text{incorrect answers}}{N}
\]

- **Answer coverage**, also called attempt rate

\[
\phi=\frac{\#\text{committed answers}}{N}
\]

- **Selective risk**, the most natural “wrong among returned reads” quantity

\[
R_{\mathrm{sel}}
=
\frac{\#\text{incorrect committed answers}}
{\#\text{committed answers}}
\]

- **False-commit risk per incoming query**

\[
R_{\mathrm{fc}}
=
\frac{\#\text{incorrect committed answers}}{N}
\]

- **Prediction-set miscoverage**

\[
R_{\mathrm{set}}
=
\Pr\{\mathcal{Y}(Q)\cap \widehat{\mathcal{A}}(Q)=\varnothing\}
\]

- **False candidates per returned set**

\[
R_{\mathrm{fp-set}}
=
\mathbb{E}\left[
\#\{a\in\widehat{\mathcal A}(Q):C(Q,a)=0\}
\right]
\]

These have different guarantees. Abstaining always reduces false-commit risk but may leave selective risk undefined when nothing is answered. A larger answer set improves set coverage while often increasing false candidates. Report all relevant quantities.

### 3.5 Reliability surface

The main empirical object is not a scalar hallucination rate but:

\[
H_m(z)=\Pr(C=0\mid Z=z,\;M=m,\;D=\text{commit})
\]

Estimate the six one-dimensional main-effect curves in the confirmatory core. Prespecified interactions are optional stretch analyses and must not delay or redefine the core. Do not attempt a dense six-dimensional grid.

### 3.6 Contract

A contract is:

\[
\mathcal K=(\mathcal G,r^\star,\delta^\star,\ell,B)
\]

where:

- \(\mathcal G\) is a prespecified collection of deployment groups;
- \(r^\star\) is the risk tolerance;
- \(1-\delta^\star\) is the confidence of the calibration claim;
- \(\ell\) is the exact loss being controlled;
- \(B\) is an optional compute/latency budget.

Primary example:

> On exchangeable English short-form factual queries in the six-factor deployment mixture defined in the frozen testcase and run manifests, model revision X with scorer Y and policy Z has false-commit risk per incoming query at most 0.05 with calibration confidence 0.95. The guarantee is not claimed for post-cutoff questions, unseen domains, or groups outside the declared scope.

Answer coverage is the primary utility endpoint. Selective risk, prediction-set miscoverage, set size, and domain-specific contracts are secondary analyses and must be labeled as such.

---

## 4. Novelty landscape that the paper must acknowledge

### 4.1 Closest work

1. **Conformal Language Modeling** calibrates a stopping rule for sampling an answer set from an unbounded LM output space and uses Learn-then-Test to select risk-controlling configurations. This is the closest predecessor to the original CPR idea.
2. **Language Models with Conformal Factuality Guarantees** uses progressively less specific outputs/back-off to provide high-probability correctness guarantees.
3. **Enhanced conformal validity methods** improve conditional behavior and scoring for LLM factuality.
4. **Conformal Risk Control** controls expected monotone losses beyond ordinary set coverage.
5. **Adaptive and conditional conformal factuality work in 2026** already adjusts thresholds based on prompt features or difficulty.
6. **CoFact at ICLR 2026** directly addresses conformal factuality under covariate shift.
7. **Semantic entropy** detects confabulation by clustering sampled answers by meaning.
8. **LM-Polygraph** provides a common implementation and benchmark for many uncertainty estimators.
9. **Uncertainty in the Wild** shows that uncertainty thresholds are sensitive to calibration/deployment shift.

### 4.2 The gap CalibRead can still own

The strongest remaining gap is the combination of:

- causal control over what was stored in parametric memory;
- factorial manipulation of read complexity rather than aggregation by dataset;
- separation of memory absence, stale knowledge, ambiguity, and reasoning failure;
- explicit auditing of marginal versus group/intersection reliability;
- an operational read interface with action and scope-aware certificates;
- evaluation of guarantee validity, usefulness, and inference cost together.

### 4.3 Required novelty checkpoint

At the end of week 2, create a spreadsheet with one row per related paper and columns:

- task and output type;
- short-form, long-form, MCQA, or free-form;
- source of correctness labels;
- uncertainty score;
- guarantee;
- assumptions;
- conditional/group behavior;
- distribution shift;
- abstention;
- candidate-set construction;
- compute cost;
- datasets;
- open-source code;
- exact difference from CalibRead.

No method section should be frozen until this table includes all work in the references at the end of this document and forward citations from the 2024 conformal papers.

---

## 5. Revised hypotheses

Use five confirmatory hypotheses. Label all other analyses exploratory.

### H1 — Exposure-frequency effect

At fixed model, relation family, answer morphology, and controlled training schedule, accuracy has a positive monotone association with log exposure. The one-sided omnibus monotonicity test is the single Holm-family result. As a prespecified practical-effect check, the lower 95% cluster-bootstrap confidence bound for the accuracy difference between exposure 16 and exposure 1 must exceed 5 percentage points. Model-scale interaction and change-point location are secondary.

### H2 — Conditional synthesis penalty

Among graphs for which every supporting component question is answered correctly, multihop final-answer error remains nonzero and exceeds the preregistered practical floor of 5%. The graph-level conditional composition-error test is the single Holm-family result.

The all-graphs comparison against the cross-fitted independence product

\[
1-\prod_{j=1}^{d}\widehat p_{j,-g}
\]

is a secondary diagnostic. Do not apply this probability formula after conditioning on all component answers being correct: under that conditioning it is a different estimand.

### H3 — Marginal validity hides subgroup failure

An aggregate-only global policy can satisfy the aggregate false-commit contract while at least one prespecified hard group violates it. The aggregate upper 95% confidence bound must be at most 0.05, and the simultaneous lower bound for the maximum hard-group risk must exceed \(0.05+0.02\). The maximum group excess, evaluated with a simultaneous interval, is the single Holm-family result. The confirmatory mixture and hard groups come from R1–R6; R7 is a secondary policy stress suite. This diagnostic policy is distinct from H4's global joint-safe baseline.

### H4 — Predicted-profile CCRC improves utility

Among policies that pass the same joint false-commit validity gate—aggregate plus all 13 hard groups under one simultaneous procedure—CCRC using a profile predicted from information available at inference time increases answer coverage over a single global joint-safe policy. The paired answer-coverage difference on the locked test set is the single Holm-family result; the meaningful-improvement threshold is 3 percentage points. Ground-truth factor labels are an oracle diagnostic, not the primary method.

### H5 — Domain transfer is asymmetric and incomplete

For each ordered source-to-target domain pair, compare the false-commit target gap under transferred calibration with within-target calibration. The primary statistic is the maximum of the four prespecified cross-minus-within target gaps, with a 2-percentage-point practical margin and a simultaneous 95% interval. This maximum-gap result is the single Holm-family result. The regression of transfer degradation on continuous shift scores is secondary.

### Multiple testing

Use Holm correction across the five confirmatory hypotheses, with the single primary result for each hypothesis specified above. Treat all remaining metrics and subgroup intersections as secondary or exploratory.

---

## 6. Benchmark design

Use two complementary tracks.

### 6.1 Track A — controlled parametric memory

Purpose: causal claims.

Create synthetic but linguistically natural “micro-worlds” with:

- typed entities;
- relations;
- categorical, numeric, and date-valued facts;
- controlled entity aliases;
- known ambiguity;
- known graph paths;
- versioned updates;
- exact exposure counts.

Use pronounceable nonce names rather than UUIDs so tokenizer length does not dominate difficulty. Match token length across factor levels.

Example:

~~~text
Entity: Velora Nemin
Relation: director_of
Object: Arven Observatory
Version: 2
Valid from: T2
~~~

Render each stored fact through several declarative templates:

~~~text
Velora Nemin directs the Arven Observatory.
The director of the Arven Observatory is Velora Nemin.
Arven Observatory is under the direction of Velora Nemin.
~~~

Test with templates never used during knowledge injection.

#### Controlled-training protocol

1. Generate fact records and assign factor levels using a seeded, counterbalanced design.
2. Render training documents with exact exposure counts.
3. Keep the number and style of paraphrases balanced.
4. Mix all frequency levels into the same training run so model-level training differences do not masquerade as frequency effects.
5. Use one unified document stream across suites and reuse the exact stream across seeds/model comparisons. Freeze the token/step budget per model before training; tokenizer-aware unrelated filler is needed only for a separate ablation that changes corpus length.
6. Continue pretraining or parameter-efficiently fine-tune a base model.
7. Save the exact adapter/checkpoint, optimizer settings, data order, and random seed.
8. Evaluate direct recall, paraphrases, inverse relations, ambiguity, and graph composition.
9. For updates, replace selected values at a later training stage and measure both current-value accuracy and stale-value retrieval.

LoRA/QLoRA is acceptable as a “parametric” store if the paper explicitly says the knowledge resides in adapter parameters. If the thesis claims behavior of dense pretraining memory, at least one smaller full-parameter continued-pretraining experiment is required.

### 6.2 Track B — natural external validity

Purpose: show that controlled findings matter on real facts.

Recommended sources:

- **SimpleQA Verified or SimpleQA** for short, unambiguous parametric factuality;
- **PopQA or TriviaQA with an open-corpus frequency estimate** for popularity/frequency;
- **FreshQA**, with an immutable dated snapshot, for pre-cutoff versus post-cutoff and changing facts;
- **AmbigNQ/CAmbigNQ** for ambiguity and clarification behavior;
- **MuSiQue** for two-to-four-hop composition;
- **BioASQ** for biomedical transfer if licensing and evaluation access are practical;
- **AbstentionBench** as a secondary external test of unanswerable, underspecified, false-premise, and outdated queries.

Do not mix all datasets into one accuracy number. Each supports a different construct and has different answer semantics.

### 6.3 Complexity factors

#### R1 — parametric exposure frequency

Controlled levels:

\[
e\in\{0,1,2,4,8,16,32\}
\]

- \(e=0\) is a known-unknown control and must lead to abstention rather than guessed correctness.
- Counterbalance relation, answer length, entity morphology, domain scaffold, and data position.
- Natural validation uses log-binned document co-occurrence or entity popularity from a corpus known to be relevant to the transparent model.
- Never call natural frequency causal.

#### R2 — requested precision

Use the same underlying fact at successively stricter output tolerances:

- categorical/coarse value;
- integer or year;
- month/date;
- exact date or exact numerical value;
- specified significant figures or tolerance.

Example:

- “In which year did X occur?”
- “On which date did X occur?”
- “Give the measured value to one decimal place.”
- “Give the measured value to three decimal places.”

The ground-truth scorer must encode the required tolerance. A response that is correct to one decimal place is wrong for a three-decimal query if the requested contract requires that precision.

#### R3 — temporal status

Split the vague original axis into two constructs.

**R3a: availability/freshness**

- stable pre-cutoff fact;
- changed fact whose old value was valid at training time;
- post-cutoff fact;
- deliberately unanswerable future fact.

Expected correct behavior differs: a post-cutoff closed-book query should normally be abstained on, not answered.

**R3b: parametric retention**, optional if compute permits

- evaluate immediately after insertion;
- evaluate after fixed amounts of unrelated continued training;
- evaluate after a conflicting update;
- track current-answer accuracy and stale-answer rate.

Do not say a static checkpoint’s memory “decays with calendar time.” Only model updates, continued training, changed external truth, or query distribution shift can produce the measured effect.

#### R4 — ambiguity

Controlled levels:

\[
a\in\{1,2,3,4\}\text{ plausible interpretations}
\]

Generate collisions through:

- shared person names;
- underspecified organization/location names;
- omitted temporal reference;
- relation scope ambiguity;
- pronoun or modifier attachment.

Correct outputs are action-dependent:

- for an unambiguous question: answer;
- for a resolvable ambiguous question in the secondary set mode: let the external controller provide a labeled set;
- for ambiguity requiring user intent: ask one minimal clarification question;
- for insufficient information: abstain.

In the primary R4 prompt, levels 2–4 explicitly require user intent. Therefore
an arbitrary single-answer commit is incorrect even if its role string appears
among the plausible interpretations. Measure ambiguity/action correctness,
secondary set quality, and post-clarification factual correctness separately.

#### R5 — synthesis depth

Use reasoning graphs with \(d\in\{1,2,3,4,5\}\) edges.

In the controlled generator, every depth returns the same `Designation` entity
type: \(d-1\) linked-record edges followed by one designation edge. This keeps
answer morphology and grading constant while depth changes.

Controls:

- identical terminal answer distribution across depths;
- comparable prompt length;
- no lexical shortcut from question to answer;
- each intermediate relation testable as a single-hop item;
- disjoint graph components across train/calibration/test;
- no answer frequency imbalance.

Primary analysis must condition on component availability. Otherwise a “reasoning” failure may simply be an unknown supporting fact.

#### R6 — domain and distribution shift

Use four domains with parallel relation templates in the controlled track:

- general entities;
- biomedical-like;
- legal/administrative-like;
- scientific/technical.

For natural data, domain is categorical. Supplement it with continuous shift measures:

- domain-classifier log odds;
- nearest-neighbor distance to calibration prompts in a frozen embedding space;
- base-model prompt perplexity;
- relation/template novelty.

Fit all shift estimators without using test correctness labels.

### 6.4 R7 becomes an operating variable

Let \(\tau\) vary over the unique uncertainty scores or a fixed grid. Plot:

- answer coverage versus selective risk;
- set size versus miscoverage;
- latency/cost versus risk;
- subgroup risk versus threshold.

The threshold is chosen on development/calibration data and applied once to the locked test set.

### 6.5 Main-effect design and optional interactions

A full \(7\times5\times4\times4\times5\times4\) factorial is infeasible and statistically wasteful.

The confirmatory 70,000-record core uses one-factor-at-a-time main-effect curves around a prespecified reference condition for R1–R6. R7 is a separate policy stress suite, not a seventh causal factor.

Only after the core analyses are complete, optionally add two exploratory interactions—frequency × synthesis depth and ambiguity × synthesis depth—and a small space-filling stress sample. These additions require separate generated records, a dated amendment, and their own sample-size justification; they are not required paper figures.

Recommended reference condition:

- exposure 16;
- coarse factual precision;
- current/stable value;
- one interpretation;
- one hop;
- general domain.

### 6.6 Sampling unit and leakage prevention

The independent unit is the underlying fact or micro-world, not a paraphrased question.

All paraphrases, inverse queries, and multihop questions derived from one micro-world must remain in the same split. Split by connected graph component when multihop paths share entities.

Use four disjoint partitions:

- **fit**: train uncertainty scorers;
- **tune**: choose features, prompts, model hyperparameters, and candidate policy grid;
- **calibrate**: compute conformal quantiles or run risk tests;
- **test**: touched exactly once for final analysis.

Suggested proportions:

\[
40\% / 15\% / 20\% / 25\%
\]

For any confirmatory group guarantee, target at least 400 calibration and 400 test units in that group. If that is unaffordable, reduce the number of guaranteed groups rather than pretending a sparse cell is reliable.

### 6.7 Sample-size target

At error rate 0.10, \(n=500\) gives an approximate 95% interval half-width of 2.6 percentage points before clustering/design effects. At coverage 0.95, \(n=1000\) gives an approximate half-width of 1.35 points.

Locked core design:

- 70,000 generated records across R0–R7, of which 17,500 are in the sealed test split;
- equal total mixture weight for each confirmatory factor suite R1–R6 and equal level weight within each suite during aggregate policy fitting/evaluation;
- at least 400 independent calibration and test units for every group receiving a confirmatory contract claim;
- 400–600 independent units per optional exploratory interaction cell, if those interactions are added after the core;
- at least 1,000 examples per natural external-validation source when available;
- a 200-unit-per-cell pilot before final power calculation.

After the pilot, estimate the paired variance and intracluster correlation, then freeze the final sample-size calculation in a preregistration.

---

## 7. Model panel

### 7.1 Core models

Use a transparent family for causal/data-frequency work:

- **OLMo 2 1B and 7B** as the preferred pair because weights, training code, recipes, data information, and checkpoints are openly documented.

Use one or two external-validity models:

- **Qwen3 8B** or another stable, permissively usable 7–9B instruction model;
- **Llama 3.1 8B Instruct** or a comparable second architecture if license/access permits.

The exact model identifiers, revisions, tokenizer revisions, licenses, and download hashes must be frozen in a manifest before the main run.

### 7.2 Base versus instruction model

Instruction tuning changes calibration. Therefore:

- use instruction models for the primary read-interface study;
- use a matched base/instruction pair as an ablation on a subset;
- use base models for controlled knowledge injection when that simplifies causal interpretation;
- do not pool base and instruction results.

### 7.3 Why not ten families

Every additional model multiplies:

- answer generation;
- sampled generations for semantic uncertainty;
- uncertainty-scorer fitting;
- conformal calibration;
- test evaluation;
- subgroup analysis;
- storage and manual adjudication.

Three well-audited configurations are stronger than ten partially run models.

### 7.4 Decoding protocol

For every model:

- one greedy answer for the main factual-read result;
- \(M=5\) stochastic samples for uncertainty in the main experiment;
- \(M\in\{1,3,5,10,20\}\) in the sampling-budget ablation;
- temperature 0.7 and top-p 0.95 for sampled generations unless the pilot justifies another fixed setting;
- maximum 32 generated tokens for short answers;
- one frozen system/user prompt;
- stop strings and answer-extraction logic versioned;
- deterministic seeds where the inference backend supports them.

Never compare uncertainty methods using different sampling budgets unless compute-normalized results are also reported.

---

## 8. Correctness and action labeling

### 8.1 Short-form factual answer

Use a deterministic scoring cascade:

1. Unicode and whitespace normalization.
2. Case and punctuation normalization.
3. Dataset-provided aliases.
4. Numeric/date parser with declared tolerance.
5. Exact canonical ID match for synthetic facts.
6. Human adjudication for unresolved natural-language equivalence.

Embedding similarity alone is not a factual correctness label.

### 8.2 Abstention

The model prompt should require one parseable status:

~~~text
ANSWER: <short answer>
STATUS: answer | ambiguous | unknown
~~~

Map clear “I do not know” variants to abstention only if the answer field contains no factual guess. An answer followed by hedging is still an attempted answer.

### 8.3 Ambiguous question

Record:

- ambiguity detected;
- returned interpretation set;
- set precision and recall over valid interpretations;
- clarification question validity;
- factual accuracy after clarification, in a simulated second turn.

### 8.4 Multihop question

Store:

- final answer;
- ordered supporting facts;
- answers to each component query;
- whether all components were individually available;
- whether the final composition was correct.

### 8.5 Human annotation

Use human labels for at least:

- 100% of disputed automatic grades;
- the fixed construction, development-grader, R4-clarification, and locked-test
  audit streams defined in the results plan;
- for each natural dataset, the preregistered random sample
  \(\min\{n,\max(200,\lceil0.05n\rceil)\}\);
- all long-form appendix outputs.

Protocol:

- two independent annotators blind to model and method;
- written rubric with examples;
- adjudication by a third person or the thesis supervisor;
- report raw agreement and Krippendorff’s alpha or Cohen’s kappa;
- revise the rubric on pilot data only, never after seeing locked test results.

An LLM judge may be a secondary scalable scorer, but it must be validated against human labels and cannot be the sole source of the theorem’s “ground truth.”

---

## 9. Uncertainty estimators and baselines

Implement all estimators behind one interface returning a scalar whose direction is fixed.

### 9.1 Zero/additional-compute baselines

- sequence mean negative log-likelihood;
- sequence total negative log-likelihood;
- minimum token probability;
- predictive entropy over the next answer token where meaningful;
- margin between top candidate scores;
- answer length;
- direct verbalized confidence;
- P(True): ask the model whether its proposed answer is correct.

### 9.2 Sampling-based baselines

- exact-answer agreement;
- top semantic-cluster mass;
- number of semantic clusters;
- semantic entropy;
- lexical diversity;
- pairwise entailment consistency;
- sample-answer likelihood statistics.

Semantic clustering:

- exact canonical identity in the controlled track;
- alias match first in natural QA;
- bidirectional NLI equivalence for remaining pairs;
- manually audit a stratified sample of clusters.

### 9.3 Learned scorers

Primary:

- logistic regression over uncertainty and complexity features.

Secondary:

- gradient-boosted trees;
- small MLP;
- hidden-state correctness probe for white-box models.

Features may include:

- sequence likelihood;
- semantic entropy;
- agreement;
- P(True);
- prompt perplexity;
- factor/profile estimates;
- answer length;
- domain-shift score.

Fit on the fit split only. Tune on tune. Freeze before conformal calibration.

### 9.4 Probability calibration baselines

- uncalibrated score mapped monotonically to confidence;
- Platt/logistic scaling;
- temperature scaling where logits are defined;
- isotonic regression;
- beta calibration, optional.

Evaluate:

- Brier score;
- negative log-likelihood;
- calibration intercept and slope;
- reliability diagram;
- adaptive ECE and equal-width ECE as secondary metrics;
- worst-group calibration error.

### 9.5 Selective/conformal baselines

- no abstention;
- random abstention at matched coverage;
- oracle ranking, clearly labeled unattainable;
- global threshold chosen on tune;
- global conformal prediction;
- Conformal Language Modeling;
- conformal factuality/back-off;
- a recent prompt-adaptive or conditional conformal method;
- domain-weighted/covariate-shift-aware method when shift weights can be estimated;
- CCRC.

Reuse **LM-Polygraph** for uncertainty estimators where possible. Reuse the current **semantic_uncertainty** repository for the semantic-entropy baseline. Use **TorchCP** as a tested reference for ordinary conformal primitives, but verify that its language-model component implements the exact loss and guarantee needed here.

---

## 10. CCRC methodology

### 10.1 Design goal

CCRC is a post-hoc read controller. It does not change the base model. It receives:

- query;
- generated candidates;
- uncertainty features;
- complexity profile;
- contract specification.

It returns:

- committed single answer;
- bounded candidate set;
- clarification request;
- abstention.

### 10.2 Query profiler

In the controlled track, predicted factor profiles based only on inference-time information are primary for H4. Use ground-truth factor labels only as an oracle diagnostic and unit-test path.

In the natural track, estimate:

- ambiguity probability;
- predicted hop depth;
- domain;
- temporal/post-cutoff flag;
- answer-type/precision class;
- frequency/popularity bin or unknown;
- continuous shift score.

The profiler must be trained without test labels. Report its own accuracy because misrouting can invalidate subgroup utility and weaken any claimed scope.

### 10.3 Candidate generation and clustering

1. Generate greedy answer \(a_0\).
2. Draw up to \(M\) stochastic answers.
3. Canonicalize exact aliases.
4. Cluster remaining responses by semantic equivalence.
5. Estimate cluster mass and uncertainty.
6. Rank clusters/candidates.
7. Construct a nested family of possible outputs:
   - abstain;
   - top one;
   - top two;
   - …;
   - all sampled clusters;
   - clarification action for ambiguous queries.

The candidate universe is finite because sampling has a maximum budget. Therefore the guarantee must account for the event that no correct candidate was generated. Conformal Language Modeling addresses this by calibrating a sampling/stopping policy. Do not silently condition on the correct answer already appearing in the candidate pool.

### 10.4 Policy family

Define a finite policy grid before calibration:

\[
\Lambda =
\{\text{score threshold}\}
\times
\{\text{sample budget}\}
\times
\{\text{set-size rule}\}
\times
\{\text{action rule}\}
\]

Keep the grid small enough for stable risk testing. Build it on the tune split.

### 10.5 Contract modes and their status

Mode B is the confirmatory contract: false-commit risk per incoming query at target 0.05 with calibration confidence 0.95. Mode A and Mode C are secondary analyses. This priority cannot be changed after the preregistration lock without a dated amendment.

#### Mode A — answer-set coverage

Loss:

\[
L_{\mathrm{set}}(\lambda)
=
\mathbb 1\{\text{no valid answer is present in the returned set}\}
\]

This secondary mode is closest to standard conformal language modeling. Under the precise exchangeability and fixed-scoring assumptions, calibrate a policy whose expected miscoverage is at most \(\alpha\).

Primary utility:

- mean and median set size;
- singleton rate;
- empty/abstain rate;
- number of samples drawn;
- latency.

#### Mode B — false-commit risk

Loss:

\[
L_{\mathrm{fc}}(\lambda)
=
\mathbb 1\{D_\lambda=\text{commit and answer is incorrect}\}
\]

Use Learn-then-Test or conformal risk control over a finite policy family at \(r^\star=0.05\) and calibration confidence \(1-\delta^\star=0.95\). This gives the primary risk per incoming query, but it is not the same as the error rate among answered queries.

Report answer coverage and selective risk alongside it so a near-always-abstaining policy cannot appear useful.

#### Mode C — selective risk

Target:

\[
\Pr(C=0\mid D_\lambda=\text{commit})\le r^\star
\]

This secondary mode is intuitive but statistically harder. Use an existing selective risk-control procedure with a published proof, or derive the ratio-risk test carefully with a statistician. Recent 2026 work such as SCoRE is directly relevant.

Do not claim Mode C from ordinary split conformal coverage or from a naive confidence threshold.

### 10.6 Complexity conditioning

The confirmatory joint contract contains the aggregate mixture plus the 13 exact
hard groups listed in `02_hypothesis_execution_plan.md`: pooled R1 exposure
0/1/2; R2 exact-date and five-decimal groups; two unavailable R3 groups; R4
ambiguity levels 3 and 4; R5 depths 4 and 5; and all four R6 domains. Other
main-effect levels are descriptive or scorer features, not additional
confirmatory guarantees.

Any interaction groups added in the stretch study are exploratory unless a dated amendment is frozen before their locked evaluation.

Compare:

1. the H3 aggregate-only global diagnostic policy;
2. one global joint-safe policy calibrated against aggregate plus all 13 groups;
3. domain-specific policy;
4. factor-group policy;
5. continuous prompt-adaptive baseline;
6. predicted-profile CCRC hierarchical policy;
7. ground-truth-profile CCRC oracle diagnostic.

Hierarchical fallback:

- use intersection policy if its calibration size meets the preregistered minimum;
- otherwise back off to the parent group;
- then to the global policy;
- if no policy passes the risk test, abstain or declare the contract unsupported.

The fallback order must be fixed before the calibration split is inspected.

### 10.7 Risk testing

Follow the Learn-then-Test structure:

1. define one null hypothesis for every fixed policy/group pair;
2. compute a valid risk-test p-value on the calibration split;
3. control family-wise error across the tested family;
4. retain only configurations whose unsafe null is rejected;
5. among retained configurations, choose maximum utility;
6. if no configuration is valid, return “contract unsupported.”

For answer-set coverage, reproduce the binomial-tail/LTT construction from Conformal Language Modeling before extending it.

For multiple groups, account explicitly for testing multiplicity. Do not reuse a 0.05 level independently for dozens of groups and call the joint contract 95% valid.

### 10.8 Guarantee language

The theorem/proposition should list:

- exchangeability or weighted-exchangeability assumption;
- fixed model, prompt, scorer, profiler, candidate generator, and policy family;
- identical correctness labeler in calibration and deployment;
- finite calibration sample;
- exact controlled loss;
- probability taken over calibration draw, test query, model sampling, or all three;
- behavior when no valid configuration is found.

### 10.9 Shift handling

Run four deployment regimes:

1. IID mixture;
2. reweighted complexity mix;
3. held-out domain;
4. temporal/post-cutoff shift.

Methods:

- global unchanged calibration;
- group/Mondrian calibration;
- importance-weighted conformal calibration where density ratios are estimable;
- recent covariate-shift conformal baseline;
- recalibration with a small labeled target sample.

Always include a “fail closed” rule: if shift exceeds a preregistered diagnostic threshold and no shifted guarantee applies, the controller says the contract is unsupported rather than emitting the old certificate.

---

## 11. Metrics

### 11.1 Base factual performance

- exact match;
- alias-aware accuracy;
- numerical/date tolerance accuracy;
- stale-answer rate;
- ambiguity detection F1;
- clarification success;
- component fact accuracy;
- multihop final accuracy.

### 11.2 Uncertainty discrimination

- AUROC for correct versus incorrect;
- AUPRC with the positive class stated;
- risk-coverage curve;
- AURC;
- excess AURC relative to oracle ordering;
- selective risk at 25%, 50%, 75%, and 90% answer coverage.

AUROC is not enough because it ignores the deployment threshold.

### 11.3 Calibration

- Brier score;
- log loss;
- calibration intercept;
- calibration slope;
- reliability diagrams with confidence bands;
- ECE/ACE as secondary;
- local or worst-group calibration gap.

### 11.4 Contract validity

- empirical risk versus target;
- one-sided exact confidence interval;
- marginal coverage gap;
- worst-group coverage gap;
- fraction of groups meeting target;
- simultaneous-contract pass rate over repeated splits;
- behavior when the calibration sample is small.

### 11.5 Utility

- answer coverage;
- mean/median/90th-percentile prediction-set size;
- singleton set rate;
- abstention rate;
- clarification rate;
- useful-answer score, defined before evaluation;
- vacuous-output rate.

### 11.6 Cost

- number of model generations;
- input/output tokens;
- verifier/NLI calls;
- GPU-seconds;
- wall-clock latency;
- peak memory;
- monetary API cost if any.

Plot risk, utility, and cost together.

### 11.7 Complexity curves

For each factor level, plot:

- raw factual error;
- confidence and calibration gap;
- AURC;
- coverage at target risk;
- prediction-set size at target miscoverage;
- contract pass/fail.

Include confidence bands and raw cell sample counts.

---

## 12. Statistical analysis

### 12.1 Unit of inference

Cluster by:

- underlying fact;
- micro-world/connected graph;
- natural question ID when paraphrases exist.

Never treat multiple sampled answers or paraphrases as independent test examples.

### 12.2 Main model

For correctness:

\[
\operatorname{logit}\Pr(C_{ij}=1)
=
\beta_0
+ f_1(\log(1+e_i))
+ \beta_2 p_i
+ \beta_3 t_i
+ \beta_4 a_i
+ f_5(d_i)
+ \beta_6 \text{domain}_i
+ \gamma_{\text{model}}
+ u_{\text{world}}
\]

In the 70,000-record core, fit main effects only. If the optional interaction
extension is separately generated and preregistered before its locked
evaluation, add only those amended interactions. Use:

- generalized additive model or restricted cubic splines for continuous curves;
- mixed-effects logistic model for binary correctness;
- cluster-robust standard errors or world-level bootstrap;
- model as a fixed effect in the primary analysis;
- seed/checkpoint as a random or blocking factor where enough levels exist.

### 12.3 Calibration comparisons

Use paired bootstrap by fact/world for metric differences. For reliability curves, show bootstrap bands rather than only one ECE number.

### 12.4 Conformal/contract assessment

- use exact binomial intervals for binary coverage where appropriate;
- report target minus observed coverage;
- before the week-20 lock, repeat policy fitting/calibration over at least 20 seeded repartitions of fit/tune/calibrate only for a secondary stability appendix; never move or reuse the sealed test in these repartitions;
- keep one canonical preregistered split for the main paper;
- distinguish a guarantee from an empirical confidence interval.

### 12.5 Domain transfer

Construct a matrix with calibration domain on rows and test domain on columns. Each cell reports:

- coverage/error;
- target gap;
- utility;
- shift score;
- calibration sample size.

### 12.6 H2 composition tests

Primary conditional estimand:

1. group all component questions and the multihop question by graph;
2. retain graphs for which every component answer is correct;
3. compute multihop final-answer error in that retained population;
4. test whether it exceeds the preregistered 5% practical floor with a one-sided graph-clustered interval/test;
5. bootstrap and resample only at graph level.

Secondary all-graphs diagnostic:

1. estimate each component-success probability using cross-fitting that excludes the evaluated graph;
2. form the independence prediction \(1-\prod_j\widehat p_{j,-g}\);
3. compare predicted and observed multihop error by graph and depth;
4. report amplification or redundancy descriptively with graph-clustered intervals.

Do not use the independence-product formula inside the all-components-correct subset. Component-question accuracy is an observable proxy for availability, not proof that the same internal reasoning path was used.

### 12.7 Effect sizes

Report:

- absolute risk difference;
- relative risk where stable;
- odds ratio from regression;
- change in answer coverage at fixed risk;
- change in set size at fixed coverage;
- GPU cost difference.

P-values are secondary to effect sizes and confidence intervals.

---

## 13. Ablations and robustness checks

Required ablations:

1. Remove complexity features from the learned scorer.
2. Global versus group versus continuous-adaptive threshold.
3. Each uncertainty feature alone.
4. Semantic entropy with different NLI/clusterers.
5. Sampling budgets \(1,3,5,10,20\).
6. Greedy versus sampled base answer.
7. Base versus instruction-tuned checkpoint.
8. Ground-truth versus predicted complexity profile.
9. Exact versus automated semantic correctness grader.
10. Calibration sample sizes \(50,100,200,500,1000\).
11. Matched versus shifted calibration.
12. With and without known-unknown examples in calibration.
13. Different prompt paraphrases.
14. Different decoding seeds.
15. Controlled-only versus natural-data transfer.

Stress tests:

- typos;
- harmless paraphrase;
- misleading premise;
- demand for unjustified precision;
- “answer confidently” adversarial instruction;
- prior chat history containing a false answer;
- domain mix reweighting;
- stale fact and superseded value;
- novel entity aliases;
- unseen reasoning templates.

---

## 14. Exact recommended experiment matrix

### 14.1 Minimum publishable version

Models:

- OLMo 2 1B instruction or matched read-ready checkpoint;
- OLMo 2 7B instruction;
- one external 7–9B instruction model.

Controlled axes:

- R1: 0, 1, 2, 4, 8, 16, 32 exposures;
- R2: 4 precision levels;
- R3a: stable, stale, post-write/current, unknowable;
- R4: 1, 2, 3, 4 interpretations;
- R5: 1, 2, 3, 4, 5 hops;
- R6: 4 domains.

Interactions:

- R1 × R5;
- R4 × R5.

Natural sources:

- one short-form factual benchmark;
- FreshQA;
- AmbigNQ;
- MuSiQue;
- one domain-specific dataset.

Methods:

- likelihood;
- verbal confidence;
- P(True);
- agreement;
- semantic entropy;
- learned logistic scorer;
- global conformal/LTT;
- one recent adaptive/conditional method;
- CCRC.

### 14.2 Stretch version

Only after the core results are complete:

- fourth model family;
- matched base/instruction study;
- long-form FActScore/SAFE appendix;
- retention under unrelated continued training;
- RAG comparison;
- hidden-state probe;
- online shift detection/recalibration.

### 14.3 Generation budget

Before launching the main run, compute:

\[
\text{total outputs}
=
\#\text{queries}
\times
\#\text{models}
\times
\#\text{decoding samples}
\times
\#\text{seeds/runs}
\]

Run a 1% dry run and extrapolate:

- wall time;
- GPU hours;
- disk;
- verifier cost;
- human-review load.

Do not start the full matrix until this estimate is approved.

---

## 15. Reproducible implementation plan

### 15.1 Repository layout

~~~text
calibread/
  README.md
  pyproject.toml
  uv.lock or requirements lock
  CITATION.cff
  LICENSE
  configs/
    models/
    datasets/
    generation/
    scorers/
    contracts/
    experiments/
  data/
    raw/
    interim/
    processed/
    manifests/
  src/calibread/
    data/
    synthetic/
    models/
    generation/
    grading/
    uncertainty/
    calibration/
    conformal/
    policies/
    metrics/
    statistics/
    reporting/
  scripts/
  tests/
  artifacts/
    predictions/
    scores/
    contracts/
    tables/
    figures/
  paper/
  preregistration/
~~~

### 15.2 Canonical JSONL record

~~~json
{
  "example_id": "world17_fact203_q4",
  "world_id": "world17",
  "fact_id": "fact203",
  "split": "calibrate",
  "query": "Who directs the Arven Observatory?",
  "valid_answers": ["Velora Nemin"],
  "answer_type": "entity",
  "factors": {
    "exposure": 8,
    "precision": "categorical",
    "temporal_status": "current",
    "ambiguity": 1,
    "hops": 1,
    "domain": "general"
  },
  "template_id": "query_director_04",
  "source": "controlled_v1",
  "license": "project-generated"
}
~~~

### 15.3 Prediction record

~~~json
{
  "run_id": "run_2026_09_14_001",
  "example_id": "world17_fact203_q4",
  "model_id": "frozen-model-id",
  "model_revision": "commit-or-hash",
  "prompt_hash": "sha256",
  "decode": {
    "temperature": 0.7,
    "top_p": 0.95,
    "seed": 17
  },
  "greedy_answer": "Velora Nemin",
  "samples": ["Velora Nemin", "Velora Nemin", "I do not know"],
  "token_logprobs": [],
  "latency_ms": 0,
  "gpu_seconds": 0
}
~~~

### 15.4 Contract artifact

~~~json
{
  "contract_id": "ccrc-v1-modelX-general-lowhop",
  "model_revision": "hash",
  "scorer_revision": "hash",
  "policy_revision": "hash",
  "calibration_manifest_hash": "sha256",
  "groups": ["general", "hops<=2"],
  "loss": "prediction_set_miscoverage",
  "target_risk": 0.05,
  "confidence": 0.95,
  "calibration_n": 842,
  "policy": {
    "max_samples": 5,
    "threshold": 0.71
  },
  "assumptions": ["exchangeable within declared scope"],
  "unsupported_scopes": ["post_cutoff", "unseen_domain"]
}
~~~

### 15.5 Reproducibility rules

- Store configurations, not notebook-only state.
- All tables and figures must be generated from immutable prediction files.
- Cache raw generations so metrics can be recomputed without inference.
- Hash prompts, datasets, splits, and model revisions.
- Use one command to reproduce each table.
- Pin dependencies.
- Record CUDA, driver, inference engine, quantization, and hardware.
- Unit-test conformal quantiles on small analytically checkable cases.
- Unit-test split leakage and group fallback.
- Add property tests: larger uncertainty threshold must produce the intended nested policy behavior where the theory requires monotonicity.
- Run a clean-machine reproduction before submission.

---

## 16. Six-month schedule

Assume 26 weeks.

### Weeks 1–2 — scope and novelty lock

Deliverables:

- related-work matrix;
- corrected definitions;
- one-page final RQs and hypotheses;
- resource inventory;
- model/data licenses;
- preregistration skeleton;
- supervisor sign-off.

Go/no-go:

- if CCRC is not distinct enough, commit to a benchmark/audit paper rather than forcing a weak algorithm claim.

### Weeks 3–4 — benchmark generator

Deliverables:

- micro-world schema;
- factor generators;
- held-out templates;
- split-by-world code;
- unified initial-stage and temporal-update corpus materialization from all R0–R7 suites;
- a fixed exposure assignment reused across model sizes and optimizer seeds;
- deterministic graders;
- 500-example hand audit;
- tests for factor independence and leakage.

Go/no-go:

- automatic label accuracy at least 99% on synthetic data;
- no split shares a connected entity graph.

### Weeks 5–6 — controlled knowledge injection pilot

Deliverables:

- training mix with exact exposures;
- one small and one 7B-scale pilot if resources allow;
- learning curves;
- proof that exposure levels produce nondegenerate accuracy differences;
- frozen injection recipe.

Fallback:

- if 7B fine-tuning is too expensive, run causal training on 1B and use natural-frequency validation on 7–9B models.

### Weeks 7–8 — generation and grading pipeline

Deliverables:

- batched inference;
- cached generations/logprobs;
- exact and numerical graders;
- abstention parser;
- run manifests;
- 1% end-to-end cost benchmark.

### Weeks 9–10 — uncertainty baselines

Deliverables:

- likelihood, P(True), verbal confidence, agreement, semantic entropy;
- scorer interface;
- LM-Polygraph comparison;
- preliminary risk-coverage curves;
- cluster-quality audit.

### Weeks 11–12 — natural datasets

Deliverables:

- immutable dataset snapshots;
- licenses and citations;
- canonical records;
- natural-data grading validation;
- decontamination/frequency metadata;
- initial domain-shift scores.

### Weeks 13–14 — conformal and risk-control reproduction

Deliverables:

- reproduce one published Conformal Language Modeling result or a small equivalent sanity test;
- reproduce standard split conformal coverage on a toy task;
- implement global policy;
- test calibration/test separation;
- write the exact guarantee and assumptions.

Go/no-go:

- no new method work until the published baseline passes.

### Weeks 15–16 — CCRC

Deliverables:

- profiler;
- group hierarchy;
- finite policy grid;
- risk testing with multiplicity control;
- unsupported-contract behavior;
- simulation verifying empirical validity under IID and showing failure under shift.

### Weeks 17–19 — development-side controlled experiments

Deliverables:

- generate and grade only fit, tune, and calibrate partitions;
- development-side main-effect curves;
- three core model configurations;
- canonical split integrity and checkpoint-gate results;
- runtime/cost data;
- automated integrity checks.

Freeze:

- do not access, generate, grade, summarize, or inspect locked-test outputs;
- freeze hypotheses, the single result per hypothesis, risk definitions, policy family, profiler, prompts, graders, exclusions, and analysis code at the end of week 19.

### Week 20 — calibration and final lock

Deliverables:

- fit scorers on fit only;
- select features and policy grids on tune only;
- calibrate policies and select the final passing configuration on calibrate only;
- archive hashes for code, prompts, graders, manifests, model checkpoints, calibration artifacts, and the signed preregistration.

### Week 21 — one-shot locked controlled evaluation

Deliverables:

- generate locked-test outputs for the first time;
- run the frozen grader and analysis exactly once;
- record every deviation without retuning;
- preserve the original locked output before any reanalysis;
- produce H1–H5 input tables and the worst-group audit.

### Week 22 — natural validation and shift

Deliverables:

- natural benchmark results with the week-21 controlled policies frozen;
- domain transfer matrix;
- temporal and reweighted-mixture shift analyses;
- target-domain recalibration study;
- explicit separation of confirmatory controlled and observational claims.

### Week 23 — statistics and figures

Deliverables:

- locked statistical analysis;
- confidence intervals;
- corrected p-values;
- effect-size tables;
- final figures and the H1–H5 decision table.

### Week 24 — ablations, error analysis, and first full paper

Deliverables:

- required ablations;
- blinded review of high-confidence errors and a frozen error taxonomy;
- a full paper draft covering introduction, related work, formal setup,
  benchmark, method, experiments, limitations, broader impact, and appendices.

### Week 25 — internal review and artifact

- supervisor/coauthor review;
- proof/statistics review;
- clean reproduction;
- anonymized repository;
- model/data cards;
- artifact documentation.

### Week 26 — revision and submission

- rebut obvious reviewer concerns in advance;
- verify every number against artifact output;
- archive data/code;
- prepare thesis chapter and conference version separately.

---

## 17. Paper structure

### Abstract

Five sentences:

1. Parametric LLM reads lack explicit reliability semantics.
2. Aggregate calibration hides structured complexity failures.
3. Introduce controlled CalibRead benchmark.
4. Introduce/evaluate complexity-conditioned read contracts.
5. State the two strongest numerical findings without universal claims.

### 1. Introduction

- motivating failure;
- why scalar hallucination is inadequate;
- why marginal guarantees are inadequate;
- contributions;
- scope: closed-book short-form factual reads.

### 2. Related work

- LLM factuality/calibration;
- semantic uncertainty;
- selective prediction/abstention;
- conformal language generation/factuality;
- conditional and shifted conformal prediction;
- factual and multihop benchmarks.

### 3. Formal setup

- parametric read;
- action space;
- risks;
- contract;
- assumptions.

### 4. CalibRead benchmark

- controlled worlds;
- natural validation;
- six factors;
- splits and grading.

### 5. CCRC

- uncertainty scorer;
- query profiler;
- policy family;
- calibration/risk tests;
- guarantees and limitations.

### 6. Experimental setup

- models;
- decoding;
- baselines;
- sample sizes;
- metrics;
- statistics;
- compute.

### 7. Results

Order:

1. failure surfaces;
2. uncertainty estimator comparison;
3. marginal versus group validity;
4. contract utility;
5. shift;
6. cost and ablations.

### 8. Limitations

- marginal/group rather than individual guarantees;
- exchangeability;
- scorer/labeler dependence;
- synthetic-to-natural gap;
- limited models/languages;
- closed-book scope;
- no proof against adversarial deployment;
- compute dependence.

### 9. Conclusion

Do not say hallucination is solved. Say the work makes the conditions and costs of a read guarantee measurable.

---

## 18. Required figures and tables

Required core figures:

1. Parametric read and CCRC action pipeline.
2. Six main-effect factual-error curves.
3. Risk-coverage curves by uncertainty estimator.
4. Aggregate versus worst-group coverage.
5. Domain calibration-transfer heatmap.
6. Utility-validity-cost Pareto frontier.
7. Calibration sample-size versus guarantee/utility.

An interaction surface may appear only as an exploratory appendix figure if the optional interaction study is actually run.

Tables:

1. Related-work comparison.
2. Dataset/factor mapping and sample counts.
3. Model revisions and decoding.
4. Confirmatory hypothesis results.
5. Contract validity under IID and shift.
6. Ablations.
7. Human-grading agreement.
8. Compute and carbon/energy estimate if required by venue.

Every plot should show sample counts, uncertainty bands, and target lines.

---

## 19. Failure modes and fallbacks

### Failure: synthetic facts are not learned

Actions:

- inspect loss and direct cloze accuracy;
- simplify names/tokenization;
- increase exposures;
- vary learning rate;
- verify answer rendering;
- reduce relation diversity;
- use a smaller base model/full fine-tuning pilot.

Do not proceed to calibration if base accuracy is degenerate at every exposure level.

### Failure: all models are nearly perfect or nearly random

Use pilot curves to move factor levels into the transition region. Freeze revised levels before the main run.

### Failure: semantic clustering is unreliable

Make exact/canonical short-answer tasks primary. Keep semantic clustering as a baseline/appendix. Audit NLI errors.

### Failure: CCRC gives no utility at 5% risk

Report the feasibility boundary. Evaluate 5%, 10%, and 20% risk levels fixed in advance. A negative result showing vacuous high-reliability contracts can be important.

### Failure: group cells are too small

Reduce the number of declared groups, merge only substantively justified neighboring levels, or back off hierarchically. Do not report unstable “guarantees.”

### Failure: model cutoffs are unclear

Avoid exact recency claims for that model. Use controlled updates and label the natural temporal study as observational.

### Failure: no method novelty remains

Submit as a benchmark/measurement paper with:

- causal controlled factors;
- subgroup failure of existing guarantees;
- standardized read contract schema;
- high-quality artifact.

### Failure: compute is limited

Priority order:

1. OLMo 1B controlled experiments;
2. one 7–9B external model;
3. main-effect cells;
4. semantic entropy at \(M=5\);
5. one natural dataset per construct;
6. interactions;
7. additional models;
8. long-form appendix.

---

## 20. Common reviewer attacks to prevent

- “The conformal method is not novel.”
  - Cite and reproduce the closest methods; narrow the contribution.
- “The guarantee is only marginal.”
  - State that clearly and audit groups; do not imply individual validity.
- “The correct answer may not be sampled.”
  - Include candidate-generation failure in the loss.
- “Frequency is guessed.”
  - Use exact controlled exposures for causal claims.
- “Recency is confused with forgetting.”
  - Separate availability, supersession, and retention.
- “Ambiguity is mislabeled hallucination.”
  - Evaluate actions and valid interpretation sets.
- “Multihop errors come from missing facts.”
  - condition on component availability.
- “ECE hides failures.”
  - include proper scoring rules and worst-group metrics.
- “LLM judge evaluates itself.”
  - exact synthetic labels and human validation.
- “Hyperparameters were chosen on test.”
  - four-way split and immutable manifests.
- “Too many correlated tests.”
  - five confirmatory hypotheses and Holm correction.
- “The method wins by abstaining on everything.”
  - report answer coverage and utility at fixed risk.
- “Results cannot be reproduced.”
  - freeze model revisions, prompts, splits, generations, and hashes.

---

## 21. First 14 days: exact checklist

### Day 1

- Create repository skeleton.
- Copy this blueprint into the repository.
- Write one paragraph defining “parametric read.”

### Day 2

- Build related-work spreadsheet.
- Add all papers in the references below.

### Day 3

- Read Conformal Language Modeling completely.
- Reproduce its exact guarantee in your own notation.

### Day 4

- Read conformal factuality and enhanced conditional validity work.
- Write a one-page difference memo.

### Day 5

- Read 2026 conditional/adaptive/shift papers.
- Decide whether CCRC is method novelty or only a systems composition.

### Day 6

- Confirm the already selected primary loss: false-commit risk per incoming query at target 0.05 and calibration confidence 0.95.
- Record answer coverage as primary utility and set miscoverage/selective risk as secondary analyses.

### Day 7

- Meet supervisor with:
  - final RQs;
  - five hypotheses;
  - novelty table;
  - compute tiers;
  - main risk definition.

### Day 8

- Implement micro-world and fact schemas.
- Generate 100 examples.

### Day 9

- Implement R1, R2, and R4.
- Unit-test exact factor values.

### Day 10

- Implement graph generation for R5.
- Verify no lexical shortcuts.

### Day 11

- Implement train/calibrate/test grouping by world.
- Add a test that detects entity leakage.

### Day 12

- Implement answer normalization and numeric/date grading.
- Hand-grade 100 records.

### Day 13

- Run a tiny model end to end.
- Save generation and manifest artifacts.

### Day 14

- Produce one pilot curve and one risk-coverage curve.
- Estimate full compute and storage.
- Freeze the next four-week milestone.

---

## 22. Recommended repositories

Use them as references or components; do not combine them blindly.

### Uncertainty

- [LM-Polygraph](https://github.com/IINemo/lm-polygraph): broad uncertainty-estimation framework and benchmark.
- [Current semantic uncertainty implementation](https://github.com/jlko/semantic_uncertainty): reproduces the Nature semantic-entropy experiments. Use this, not the deprecated earlier repository.
- [Uncertainty in the Wild](https://github.com/duygunuryldz/uncertainty_in_the_wild): robustness and threshold-shift experiments.

### Conformal prediction

- [TorchCP](https://github.com/ml-stat-Sustech/TorchCP): tested conformal primitives and an implementation of Conformal Language Modeling.
- [General conformal prediction examples](https://github.com/aangelopoulos/conformal-prediction): reference notebooks and theory-oriented examples.
- [Batch Multivalid Conformal](https://github.com/ProgBelarus/BatchMultivalidConformal): group-conditional/multivalid reference.

### Datasets/evaluation

- [AbstentionBench](https://github.com/facebookresearch/AbstentionBench): abstention across unknown, ambiguous, false-premise, and outdated questions.
- [MuSiQue](https://github.com/StonyBrookNLP/musique): official multihop dataset and evaluator.
- [FreshQA](https://github.com/freshllms/freshqa): dated changing-knowledge snapshots; freeze the snapshot.
- [FActScore](https://github.com/shmsw25/FActScore): optional long-form factual precision.
- [Long-form factuality/SAFE](https://github.com/google-deepmind/long-form-factuality): optional long-form appendix.
- [SimpleQA evaluator](https://github.com/openai/simple-evals): short-form factuality baseline.

### Transparent models

- [OLMo](https://github.com/allenai/olmo): training code, configurations, checkpoints, and transparent data information.
- [Pythia](https://github.com/EleutherAI/pythia): alternative scaling/checkpoint family trained on the same data order; useful for training-dynamics ablations.
- [OLMES](https://github.com/allenai/olmes): reproducible evaluation tooling.

Repository use policy:

- pin a commit;
- record license;
- isolate third-party code behind adapters;
- do not modify upstream code without tracking the patch;
- validate output against a tiny known case;
- cite both paper and repository.

---

## 23. Core reading list

### Conformal prediction and risk control

- Quach et al., [Conformal Language Modeling](https://proceedings.iclr.cc/paper_files/paper/2024/hash/31421b112e5f7faf4fc577b74e45dab2-Abstract-Conference.html), ICLR 2024.
- Mohri and Hashimoto, [Language Models with Conformal Factuality Guarantees](https://proceedings.mlr.press/v235/mohri24a.html), ICML 2024.
- Cherian, Gibbs, and Candès, [Large Language Model Validity via Enhanced Conformal Prediction Methods](https://arxiv.org/abs/2406.09714), NeurIPS 2024.
- Angelopoulos et al., [Conformal Risk Control](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f3549ef9b5ff520a7e41ff3cc306ab2b-Abstract-Conference.html), ICLR 2024.
- Angelopoulos et al., [Learn then Test](https://arxiv.org/abs/2110.01052).
- Fisch et al., [Conformal Prediction Sets with Limited False Positives](https://arxiv.org/abs/2202.07650), ICML 2022.
- Tibshirani et al., [Conformal Prediction Under Covariate Shift](https://papers.neurips.cc/paper_files/paper/2019/hash/8fb21ee7a2207526da55a679f0332de2-Abstract.html), NeurIPS 2019.
- Jung et al., [Batch Multivalid Conformal Prediction](https://arxiv.org/abs/2209.15145).
- Hu et al., [CoFact: Conformal Factuality Guarantees for Language Models Under Covariate Shift](https://openreview.net/pdf?id=eiBp7rsc3K), ICLR 2026.
- Ye, Pan, and Li, [Conditional Factuality Controlled LLMs with Generalization Certificates via Conformal Sampling](https://arxiv.org/abs/2603.27403), CVPR 2026.
- Rubashevskii et al., [Adaptive Conformal Prediction for Improving Factuality of Generations by Large Language Models](https://arxiv.org/abs/2604.13991), 2026.

### Calibration and uncertainty

- Jiang et al., [How Can We Know When Language Models Know?](https://aclanthology.org/2021.tacl-1.57/), TACL 2021.
- Kadavath et al., [Language Models (Mostly) Know What They Know](https://arxiv.org/abs/2207.05221), 2022.
- Kuhn et al., [Detecting Hallucinations in Large Language Models Using Semantic Entropy](https://www.nature.com/articles/s41586-024-07421-0), Nature 2024.
- Fadeeva et al., [LM-Polygraph](https://aclanthology.org/2023.emnlp-demo.41/), EMNLP 2023.
- Bakman et al., [Reconsidering LLM Uncertainty Estimation Methods in the Wild](https://aclanthology.org/2025.acl-long.1429/), ACL 2025.
- Wen et al., [Know Your Limits: A Survey of Abstention in Large Language Models](https://aclanthology.org/2025.tacl-1.26/), TACL 2025.

### Knowledge and benchmark design

- Kandpal et al., [Large Language Models Struggle to Learn Long-Tail Knowledge](https://proceedings.mlr.press/v202/kandpal23a.html), ICML 2023.
- Min et al., [AmbigQA](https://aclanthology.org/2020.emnlp-main.466/), EMNLP 2020.
- Trivedi et al., [MuSiQue](https://aclanthology.org/2022.tacl-1.31/), TACL 2022.
- Min et al., [FActScore](https://aclanthology.org/2023.emnlp-main.741/), EMNLP 2023.
- Wei et al., [Measuring Short-Form Factuality in Large Language Models / SimpleQA](https://arxiv.org/abs/2411.04368), 2024.
- Kirichenko et al., [AbstentionBench](https://arxiv.org/abs/2506.09038), 2025.

---

## 24. Final success criteria

The thesis is complete when:

- the six factors have precise operational definitions;
- causal claims rely on controlled exposures, not guessed corpus statistics;
- all data partitions are fact/world-disjoint;
- at least three model configurations complete the core matrix;
- the principal uncertainty baselines are reproduced;
- the closest conformal baseline is reproduced;
- the contract controls one explicitly defined risk;
- aggregate and subgroup validity are both measured;
- shift failures are reported rather than hidden;
- results include usefulness and cost;
- confirmatory hypotheses are analyzed on a locked test set;
- the artifact recreates every main table and figure;
- the paper’s novelty claim survives direct comparison with 2024–2026 conformal LLM work.

The most valuable possible result is not necessarily that CCRC always succeeds. A rigorous map showing **where reliability contracts are feasible, where they become vacuous, and which complexity regimes break them** is itself a meaningful research contribution.
