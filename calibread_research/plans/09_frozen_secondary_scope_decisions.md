# Frozen secondary-scope decisions (protocol v1.2)

**Decision date:** 2026-07-22  
**Authority:** This file resolves R02–R05 in
FINAL_CONSISTENCY_ISSUES_AND_REPAIR_PLAN.md. It is subordinate only to the
final H1–H5 crosswalk for confirmatory endpoints and overrides older roadmap
text that lists these features as required deliverables.

These decisions are made before calibration-policy freeze and before locked-test
access. They reduce optional scope; they do not change the R0–R7 corpus, H,
H1–H5 endpoints, false-commit contract, independent-world inference, or CPR.

## Primary confidence feature

The sole primary confidence feature is exact_agreement, calculated against
the greedy answer from the frozen generation budget. It is available for every
provider because it does not require logprobs or a separate self-evaluation
request. The runner and confirmatory preflight fail closed if a primary row is
missing this declared method.

P(True) and mean token probability remain optional, explicitly named secondary
features. Their availability is reported by model/provider/suite. They are
never substituted for, or mixed into, the primary score. A separate verbal
confidence prompt and a learned correctness scorer are omitted from protocol
v1.2 and may only appear in future work or a clearly labelled post-hoc
extension.

## Entropy terminology

Protocol v1.2 reports exact_answer_entropy: entropy over strictly normalized
answer strings from repeated generations. It is not semantic entropy and must
never be called semantic entropy. NLI/embedding clustering, semantic entropy,
and semantic-cluster auditing are omitted and reserved for future work.

## H4 query profiler

The H4 deployable profiler is the deterministic, versioned,
query-text-only rule set query_rules_v1.1. It uses frozen regular expressions
for ambiguity, temporal, precision, synthesis, and domain cues and never reads
dimension IDs, factors, labels, answers, losses, or split names. Fit/tune data
may estimate policy penalties within the frozen profiles, but do not train the
profile assignment rule.

A trained classifier profiler and a ground-truth-factor oracle are omitted from
the required protocol. If produced later, the oracle is diagnostic only and
cannot select or validate the primary H4 policy.

## R6 continuous shift features

H5 remains the categorical, prespecified four-direction calibration-transfer
endpoint. Frozen embedding distance, domain-classifier log odds, prompt
perplexity, relation/template novelty, answer-token rarity, their regression,
and the associated feature-model hashes are omitted from protocol v1.2. The
pooled/domain transfer matrix and maximum-gap inference remain required.

These continuous features may be future secondary work. They must not be
described as planned outputs, explanations established by this paper, or
requirements for the categorical H5 conclusion.

## Reporting constraints

- The paper’s main uncertainty comparison is exact agreement plus optional
  availability-labelled P(True)/token diagnostics.
- Every entropy table says “exact answer entropy.”
- H4 says “deterministic query-only profiler,” not “trained profiler.”
- H5 claims categorical transfer behavior, not a causal explanation from
  continuous shift features.
- Reintroducing any omitted feature after locked-test access is post-hoc and
  cannot alter confirmatory decisions.
