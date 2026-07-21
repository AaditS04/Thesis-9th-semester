# Paper claim guardrails enforced by the code

The proposal paragraph should not be copied unchanged into the final paper.
The executable study supports the following corrected claims.

## 1. Six causal factors plus one policy stress suite

R1–R6 are the six controlled complexity factors:

1. exposure frequency;
2. required precision;
3. temporal availability;
4. ambiguity;
5. synthesis depth;
6. domain shift.

R7 applies thresholds to frozen confidence scores and is a secondary policy
stress suite. It is not a seventh independently randomized cause. R0 remains a
pipeline/control suite outside this six-factor mixture.

Recommended wording:

> CalibRead measures false-commit reliability across six independently
> controlled query/knowledge complexity factors and a separate threshold-policy
> stress suite, producing reliability surfaces rather than one scalar score.

## 2. H is a false-commit surface

The code defines

\[
H_{fc}(\theta,Q)=|Q_\theta|^{-1}\sum_i
1\{D_i=\mathrm{ANSWER}\land C_i=0\}.
\]

This makes abstention visible through answer coverage and prevents selective
risk from silently changing the denominator. The code also exports selective
hallucination risk, but it is secondary.

`D=ANSWER` is operationalized as either a declared ANSWER or any non-empty
answer payload, so an invalid response cannot hide a factual commit behind an
ABSTAIN/CLARIFY label.

## 3. Do not claim an individual conformal posterior

The final Read artifact contains:

- `y`: the returned answer when the policy commits;
- `c_point_estimate`: an empirically calibrated correctness estimate;
- `estimated_error_probability`: its descriptive complement;
- a policy-level false-commit risk upper bound (whose complement is a lower
  bound on avoiding a false commit, including abstentions); and
- an optional CPR prediction set.

Standard split conformal coverage is marginal over future exchangeable
examples. It does not ordinarily prove that one particular answer has error
probability at most `1-c`. The CSV therefore sets
`individual_error_bound_available=0` and records the formal scope explicitly.

Recommended wording:

> CalibRead returns an answer with a calibrated score and an explicit
> policy-level reliability certificate. CPR constructs answer sets with
> finite-sample marginal coverage under exchangeability; it does not interpret
> the certificate as a posterior error bound for an individual string.

## 4. CPR minimality is relative to a frozen family

The implemented set family is nested top-k sampled answer clusters plus an
all-answers vacuous fallback, on which the deployed system abstains. The conformal rank cutoff is the smallest member
of this frozen family that passes calibration. This is not a proof of globally
minimum set size over every possible set-valued predictor.

CPR coverage is evaluated only on operationally unique targets; multi-answer
ambiguity cases are part of the false-commit policy analysis, not the conformal
single-label coverage population.

Recommended wording:

> CPR selects the smallest certified set in a prespecified nested candidate
> family and reports both non-vacuous set size and universal-fallback rate.

## 5. OpenRouter mode affects the scientific claim

A public OpenRouter model has not learned the synthetic controlled facts.
Zero-shot and prompt-context runs are useful pipeline/baseline experiments but
cannot confirm parametric exposure or storage hypotheses. Only a served model
whose frozen checkpoint manifest attests the unified CalibRead training stream
may produce `scientific_status=confirmatory_parametric`.

## 6. Protocol-v1.2 feature scope

Exact agreement is the sole primary confidence score. Missing primary scores
remain missing and fail confirmatory preflight; they are never replaced by a
different method. P(True) and token probability are optional
availability-labelled diagnostics.

The implemented entropy is exact_answer_entropy over exact normalized
answer/action clusters, not semantic entropy. Protocol v1.2 does not claim a
verbal-confidence model, learned correctness scorer, NLI semantic clustering,
trained/ground-truth H4 profiler, or continuous R6 shift-feature explanation.
H4 uses deterministic query_rules_v1.1 and H5 remains the categorical frozen
transfer endpoint.
