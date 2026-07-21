# CalibRead annotated reference guide

Last verified: 22 July 2026

This is the working literature guide for **CalibRead: Parametric Complexity
Analysis of Probabilistic Read Reliability in LLM Knowledge Systems**. It is
not merely a list of related papers: every item below states why it matters,
where it belongs in the paper, and which CalibRead research dimensions or
hypotheses it supports.

The companion BibTeX database is
[`calibread_references.bib`](calibread_references.bib). Citation keys appear in
backticks below. Metadata has been checked against primary publisher,
proceedings, OpenReview, arXiv, or official repository pages. Recheck preprint
publication status immediately before the final submission.

## How to use this file

- **Core** means the paper should normally appear in the main paper.
- **Methods** means it directly informs experimental or statistical design.
- **Evaluation** means it supplies a task, metric, benchmark, or comparison.
- **Context** means it locates the contribution but may move to an appendix if
  space is tight.
- **Preprint** means the idea can be discussed, but its review status must be
  described accurately.
- Cite a work for the particular claim described here; do not attach a long
  chain of citations to a broader claim that none of them directly tests.
- For datasets and code, cite both the paper and the exact software/data
  revision used in the experiment manifest.

## Minimum reading order

Read these first, in this order:

1. Shafer and Vovk (`shafer2008tutorial`) for the conformal prediction base.
2. Angelopoulos et al. (`angelopoulos2024crc`) for risk control beyond simple
   classification coverage.
3. Quach et al. (`quach2024conformal`) for set-valued language generation.
4. Mohri and Hashimoto (`mohri2024factuality`) for conformal factuality and
   back-off behavior.
5. Cherian et al. (`cherian2024validity`) for conditional validity and improved
   scoring.
6. Jiang et al. (`jiang2021calibration`) and Kadavath et al.
   (`kadavath2022mostly`) for confidence elicitation in language models.
7. Farquhar et al. (`farquhar2024semantic`) for semantic uncertainty.
8. Kandpal et al. (`kandpal2023memorization`) for knowledge frequency and H1.
9. Bakman et al. (`bakman2025wild`) for calibration-distribution shift and H5.
10. Wen et al. (`wen2025abstention`) for the abstention taxonomy and baselines.
11. Min et al. (`min2023factscore`) plus Wei et al. (`wei2024simpleqa`) for
    factuality evaluation design.
12. He and Thinking Machines Lab (`he2025nondeterminism`) for deterministic
    inference controls; treat this as an engineering source, not statistical
    proof of model determinism.

## 1. Foundations: calibration, selective prediction, and conformal prediction

### Shafer and Vovk (2008) — tutorial on conformal prediction

**Key:** `shafer2008tutorial` · **Priority:** Core, Methods

Glenn Shafer and Vladimir Vovk. “A Tutorial on Conformal Prediction.” *Journal
of Machine Learning Research* 9(12):371–421, 2008.
[Publisher page](https://www.jmlr.org/papers/v9/shafer08a.html)

Why it matters: establishes the exchangeability-based framework, nonconformity
scores, and finite-sample marginal coverage language. Use it when defining what
the CalibRead guarantee does and does not cover. It is especially important for
preventing claims of per-example, per-domain, or causal validity from a merely
marginal guarantee.

Use in CalibRead: formal setup; calibration/test split; coverage theorem and
assumptions; limitations of H3–H5.

### Guo et al. (2017) — neural-network calibration

**Key:** `guo2017calibration` · **Priority:** Core, Methods

Chuan Guo, Geoff Pleiss, Yu Sun, and Kilian Q. Weinberger. “On Calibration of
Modern Neural Networks.” *ICML*, 2017.
[PMLR page](https://proceedings.mlr.press/v70/guo17a.html)

Why it matters: standard source for expected calibration error and temperature
scaling. It also supplies a warning for the thesis: a low binned ECE is not a
selective-risk guarantee and can conceal failures in small or hard groups.

Use in CalibRead: confidence baseline; reliability diagrams; temperature
scaling; motivation for reporting ECE alongside Brier, NLL, risk–coverage, and
worst-group gaps rather than as the sole endpoint.

### Geifman and El-Yaniv (2017) — selective classification

**Key:** `geifman2017selective` · **Priority:** Core, Methods

Yonatan Geifman and Ran El-Yaniv. “Selective Classification for Deep Neural
Networks.” arXiv:1705.08500, 2017.
[arXiv](https://arxiv.org/abs/1705.08500)

Why it matters: formalizes prediction with a reject option and the relationship
between risk and retained coverage.

Use in CalibRead: define the answer/abstain policy, risk–coverage curve, AURC,
and the equal-risk utility comparison in H4/R7.

### Angelopoulos et al. (2022) — Learn then Test

**Key:** `angelopoulos2022learn` · **Priority:** Methods

Anastasios N. Angelopoulos, Stephen Bates, Emmanuel J. Candès, Michael I.
Jordan, and Lihua Lei. “Learn then Test: Calibrating Predictive Algorithms to
Achieve Risk Control.” arXiv:2110.01052, 2022.
[arXiv](https://arxiv.org/abs/2110.01052)

Why it matters: separates learning candidate procedures from statistically
testing which ones satisfy a risk constraint. This is a clean template for
choosing CalibRead policies on fit/tune data and validating the frozen policy
without test leakage.

Use in CalibRead: policy selection; multiple candidate thresholds; H4 validity
gate before comparing utility.

### Angelopoulos et al. (2024) — conformal risk control

**Key:** `angelopoulos2024crc` · **Priority:** Core, Methods

Anastasios Angelopoulos, Stephen Bates, Adam Fisch, Lihua Lei, and Tal Schuster.
“Conformal Risk Control.” *ICLR*, 2024.
[ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f3549ef9b5ff520a7e41ff3cc306ab2b-Abstract-Conference.html)

Why it matters: extends conformal calibration to monotone, bounded loss
functions. This is the most direct foundation for controlling false commits,
selective factual error, or other risks instead of only set miscoverage.

Use in CalibRead: global risk-controlled baseline; H3 aggregate versus group
validity; H4 equal-risk policy comparison; R7 threshold calibration.

### Fisch et al. (2022) — limited false positives

**Key:** `fisch2022limited` · **Priority:** Methods

Adam Fisch, Tal Schuster, Tommi Jaakkola, and Regina Barzilay. “Conformal
Prediction Sets with Limited False Positives.” arXiv:2202.07650, 2022.
[arXiv](https://arxiv.org/abs/2202.07650)

Why it matters: studies prediction sets where the harmful event is including
too many false positives. This is relevant if CalibRead returns multiple
answers, interpretations, or claims and the contract penalizes unsupported set
members.

Use in CalibRead: optional set-valued contract for R4 ambiguity; false-member
loss; sensitivity analysis distinct from answer/abstain evaluation.

### Tibshirani et al. (2019) — conformal prediction under covariate shift

**Key:** `tibshirani2019covariate` · **Priority:** Core, Methods

Ryan J. Tibshirani, Rina Foygel Barber, Emmanuel Candès, and Aaditya Ramdas.
“Conformal Prediction Under Covariate Shift.” *NeurIPS*, 2019.
[NeurIPS proceedings](https://papers.neurips.cc/paper_files/paper/2019/hash/8fb21ee7a2207526da55a679f0332de2-Abstract.html)

Why it matters: provides a principled importance-weighted response to a
particular distribution-shift setting. It is not a universal cure for arbitrary
domain or label shift.

Use in CalibRead: importance-weighting comparator in H5; specify density-ratio,
support-overlap, and shift assumptions; contrast with unchanged and small-target
recalibration.

### Jung et al. (2022) — batch multivalid conformal prediction

**Key:** `jung2022multivalid` · **Priority:** Methods, Context

Christopher Jung, Georgy Noarov, Ramya Ramalingam, and Aaron Roth. “Batch
Multivalid Conformal Prediction.” arXiv:2209.15145, 2022.
[arXiv](https://arxiv.org/abs/2209.15145)

Why it matters: targets validity across many intersecting groups rather than
only in aggregate. This is a key comparator and conceptual precursor for
complexity-conditioned calibration.

Use in CalibRead: H3 group diagnostics; H4 multigroup/conditional baseline;
discussion of the sample-size and multiplicity costs of finer groups.

## 2. Conformal prediction for language and factuality

### Quach et al. (2024) — conformal language modeling

**Key:** `quach2024conformal` · **Priority:** Core, Methods

Victor Quach, Adam Fisch, Tal Schuster, Adam Yala, Jae Ho Sohn, Tommi Jaakkola,
and Regina Barzilay. “Conformal Language Modeling.” *ICLR*, 2024.
[ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/31421b112e5f7faf4fc577b74e45dab2-Abstract-Conference.html)

Why it matters: calibrates language-model sampling, stopping, and rejection to
produce output sets with distribution-free guarantees. It is the closest
general language-generation predecessor to CalibRead.

Use in CalibRead: language-output sets; sampled candidate construction; global
conformal baseline; explain how CalibRead differs by explicitly modeling six
parametric complexity factors R1–R6, with R7 as a separate policy stress suite,
and testing conditional reliability.

### Mohri and Hashimoto (2024) — conformal factuality guarantees

**Key:** `mohri2024factuality` · **Priority:** Core, Methods

Christopher Mohri and Tatsunori Hashimoto. “Language Models with Conformal
Factuality Guarantees.” *ICML*, 2024, PMLR 235:36029–36047.
[PMLR page](https://proceedings.mlr.press/v235/mohri24a.html)

Why it matters: directly addresses factuality risk and uses a hierarchy of
back-off responses. This is a central baseline for any CalibRead claim about
reliable reads rather than generic token prediction.

Use in CalibRead: set/back-off comparator; atomic-claim factuality loss;
selective contract; contrast their global guarantee with CalibRead’s
complexity-conditioned diagnosis and H3/H5 failure analysis.

### Cherian, Gibbs, and Candès (2024) — enhanced conformal prediction for LLM validity

**Key:** `cherian2024validity` · **Priority:** Core, Methods

John J. Cherian, Isaac Gibbs, and Emmanuel J. Candès. “Large Language Model
Validity via Enhanced Conformal Prediction Methods.” *NeurIPS*, 2024.
[arXiv](https://arxiv.org/abs/2406.09714)

Why it matters: develops conditional procedures and improved scoring for LLM
validity. It should be treated as a serious modern baseline, not just related
work.

Use in CalibRead: conditional-scoring comparator; H3/H4; motivate why the
complexity profile must be preregistered or cross-fitted rather than selected
after seeing group failures.

### Hu et al. (2026) — CoFact

**Key:** `hu2026cofact` · **Priority:** Core, Current comparator

Zirui Hu, Zheng Zhang, Yingjie Wang, Leszek Rutkowski, and Dacheng Tao.
“CoFact: Conformal Factuality Guarantees for Language Models Under Covariate
Shift.” *ICLR*, 2026.
[OpenReview](https://openreview.net/forum?id=eiBp7rsc3K)

Why it matters: a current peer-reviewed treatment of conformal factuality under
covariate shift. Because it is contemporaneous with the thesis and overlaps H5,
omitting it would make the baseline set appear dated.

Use in CalibRead: current conformal-factuality comparator; paper-positioning
table; H4 validity/utility frontier. Reproduce only after pinning the authors’
official implementation or recording that no implementation was available.

### Ye, Pan, and Li (2026) — conditional factuality calibration

**Key:** `ye2026conditional` · **Priority:** Core, Preprint/current comparator

Kai Ye, Qingtao Pan, and Shuo Li. “Conditional Factuality Controlled LLMs with
Generalization Certificates via Conformal Sampling.” arXiv:2603.27403; listed
for *CVPR 2026*.
[arXiv](https://arxiv.org/abs/2603.27403)

Why it matters: proposes feature-conditional thresholds and a PAC-style
variant, making it particularly close to CalibRead’s complexity-conditioned
policy.

Use in CalibRead: closest-method comparison for H4; explicitly distinguish
their learned conditional calibration target from CalibRead’s controlled
factorial measurement contribution and R0 controls/R1–R6 factors/R7 stress
testbed. Recheck final proceedings
status before citation.

### Rubashevskii et al. (2026) — adaptive conformal factuality

**Key:** `rubashevskii2026adaptive` · **Priority:** Preprint/current comparator

Aleksandr Rubashevskii, Dzianis Piatrashyn, Preslav Nakov, and Maxim Panov.
“Adaptive Conformal Prediction for Improving Factuality of Generations by Large
Language Models.” arXiv:2604.13991, 2026.
[arXiv](https://arxiv.org/abs/2604.13991)

Why it matters: adapts scores to prompt-level variation, directly overlapping
the problem of heterogeneous factual difficulty.

Use in CalibRead: H4 continuous adaptive comparator and ablation against
discrete factor groups. Label it as a preprint unless a reviewed venue is
confirmed.

## 3. LLM calibration, uncertainty, and abstention

### Jiang et al. (2021) — calibration in pre-trained language models

**Key:** `jiang2021calibration` · **Priority:** Core

Zhengbao Jiang, Jun Araki, Haibo Ding, and Graham Neubig. “How Can We Know When
Language Models Know? On the Calibration of Language Models for Question
Answering.” *TACL* 9:962–977, 2021.
[ACL Anthology](https://aclanthology.org/2021.tacl-1.57/)

Why it matters: early direct evidence on QA confidence calibration and methods
for obtaining confidence from language models.

Use in CalibRead: confidence-prompt baseline; calibration related work;
reliability diagrams and ECE cautions across R1–R6.

### Kadavath et al. (2022) — models estimating their own correctness

**Key:** `kadavath2022mostly` · **Priority:** Core, Methods

Saurav Kadavath et al. “Language Models (Mostly) Know What They Know.”
arXiv:2207.05221, 2022.
[arXiv](https://arxiv.org/abs/2207.05221)

Why it matters: introduces and studies P(True) and P(IK)-style self-evaluation.
These are natural black-box uncertainty baselines but must not be interpreted as
guarantees.

Use in CalibRead: uncertainty features; answer-probability and self-critique
baselines; model-scale interaction in H1; predicted profiler features in H4.

### Farquhar et al. (2024) — semantic entropy

**Key:** `farquhar2024semantic` · **Priority:** Core, Methods

Sebastian Farquhar, Jannik Kossen, Lorenz Kuhn, and Yarin Gal. “Detecting
Hallucinations in Large Language Models Using Semantic Entropy.” *Nature*
630:625–630, 2024.
[Nature](https://www.nature.com/articles/s41586-024-07421-0)

Why it matters: aggregates uncertainty over semantic equivalence classes rather
than surface-form sequences. That distinction is critical when paraphrases are
not different answers.

Use in CalibRead: sampling-based uncertainty baseline; R0 paraphrase controls;
R4 ambiguity; H4 feature ablation. Record the semantic-clustering model and
threshold because they introduce their own error and cost.

### Fadeeva et al. (2023) — LM-Polygraph

**Key:** `fadeeva2023lmpolygraph` · **Priority:** Methods, Software

Ekaterina Fadeeva et al. “LM-Polygraph: Uncertainty Estimation for Language
Models.” *EMNLP System Demonstrations*, 2023.
[ACL Anthology](https://aclanthology.org/2023.emnlp-demo.41/) ·
[Official repository](https://github.com/IINemo/lm-polygraph)

Why it matters: provides a common implementation of many white-box and
black-box uncertainty estimators, reducing accidental differences between
baselines.

Use in CalibRead: estimator library for entropy, mutual-information, semantic,
and density-based baselines. Pin the package commit and independently validate
score direction, batching, and tokenizer assumptions.

### Bakman et al. (2025) — uncertainty estimation in the wild

**Key:** `bakman2025wild` · **Priority:** Core, Evaluation

Yavuz Faruk Bakman et al. “Reconsidering LLM Uncertainty Estimation Methods in
the Wild.” *ACL*, 2025, pp. 29531–29556.
[ACL Anthology](https://aclanthology.org/2025.acl-long.1429/) ·
[Official repository](https://github.com/duygunuryldz/uncertainty_in_the_wild)

Why it matters: evaluates uncertainty when calibration and evaluation
distributions differ and reports substantial threshold sensitivity under
shift. This is direct motivation for H5.

Use in CalibRead: in-the-wild external validation; shift-aware uncertainty
baselines; source→target threshold-transfer matrix; evidence for why pooled
calibration cannot be assumed to transfer.

### Wen et al. (2025) — abstention survey

**Key:** `wen2025abstention` · **Priority:** Core, Context

Bingbing Wen, Jihan Yao, Shangbin Feng, Chenjun Xu, Yulia Tsvetkov, Bill Howe,
and Lucy Lu Wang. “Know Your Limits: A Survey of Abstention in Large Language
Models.” *TACL* 13:529–556, 2025.
[ACL Anthology](https://aclanthology.org/2025.tacl-1.26/)

Why it matters: supplies the taxonomy for abstention, confidence estimation,
training-time methods, and evaluation.

Use in CalibRead: related-work organization; R7 policy taxonomy; selection of
representative rather than redundant baselines; limitations and deployment
discussion.

### Bai and Jin (2026) — selective conformal risk control

**Key:** `bai2026score` · **Priority:** Methods, Secondary contract

Tian Bai and Ying Jin. “Conformal Selective Prediction with General Risk
Control.” arXiv:2603.24704, 2026.
[arXiv](https://arxiv.org/abs/2603.24704)

Why it matters: SCoRE targets risk among selected/trusted cases, which is closer
to selective risk than ordinary split-conformal coverage. It is relevant to the
secondary Mode C analysis, not evidence for the primary false-commit contract.
Verify the preprint version and proof assumptions again before implementation.

## 4. Parametric knowledge, complexity factors, and factuality benchmarks

### Kandpal et al. (2023) — knowledge frequency and memorization

**Key:** `kandpal2023memorization` · **Priority:** Core, Evaluation

Nikhil Kandpal, Haikang Deng, Adam Roberts, Eric Wallace, and Colin Raffel. “Large
Language Models Struggle to Learn Long-Tail Knowledge.” *ICML*, 2023, PMLR
202:15696–15707.
[PMLR page](https://proceedings.mlr.press/v202/kandpal23a.html)

Why it matters: relates pretraining document frequency to factual QA behavior.
It is the principal observational predecessor for CalibRead’s controlled
exposure-frequency experiment.

Use in CalibRead: H1/R1 motivation and external validation. The thesis’s added
value is exact controlled exposure, held-out synthetic worlds, multiple seeds,
and calibration/selective-risk endpoints rather than only natural-corpus
frequency correlations.

### Mallen et al. (2023) — PopQA and long-tail parametric memory

**Key:** `mallen2023popqa` · **Priority:** Evaluation

Alex Mallen et al. “When Not to Trust Language Models: Investigating
Effectiveness of Parametric and Non-Parametric Memories.” *ACL*, 2023,
pp. 9802–9822.
[ACL Anthology](https://aclanthology.org/2023.acl-long.546/)

Use in CalibRead: observational external validation of R1. PopQA's natural
popularity measurements cannot replace the exact controlled exposure treatment.

### Lin et al. (2022) — TruthfulQA

**Key:** `lin2022truthfulqa` · **Priority:** Evaluation context

Stephanie Lin, Jacob Hilton, and Owain Evans. “TruthfulQA: Measuring How Models
Mimic Human Falsehoods.” *ACL*, 2022, pp. 3214–3252.
[ACL Anthology](https://aclanthology.org/2022.acl-long.229/)

Use in CalibRead: natural misconception/falsehood stress context. It is not a
controlled factor suite and should not be pooled into confirmatory H1–H5 tests.

### Joshi et al. (2017) — TriviaQA

**Key:** `joshi2017triviaqa` · **Priority:** Optional external evaluation

Mandar Joshi, Eunsol Choi, Daniel Weld, and Luke Zettlemoyer. “TriviaQA: A Large
Scale Distantly Supervised Challenge Dataset.” *ACL*, 2017, pp. 1601–1611.
[ACL Anthology](https://aclanthology.org/P17-1147/)

Use in CalibRead: optional open-domain frequency validation with a separately
versioned corpus-frequency estimator; do not treat distant supervision as the
same label quality as the synthetic exact graders.

### Tsatsaronis et al. (2015) — BioASQ

**Key:** `tsatsaronis2015bioasq` · **Priority:** Domain external evaluation

George Tsatsaronis et al. “An Overview of the BioASQ Large-Scale Biomedical
Semantic Indexing and Question Answering Competition.” *BMC Bioinformatics*
16:138, 2015.
[PubMed](https://pubmed.ncbi.nlm.nih.gov/25925131/)

Use in CalibRead: R6 biomedical external validation. Freeze a specific BioASQ
task/year and confirm its access and redistribution terms before use.

### Min et al. (2020) — AmbigQA

**Key:** `min2020ambigqa` · **Priority:** Evaluation

Sewon Min, Julian Michael, Hannaneh Hajishirzi, and Luke Zettlemoyer. “AmbigQA:
Answering Ambiguous Open-domain Questions.” *EMNLP*, 2020, pp. 5783–5797.
[ACL Anthology](https://aclanthology.org/2020.emnlp-main.466/)

Why it matters: distinguishes multiple legitimate interpretations and answers,
which prevents the R4 ambiguity suite from collapsing into ordinary QA error.

Use in CalibRead: natural validation for R4; interpretation-set evaluation;
scoring rules that do not mark a valid alternative as hallucinated.

### Trivedi et al. (2022) — MuSiQue

**Key:** `trivedi2022musique` · **Priority:** Evaluation

Harsh Trivedi, Niranjan Balasubramanian, Tushar Khot, and Ashish Sabharwal.
“MuSiQue: Multihop Questions via Single-hop Question Composition.” *TACL*
10:539–554, 2022.
[ACL Anthology](https://aclanthology.org/2022.tacl-1.31/) ·
[Official repository](https://github.com/StonyBrookNLP/musique)

Why it matters: explicitly composes multihop questions from single-hop
components, matching H2’s need to compare component retrievability with joint
synthesis success.

Use in CalibRead: external R5 validation; component probes; graph-level
bootstrap; observed versus independent per-hop error. Do not mix its natural
confounds with the primary controlled R5 estimate.

### Min et al. (2023) — FActScore

**Key:** `min2023factscore` · **Priority:** Core, Evaluation

Sewon Min et al. “FActScore: Fine-grained Atomic Evaluation of Factual Precision
in Long Form Text Generation.” *EMNLP*, 2023, pp. 12076–12100.
[ACL Anthology](https://aclanthology.org/2023.emnlp-main.741/) ·
[Official repository](https://github.com/shmsw25/FActScore)

Why it matters: decomposes long-form generations into atomic claims and scores
their support. It is useful when CalibRead moves beyond short answers.

Use in CalibRead: atomic-claim evaluation; false-claim risk; long-form secondary
experiment. Do not use an automated FActScore judgment as unquestioned ground
truth—validate a stratified subset with humans and report judge model/version.

### Wei et al. (2024) — SimpleQA

**Key:** `wei2024simpleqa` · **Priority:** Core, Evaluation

Jason Wei, Karina Nguyen, Hyung Won Chung, Yunxin Joy Jiao, Spencer Papay, Amelia
Glaese, John Schulman, William Fedus. “Measuring Short-form Factuality in Large
Language Models.” arXiv:2411.04368, 2024.
[arXiv](https://arxiv.org/abs/2411.04368) ·
[Official evaluation code](https://github.com/openai/simple-evals)

Why it matters: provides a simple short-answer factuality setup with explicit
correct, incorrect, and not-attempted outcomes.

Use in CalibRead: external short-form benchmark; answer/abstain grader design;
false-commit and attempted-coverage metrics. Keep SimpleQA results separate from
controlled causal claims.

### Kirichenko et al. (2025) — AbstentionBench

**Key:** `kirichenko2025abstentionbench` · **Priority:** Evaluation, Preprint

Polina Kirichenko, Mark Ibrahim, Kamalika Chaudhuri, and Samuel J. Bell.
“AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions.”
arXiv:2506.09038, 2025.
[arXiv](https://arxiv.org/abs/2506.09038) ·
[Official repository](https://github.com/facebookresearch/AbstentionBench)

Why it matters: focuses on unanswerable inputs, which are essential negative
controls for measuring confident false commits.

Use in CalibRead: R0 unanswerable/false-premise validation; R7 abstention
behavior; compare “correct abstention” separately from factual answer accuracy.

### Vu et al. (2023) — FreshLLMs/FreshQA

**Key:** `vu2023freshllms` · **Priority:** Evaluation, Preprint

Tu Vu et al. “FreshLLMs: Refreshing Large Language Models with Search Engine
Augmentation.” arXiv:2310.03214, 2023.
[arXiv](https://arxiv.org/abs/2310.03214) ·
[Official repository](https://github.com/freshllms/freshqa)

Why it matters: FreshQA includes current, changing, and false-premise
questions, making it useful for temporal-freshness behavior.

Use in CalibRead: external R3 validation. Version every question and annotation
snapshot because freshness labels change over time; never treat the live set as
a stable locked test without archiving it.

### Team OLMo et al. (2025) — OLMo 2

**Key:** `olmo2025furious` · **Priority:** Model methodology

Team OLMo et al. “2 OLMo 2 Furious.” arXiv:2501.00656, 2025.
[arXiv](https://arxiv.org/abs/2501.00656) ·
[Official repository](https://github.com/allenai/OLMo)

Use in CalibRead: justify the transparent controlled-model family and pin exact
model/tokenizer/checkpoint revisions. The paper documents 7B/13B releases; if a
1B derivative is used, cite and record that exact release separately.

### Biderman et al. (2023) — Pythia

**Key:** `biderman2023pythia` · **Priority:** Model alternative

Stella Biderman et al. “Pythia: A Suite for Analyzing Large Language Models
Across Training and Scaling.” *ICML*, 2023, PMLR 202:2397–2430.
[PMLR page](https://proceedings.mlr.press/v202/biderman23a.html)

Use in CalibRead: optional matched-data-order scaling/checkpoint family. Do not
mix it with OLMo results without an explicit architecture-family effect.

## 5. Determinism and experimental systems

### He and Thinking Machines Lab (2025) — defeating inference nondeterminism

**Key:** `he2025nondeterminism` · **Priority:** Engineering, Methods context

Horace He and Thinking Machines Lab. “Defeating Nondeterminism in LLM
Inference.” 10 September 2025.
[Article](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/) ·
[Companion repository](https://github.com/thinking-machines-lab/batch_invariant_ops)

Why it matters: demonstrates that fixed seeds and temperature zero do not by
themselves ensure identical outputs. Batch composition and reduction order can
alter floating-point results; batch-invariant kernels can remove an important
source of run-to-run variation.

Use in CalibRead: R0 infrastructure repeatability gate; deterministic greedy
evaluation; run manifests; batching controls. Report exact hardware, kernels,
parallelism, batch construction, server version, and request order. This source
does not eliminate the need for repeated-run audits and does not imply that
sampled generations should be forced to be identical.

### Batch Invariant Ops software

**Key:** `thinkingmachines2025batchops` · **Priority:** Software

Official proof-of-concept batch-invariant kernels from Thinking Machines Lab.
Pin a commit if used. As of the review performed for this thesis, the project
described itself as alpha/proof-of-concept software; benchmark compatibility and
performance on the chosen model stack before adopting it.

Use in CalibRead: optional deterministic-kernel backend, not a universal
dependency. The vLLM proof-of-concept pull request associated with this work was
closed and unmerged, so do not assume stock vLLM provides this behavior.
[vLLM proof-of-concept PR](https://github.com/vllm-project/vllm/pull/24583)

### TorchCP

**Key:** `torchcpsoftware` · **Priority:** Software

[TorchCP](https://github.com/ml-stat-Sustech/TorchCP) is a general PyTorch
conformal-prediction library. It can accelerate baseline implementation, but
the final methods must still be verified against the equations and small
hand-computed examples.

Use in CalibRead: standard conformal quantiles and risk-control scaffolding;
unit-test oracle; not a substitute for documenting the exact finite-sample
correction and randomized/tie behavior used.

## 6. Software and model repositories to pin in the experiment manifest

These are implementation resources, not all of them bibliographic evidence.
Record repository URL, full commit SHA, license, environment lockfile, model
revision, and local modifications.

| Resource | Repository | Intended role |
|---|---|---|
| LM-Polygraph | <https://github.com/IINemo/lm-polygraph> | uncertainty estimators |
| Semantic uncertainty | <https://github.com/jlko/semantic_uncertainty> | current semantic-entropy reference implementation; the older Lorenz Kuhn repository is deprecated |
| Uncertainty in the wild | <https://github.com/duygunuryldz/uncertainty_in_the_wild> | H5 shift baselines/data |
| TorchCP | <https://github.com/ml-stat-Sustech/TorchCP> | conformal utilities |
| Batch multivalid CP | <https://github.com/ProgBelarus/BatchMultivalidConformal> | multigroup comparator |
| AbstentionBench | <https://github.com/facebookresearch/AbstentionBench> | unanswerable external evaluation |
| MuSiQue | <https://github.com/StonyBrookNLP/musique> | multihop external evaluation |
| FreshQA | <https://github.com/freshllms/freshqa> | temporal external evaluation |
| FActScore | <https://github.com/shmsw25/FActScore> | atomic factuality scoring |
| SAFE | <https://github.com/google-deepmind/long-form-factuality> | long-form factuality comparator |
| simple-evals | <https://github.com/openai/simple-evals> | SimpleQA evaluation reference |
| OLMo | <https://github.com/allenai/OLMo> | open model/training stack candidate |
| Pythia | <https://github.com/EleutherAI/pythia> | controlled model-scale/checkpoint candidate |
| OLMES | <https://github.com/allenai/olmes> | reproducible LM evaluation harness candidate |
| Batch Invariant Ops | <https://github.com/thinking-machines-lab/batch_invariant_ops> | deterministic inference experiment |

## 7. Source reviewed but not suitable as research evidence

### Fxis

[Fxis](https://github.com/Pranavbh1/Fxis) was inspected because it claims to help
with deterministic inference. In its reviewed state, it mainly wrapped random
seed settings and did not establish batch invariance; parts of the code path
were incomplete or broken. Fixed seeds are useful, but they do not address the
floating-point and batch-order mechanism documented by He and Thinking Machines
Lab.

Decision: do **not** cite Fxis as evidence that CalibRead inference is
deterministic, and do not add it as a required dependency. It may be mentioned
only in internal engineering notes or reevaluated if a later tagged release
adds tested batch-invariant operations, hardware/version coverage, and a
repeatability benchmark.

## 8. Citation-to-experiment matrix

| CalibRead target | Essential references | What they justify |
|---|---|---|
| R0 controls and repeatability | `kirichenko2025abstentionbench`, `farquhar2024semantic`, `he2025nondeterminism` | unanswerability, paraphrase equivalence, systems repeatability |
| R1 / H1 exposure frequency | `kandpal2023memorization`, `mallen2023popqa`, `jiang2021calibration`, `kadavath2022mostly` | long-tail premise, confidence behavior, external validation |
| R2 precision | `jiang2021calibration`, `guo2017calibration` | calibration analysis; R2 itself remains a main novel controlled factor |
| R3 temporal freshness | `vu2023freshllms`, `bakman2025wild` | temporal benchmark and distribution-shift evaluation |
| R4 ambiguity | `min2020ambigqa`, `fisch2022limited`, `farquhar2024semantic` | valid-answer sets, false members, semantic equivalence |
| R5 / H2 synthesis depth | `trivedi2022musique` | component composition and natural multihop validation |
| R6 / H5 domain shift | `tibshirani2019covariate`, `bakman2025wild`, `hu2026cofact`, `tsatsaronis2015bioasq` | weighted calibration, conformal factuality under shift, in-the-wild transfer failure, biomedical validation |
| R7 abstention policy | `geifman2017selective`, `angelopoulos2024crc`, `wen2025abstention`, `bai2026score` | risk–coverage contract, primary false-commit control context, baseline taxonomy, secondary selective-risk method |
| H3 group failure | `shafer2008tutorial`, `jung2022multivalid`, `cherian2024validity` | marginal guarantee boundary and group-aware validity |
| H4 conditioned utility | `quach2024conformal`, `mohri2024factuality`, `hu2026cofact`, `ye2026conditional`, `rubashevskii2026adaptive` | language/factuality baselines and current conditional methods |

## 9. Literature-review structure for the final paper

Write the related-work section as an argument, not as one paragraph per paper:

1. **Parametric knowledge is heterogeneous.** Begin with long-tail exposure,
   temporal freshness, ambiguity, synthesis depth, and domain transfer. State
   that prior benchmarks normally vary several factors at once, motivating the
   controlled R0 controls, R1–R6 factors, and separate R7 policy-stress design.
2. **Confidence is useful but not a guarantee.** Cover calibration,
   self-evaluation, semantic entropy, uncertainty toolkits, and abstention.
   Distinguish ranking quality from calibrated probability and both from a
   validated risk contract.
3. **Conformal methods provide finite-sample marginal control.** Establish the
   foundation, language-generation extensions, and factuality-specific methods.
4. **Marginal control can hide conditional failures.** Move to multivalid,
   conditional, adaptive, and shift-aware methods. This leads directly to H3,
   H4, and H5.
5. **CalibRead’s gap.** No cited work jointly supplies controlled parametric
   complexity interventions, a common factual-read API, H1/H2 behavioral
   decompositions, worst-group validity auditing, and equal-risk comparison of
   complexity-conditioned policies across R1–R6 with an R7 stress suite. Phrase this as the gap your
   verified literature review found, not as an absolute “first ever” claim.

## 10. Maintenance checklist before submission

- Search by exact title and author for later peer-reviewed versions of every
  arXiv item.
- Export final publisher BibTeX where available and compare title, author order,
  year, pages, DOI, and venue against the companion database.
- Add access dates and immutable snapshots for changing datasets and web
  articles if required by the target citation style.
- Pin every repository by commit SHA in the reproducibility appendix; a branch
  name such as “main” is not sufficient.
- Cite licenses and document any data/model usage restrictions.
- Run a citation audit: every bibliography item must be cited, every citation
  key must exist, and every empirical or theoretical claim must be supported by
  the cited source.
- Do not cite this annotated guide itself. Cite the original work.
