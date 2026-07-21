# Unified controlled-training and checkpoint plan

## Why one training design is required

Primary R1–R6 comparisons and the H3/H4 mixture must refer to one deployed read
system per model/seed. Training a separate adapter for every suite would
confound complexity with checkpoint identity. The core design therefore uses
one unified controlled knowledge stream for each model configuration and
training seed.

## Training unit

One controlled run is identified by:

~~~text
(base_model_revision, unified_corpus_revision, training_seed, data_order_seed)
~~~

The same fixed exposure assignment is used across model sizes and seeds so
model comparisons evaluate the same facts. Training seeds replicate optimizer
and data-order variation; they do not relabel a fact's exposure. Randomization
and balance of entity morphology, answer token length, relation, and stream
position must be audited before the corpus is frozen.

## Unified corpus inputs

The initial corpus combines the deduplicated injection programs from R0–R7:

- all positive-exposure R0/R1 facts;
- exact R2 date, numerical, and categorical values;
- R3 T0 inserts only;
- all R4 identities and roles;
- all R5 component facts;
- all R6 domain facts;
- R7 policy-stress facts.

Exposure-zero and withheld-current facts produce no document. Fit/tune/
calibrate/test is a downstream scorer/policy split, not a knowledge-injection
split: positive-exposure facts from every partition must be stored so the
locked test measures reads rather than accidental training omission.

## Two temporal stages

### Stage T0 — initial storage

1. Materialize all non-temporal programs and only T0 steps from temporal
   schedules.
2. Combine, deterministically order, and tokenize the corpus.
3. Train for the frozen token/step budget.
4. Save `checkpoint_t0` and run reload/repeatability probes.
5. Evaluate the preregistered pre-update R3 probes only.

### Stage T2 — controlled updates

1. Materialize only non-T0 update steps from R3 schedules.
2. Continue from `checkpoint_t0` with frozen optimizer/reset semantics.
3. Save `checkpoint_t2`.
4. Run the final R0 gate and main R1–R6 evaluation on `checkpoint_t2`; run R7 separately as a secondary policy stress suite.
5. For R3, compare T0 and T2 where a paired update effect is required.

Superseded-stale facts receive no new value at T2; they experience the same
unrelated update stream as the rest of the model. Post-cutoff/unknown facts are
never inserted.

## Materialization commands

Initial corpus:

~~~shell
python3 calibread_research/scripts/materialize_training_corpus.py \
  --testcase-file calibread_research/testcases/r0_baseline_controls.jsonl \
  --testcase-file calibread_research/testcases/r1_exposure_frequency.jsonl \
  --testcase-file calibread_research/testcases/r2_precision.jsonl \
  --testcase-file calibread_research/testcases/r3_temporal.jsonl \
  --testcase-file calibread_research/testcases/r4_ambiguity.jsonl \
  --testcase-file calibread_research/testcases/r5_synthesis_depth.jsonl \
  --testcase-file calibread_research/testcases/r6_domain_shift.jsonl \
  --testcase-file calibread_research/testcases/r7_threshold_policy.jsonl \
  --stage initial \
  --output /approved/corpus/location/calibread_t0.jsonl
~~~

Update corpus:

~~~shell
python3 calibread_research/scripts/materialize_training_corpus.py \
  --testcase-file calibread_research/testcases/r3_temporal.jsonl \
  --stage update \
  --output /approved/corpus/location/calibread_t2_updates.jsonl
~~~

## Token-budget rule

All seeds of one model use the same materialized documents and frozen number of
training tokens/steps. Because every exposure level appears in the same unified
run, no per-level filler is required or allowed: differences in documents per
fact are the R1 treatment itself.

If an ablation creates genuinely different total corpora, a tokenizer-aware
training-preparation step must add unrelated filler and verify equality in
**tokens**, not merely documents or characters. The current materializer does
not claim to perform tokenizer-aware filler generation.

## Model/checkpoint acceptance

For every checkpoint used in analysis, using development-side R0 partitions:

- planned token budget reached;
- no loss corruption;
- checkpoint reload probe matches under the declared inference backend;
- R0 known-direct and paraphrase gates pass for that checkpoint;
- general sanity-set degradation stays within the preregistered margin;
- corpus, order, optimizer, checkpoint, and environment hashes are recorded.

A checkpoint that fails is excluded only by the preregistered model-specific
gate and remains in the intention-to-evaluate failure summary.
