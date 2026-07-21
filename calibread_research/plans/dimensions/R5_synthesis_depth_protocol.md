# R5 protocol — synthesis depth

## Scientific question

How does factual read reliability change when the final answer requires combining one to five stored facts, and is the change explained by independent per-hop failures?

## Testcase file and sample size

File: ../../testcases/r5_synthesis_depth.jsonl

- 10,000 records.
- 2,000 graph worlds.
- Five paired depth queries per graph.
- Locked test: 500 worlds × five depths = 2,500 records.

Every graph contains one origin, four linked record nodes, and one registered
designation attached at every depth. A depth-\(d\) query traverses \(d-1\)
`linked_record` edges and one final `registered_designation` edge. Every answer
therefore has the same generated `Designation` entity morphology. All depth
variants remain in one split. The paired structure provides substantially more
precision than unrelated questions at each depth without confounding depth with
person/city/code answer type.

## Knowledge injection

- Inject all four link facts and five designation facts with equal exposure count 16.
- Balance answer token length and relation templates.
- Keep graph components disjoint across worlds.
- Verify `answer_type=entity` and matched answer-token distributions at every depth.
- Ensure the final answer is not lexically present in the query.
- Keep question length comparable where possible and record token count.

## Required precheck

Before evaluating synthesis:

1. Ask every component single-hop question.
2. Record component correctness and confidence.
3. Mark whether all required facts for each depth are individually retrievable.

Deduplicate component probes by `(world_id, component query)` and reuse the
frozen result wherever a shallower link supports multiple depths. Repeated
references to the same probe are not additional observations.

The primary reasoning analysis includes only cases where all required components are available. The all-cases analysis is secondary.

## Hypothesis

H2's primary estimand is multihop final-answer error among graph-depth
observations for which every required component answer is correct. The
one-sided confirmatory test asks whether that error exceeds the 5% practical
floor.

On all graphs only, the secondary diagnostic compares observed error with a
cross-fitted independence prediction \(1-\prod_j\widehat p_{j,-g}\), where the
component-success models exclude graph \(g\). Never apply that formula inside
the all-components-correct subset.

## Inference

Run two prompt conditions:

- answer only;
- concise structured intermediate entities, with the final answer separately parsed.

The answer-only condition is primary because exposed reasoning can change behavior. The structured condition diagnoses which hop failed.

Collect:

- final answer;
- component answers;
- extracted intermediate path;
- confidence/uncertainty;
- sample clusters;
- path consistency;
- latency and tokens.

## Metrics

- final accuracy by depth;
- conditional final accuracy given all components available;
- component availability rate;
- first failed hop distribution;
- path faithfulness;
- AURC by depth;
- coverage at fixed risk;
- set size/miscoverage;
- inference cost versus depth.

## Statistical analysis

- Mixed-effects logistic/GAM model with graph intercept and depth.
- Paired depth contrasts within graph.
- Secondary all-graphs independence residual:

\[
\Delta_d=H_d^{observed}-H_d^{ind}
\]

- Cross-fit component probabilities with graph exclusion, then cluster bootstrap by graph for \(\Delta_d\).
- Model × depth and prompt × depth interactions.
- Sensitivity analysis controlling query token count.

Primary confirmatory analysis: graph-clustered one-sided interval/test of
conditional composition error against 5%. Depth-specific conditional results
are secondary.

Secondary diagnostic interpretation:

- \(\Delta_d>0\): amplification/dependence beyond independent hop failure.
- \(\Delta_d<0\): redundancy, self-correction, or mismatch between component probes and internal reasoning.
- interval containing zero: independence approximation is not rejected.

## Contract experiment

Calibrate a global policy on all depths, then audit each depth. Compare with:

- low-depth/high-depth groups;
- continuous depth-aware policy;
- CCRC.

H3 contribution: depth 4–5 are two of the 13 prespecified hard groups used to
test aggregate-versus-group validity. H3 is decided over the full group family,
not by R5 alone.

H4 contribution: depth features may let predicted-profile CCRC retain more
low-depth answers while satisfying the same aggregate-plus-13-group validity
gate as the global joint-safe baseline. H4 is decided on the full R1–R6
mixture, not by an R5-only comparison.

## Required output

- Accuracy and conditional-accuracy curves.
- Observed versus independence-predicted error.
- First-failed-hop Sankey or compact transition plot.
- Risk-coverage by depth.
- Table of depth interactions and CCRC utility.
