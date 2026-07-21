# R4 protocol — ambiguity and valid interpretations

## Scientific question

Can the read system detect that a question has multiple valid interpretations and choose clarification or a set rather than confidently committing one arbitrary answer?

## Testcase file and sample size

File: ../../testcases/r4_ambiguity.jsonl

- 8,000 records.
- 2,000 paired worlds.
- Four ambiguity levels per world: 1, 2, 3, and 4 valid interpretations.
- Locked test: 500 worlds × four levels = 2,000 records.

Pairing holds the shared display name and stored roles fixed while varying how many records the question leaves plausible.

## Ground truth

Each world contains four distinct identities sharing the same display name, each linked to a different office and role.

- Level 1 names one office and has one valid answer.
- Levels 2–4 leave two to four office-specific interpretations plausible.

Primary operational target:

- answer at level 1;
- ask a minimal clarification question at levels 2–4.

Secondary answer-set target:

- return all plausible labeled role interpretations.

## Procedure

1. Inject all four office-specific facts at equal exposure.
2. Confirm each disambiguated component is retrievable.
3. Run the ambiguity variants with identical response schema.
4. Parse action before grading content.
5. If action is clarification, compare its proposed choices with valid choices.
6. Simulate a second turn by selecting each clarification option once.
7. Measure factual accuracy after clarification.

## Metrics

Primary:

- ambiguity detection precision, recall, and F1;
- action accuracy;
- clarification-option recall;
- post-clarification factual accuracy.

Answer-set mode:

- interpretation-set precision;
- interpretation-set recall;
- set F1;
- exact-set match;
- unsupported interpretation count.

Reliability:

- confidence assigned to forced single answers;
- false-commit rate under ambiguity;
- risk-coverage and clarification-coverage curves;
- group coverage gap by ambiguity count.

## Analysis

- Mixed-effects logistic regression with world intercept and ambiguity count.
- Test monotonic change in clarification probability.
- Compare factual error when forced to answer versus allowed to clarify.
- Paired bootstrap by world.
- Treat the four-level trend as the primary test and pairwise levels as secondary.

Error categories:

- failed to detect ambiguity;
- detected but asked an irrelevant clarification;
- incomplete option list;
- invented interpretation;
- correct set but wrong action format;
- correct after clarification.

## Contract experiment

The action policy must have separate losses:

- factual loss after commit;
- ambiguity-action loss;
- answer-set miscoverage.

Do not treat any one valid answer to an ambiguous query as fully correct if the required action was clarification. Compare:

For the primary false-commit loss, every level-2–4 single-answer `ANSWER` is an
incorrect commit because the request has no unique intended office. The listed
roles are retained to grade clarification choices and secondary externally
constructed answer sets; they are not licenses to score an arbitrary singleton
as correct.

- global confidence threshold;
- ambiguity-aware rule;
- CCRC with deterministic query_rules_v1.1 ambiguity routing.

Ground-truth-oracle profiling is omitted under protocol v1.2 and cannot support
H4.

## Required output

- Figure: action distribution versus valid interpretation count.
- Figure: false-commit risk versus ambiguity.
- Table: ambiguity detector and clarification quality.
- Table: forced answer versus clarification policy.
- Appendix: the fixed, blinded audit of 200 fit/tune-only clarification
  questions and their simulated second-turn outcomes.
