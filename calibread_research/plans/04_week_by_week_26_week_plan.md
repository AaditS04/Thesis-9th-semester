# Detailed 26-week execution plan

## Operating cadence

Every week:

- Monday: select tasks and freeze the week’s acceptance criteria.
- Tuesday–Thursday: implementation/experiments.
- Friday morning: validate artifacts and update lab notebook.
- Friday afternoon: supervisor review with one-page status.
- Never start a large run on unvalidated code.

Maintain:

- decision log;
- experiment registry;
- risk register;
- bibliography;
- paper draft from week 1;
- compute ledger.

---

## Week 1 — research question and scope lock

Tasks:

- Read the master blueprint.
- Define parametric read and excluded retrieval/tool behavior.
- Confirm the primary action interface: `ANSWER`, `ABSTAIN`, `CLARIFY`, and `REJECT_PREMISE`; the external controller may construct answer sets for secondary analyses.
- Record the already selected primary contract: false-commit risk per incoming query at target 0.05 and calibration confidence 0.95; answer coverage is primary utility.
- Document available GPUs, storage, and human annotators.
- Create bibliography manager and related-work spreadsheet.
- Read Conformal Language Modeling and conformal factuality.

Deliverables:

- one-page scope;
- primary risk definition;
- compute inventory;
- 20-paper related-work table.

Gate:

- supervisor can restate the guarantee without ambiguity.

## Week 2 — novelty and preregistration

Tasks:

- Read conditional/adaptive/shift conformal work through July 2026.
- Complete novelty comparison columns.
- Decide whether CCRC is a method contribution or systems application.
- Freeze H1–H5 primary endpoints.
- Freeze target risks and confidence levels.
- Draft exclusions and multiplicity correction.
- Select a provisional target venue and record its current paper format, page limit, review calendar, and artifact policy; recheck before submission.

Deliverables:

- novelty memo;
- preregistration v0.1;
- paper contribution paragraph;
- go/no-go decision on method novelty.

Gate:

- no “first conformal LLM” claim remains.

## Week 3 — testcase schema and generators

Tasks:

- Review R0–R7 JSONL schema.
- Run generator and validator.
- Inspect 25 fit/tune cases per file; do not sample calibrate/test for design repair.
- Verify factor level balance and split grouping.
- Review entity/token length distributions.
- Test that answers do not appear in held-out query wording.

Deliverables:

- testcase manifest and hashes;
- 200-case audit sheet;
- issue list.

Gate:

- zero schema/split errors; at least 98% human acceptance of case validity.

## Week 4 — knowledge-corpus materialization

Tasks:

- Implement the multi-file, stage-aware materializer from `injection_spec`.
- Cycle templates exactly by exposure.
- Build one unified initial corpus from all R0–R7 suites and one R3 temporal-update corpus.
- Fix exposure assignments across model sizes and optimizer seeds; seeds may change optimizer/data order only.
- Generate train documents and data-order manifest with the same document stream and token budget for every confirmatory seed/model run.
- Verify no evaluation templates in training.
- Compute per-level token, answer-length, and relation summaries.

Deliverables:

- training corpus v0.1;
- leakage report;
- counterbalance table;
- materializer tests.

Gate:

- designed exposure equals observed occurrence count exactly.

## Week 5 — small-model injection pilot

Tasks:

- Select 1B base model revision.
- Run small hyperparameter grid on fit only.
- Measure direct cloze and R0 accuracy.
- Inspect learning by exposure.
- Check catastrophic general capability loss on a tiny public sanity set.
- Choose one training recipe on tune.

Deliverables:

- learning curves;
- checkpoint/adapters;
- recipe decision memo;
- R0 pilot.

Gate:

- nondegenerate exposure curve and adequate R0 known accuracy.

## Week 6 — final design and power

Tasks:

- Estimate error rates and within-world correlations from pilot.
- Complete power calculation.
- Freeze full sample counts or amend before test use.
- Freeze prompts and answer schema.
- Freeze model panel and training seeds.
- Confirm the false-commit contract, target 0.05, confidence 0.95, and answer-coverage utility; any change is a dated fit/tune-only amendment.
- Submit preregistration to supervisor/internal archive.

Deliverables:

- preregistration v1.0;
- sample-size memo;
- frozen configuration directory.

Gate:

- changes after this week require dated deviations.

## Week 7 — scalable generation pipeline

Tasks:

- Implement batched, resume-safe inference.
- Store raw prompts, outputs, logprobs, latency.
- Implement run manifests and unique keys.
- Test deterministic greedy behavior.
- Run 1% R0–R2 dry run.

Deliverables:

- raw generation layer;
- cost extrapolation;
- missing/duplicate checker.

Gate:

- zero missing/duplicate outputs in dry run.

## Week 8 — graders and parsers

Tasks:

- Implement action parser.
- Implement exact/alias/date/numeric graders.
- Implement stale/current classifier.
- Implement ambiguity-set and path graders.
- Hand grade 300 development outputs blind: the fixed 100-output R0 gate sample
  plus 200 outputs stratified across R1–R7 graders and action types.
- Measure agreement and repair rubric/parser.

Deliverables:

- grader package;
- rubric;
- validation report.

Gate:

- at least 98% agreement for deterministic tasks; adjudication path for others.

## Week 9 — basic uncertainty features

Tasks:

- Freeze exact sample agreement as the sole primary score.
- Validate optional P(True) and token-score availability without fallback.
- Normalize score directions.
- Produce initial risk-coverage plots.
- Export feature-availability diagnostics by provider and suite.

Deliverables:

- uncertainty feature table v0.1;
- feature tests;
- baseline plots.

## Week 10 — exact-answer uncertainty hardening

Tasks:

- Verify strict answer normalization and exact-answer entropy.
- Add adversarial parser/candidate tests.
- Document that exact-answer entropy is not semantic entropy.
- Record sampling-budget sensitivity and failure cases.

Deliverables:

- exact-answer entropy feature;
- terminology and normalization audit;
- cost comparison.

Gate:

- no artifact or paper text labels exact entropy as semantic entropy.

## Week 11 — primary-score and calibration hardening

Tasks:

- Test exact-agreement completeness across providers.
- Test P(True)/token missingness fail-closed behavior.
- Fit calibration maps only on development splits.
- Freeze the primary score and its generation budget.

Deliverables:

- primary-score revision/hash;
- availability report;
- calibration tests.

## Week 12 — natural dataset preparation

Tasks:

- Freeze dated SimpleQA/FreshQA/AmbigNQ/MuSiQue/domain snapshots.
- Record licenses and checksums.
- Convert to canonical schema.
- Define graders.
- Manually validate 100 per dataset.
- Keep natural and synthetic result labels separate.

Deliverables:

- natural manifests;
- licensing table;
- validity audit.

## Week 13 — reproduce ordinary conformal baseline

Tasks:

- Implement split conformal toy example.
- Unit-test quantile finite-sample correction.
- Reproduce a small published language-model conformal result.
- Check calibration/test exchangeability assumptions.
- Write theorem/guarantee in project notation.

Deliverables:

- baseline reproduction notebook/script;
- theory note;
- unit tests.

Gate:

- no CCRC claim until baseline is correct.

## Week 14 — global risk-control policy

Tasks:

- Define finite policy grid.
- Implement Learn-then-Test/conformal risk control.
- Implement multiplicity correction.
- Implement unsupported-contract output.
- Simulate IID validity over repeated draws.
- Simulate distribution-shift failure.

Deliverables:

- global policy;
- simulation figures;
- risk-test logs.

## Week 15 — CCRC group hierarchy

Tasks:

- Freeze the R1–R6 groups; interaction groups are outside the core.
- Unit-test deterministic query-only routing without a ground-truth oracle.
- Implement hierarchical fallback.
- Enforce minimum calibration sample.
- Validate simultaneous risk tests.
- Compare global and group policies on tune.

Deliverables:

- CCRC v0.1;
- hierarchy diagram;
- unit/property tests.

## Week 16 — deterministic query profiler

Tasks:

- Freeze and hash query-only profile rules.
- Evaluate profile assignments on fit/tune.
- Audit forbidden-field independence.
- Measure routing confusion.
- Add fail-closed behavior for out-of-scope queries.

Deliverables:

- query_rules_v1.1 specification and assignment audit;
- assignment distributions;
- CCRC v1.0 frozen.

## Week 17 — main controlled model training

Tasks:

- Run frozen 1B seeds.
- Run frozen unified 7B model/seed adapters if approved; never train one adapter per suite.
- Verify hashes and losses.
- Run the policy-free R0 gate for every checkpoint using development partitions only.
- Exclude only by preregistered infrastructure/gate rules.

Deliverables:

- final checkpoints;
- R0 gate table;
- training-cost ledger.

## Week 18 — R1–R3 development-side generation

Tasks:

- Generate fit, tune, and calibrate splits only; the sealed test split must not be generated or scored.
- Grade and compute features.
- Validate counts/hashes.
- Verify the test-output location is empty and access controls remain active.

Deliverables:

- immutable development-side R1–R3 raw/scored artifacts;
- QC report.

## Week 19 — R4–R7 development-side generation and analysis freeze

Tasks:

- Generate, grade, and score fit, tune, and calibrate partitions of R4–R7 only.
- Run clarification second-turn simulations.
- Complete the fixed 200-question fit/tune-only R4 clarification audit.
- Run component probes for R5.
- Apply the R7 threshold grid on development-side records.
- Validate counts/hashes.
- Freeze the single result per H1–H5, prompts, graders, exclusions, policy family, profiler, analysis code, and all artifact hashes.

Deliverables:

- immutable development-side R4–R7 artifacts;
- QC report.

## Week 20 — calibration and contract freeze

Tasks:

- Fit scorers on fit.
- Choose grids/features on tune.
- Calibrate policies on calibrate.
- Save contract artifacts.
- Freeze all selected policies.
- Confirm test code cannot refit.
- Sign and archive the preregistration plus code/prompt/grader/model/calibration hashes before any test generation.

Deliverables:

- signed/frozen contract manifests;
- calibration report;
- supported/unsupported group list.

## Week 21 — locked controlled evaluation

Tasks:

- Generate locked-test model outputs for the first time.
- Grade and score with the frozen pipeline.
- Run the final evaluation script once without refitting or threshold selection.
- Generate aggregate metrics and intervals.
- Check denominators.
- Record deviations.
- Preserve original output before any reanalysis.
- Create one blinded 200-case test-only audit (25 per suite) by joining each
  sampled frozen specification to its frozen output; record label defects as
  deviations and never use it for retuning.

Deliverables:

- locked results v1;
- H1–H5 input tables;
- preliminary figures.

## Week 22 — natural validation and shift

Tasks:

- Run natural datasets with frozen models/policies.
- Construct domain transfer matrix.
- Run temporal and mixture-reweight shift.
- Run small target recalibration study.
- Separate confirmatory controlled and observational natural claims.

Deliverables:

- transfer matrix;
- natural-results appendix;
- shift failure report.

## Week 23 — hypothesis statistics

Tasks:

- Execute exact H1–H5 scripts.
- Apply Holm correction.
- Compute effect sizes and intervals.
- Run only preregistered sensitivity analyses.
- Label exploratory results.

Deliverables:

- hypothesis decision table;
- statistical appendix;
- final figures.

## Week 24 — ablations, errors, and first paper

Tasks:

- Complete required ablations.
- Human-review high-confidence errors.
- Create error taxonomy.
- Write full paper draft.
- Insert generated tables/figures, never hand-copy numbers.

Deliverables:

- draft v1;
- ablation table;
- error-analysis section.

## Week 25 — internal review and reproducibility

Tasks:

- Supervisor/coauthor review.
- Statistical proof review.
- Run clean-environment reproduction.
- Create anonymized artifact.
- Check citations and licenses.
- Create model/data cards.

Deliverables:

- draft v2;
- artifact checklist;
- reproducibility report.

Gate:

- every main number reproducible by one documented command.

## Week 26 — final thesis/paper release

Tasks:

- Address review.
- Verify claims match statistical evidence.
- Finalize limitations.
- Archive code/data/manifests.
- Prepare venue format, supplement, and thesis chapter.
- Prepare 15-minute and 30-minute presentations.

Deliverables:

- submission-ready paper;
- thesis methodology/results chapters;
- archived artifact;
- presentation.
