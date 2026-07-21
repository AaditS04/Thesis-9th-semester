# CalibRead OpenRouter runner

This package runs CalibRead R0–R7 through an OpenRouter model, caches every raw
response, grades it deterministically, derives uncertainty features, and writes
CSV files consumed by the separate `calibread_analytics` package.

## Scientific boundary you must preserve

CalibRead's controlled facts are synthetic. A normal public OpenRouter model
has not received the unified CalibRead T0/T2 training corpus. Therefore:

- `closed_book_external` is a useful zero-shot hallucination/control baseline,
  but it cannot confirm an exposure-frequency or parametric-storage claim;
- `contextual_debug` repeats injected documents in the prompt and is only a
  pipeline test—it measures contextual reading, not parametric memory;
- `parametric_checkpoint` is the only confirmatory mode. It requires an
  existing checkpoint-manifest file and the explicit injection attestation in
  the config. Use it only when the selected endpoint really serves that frozen
  trained checkpoint.

Copy `checkpoint_manifest.example.json` only after training. The runner checks
that its served model ID matches the selected OpenRouter slug and that checkpoint,
corpus, unified-training, and completion attestations are present.

R0 is executable only as a development checkpoint gate and never enters the
R1–R6 hypothesis mixture. R3 uses two separately frozen served
endpoints/checkpoints. The primary paper
run evaluates all R1–R7 levels—including every R3 state—on `checkpoint_t2`.
A separate secondary run evaluates only R3 `current_after_update` queries on
`checkpoint_t0`; analytics pairs those same worlds with their primary T2 rows
to estimate the controlled update effect. Secondary T0 rows are excluded in
code from H1–H5, H(θ,Q), calibration, and CPR.

Use distinct run IDs, output directories, and manifests while keeping prompts,
decoding, provider, and splits identical. Give both endpoints the same frozen
`model.analysis_id` (for example `calibread-family-seed-01`) but retain the real
endpoint slug in `model.id`. Endpoint-level provenance remains in raw/scored
model fields, configs, and manifests. The relevant experiment fields are:

Primary T2 config:

~~~json
"analysis_role": "primary",
"checkpoint_stage": "checkpoint_t2",
"levels": []
~~~

Secondary T0 config (with `suites` set to `["R3"]`):

~~~json
"analysis_role": "secondary_temporal",
"checkpoint_stage": "checkpoint_t0",
"levels": ["current_after_update"]
~~~

Add both output directories to analytics `inputs`. Do not switch a served
checkpoint in place under one run ID. For pilots, the equivalent selector is
`--level LEVEL`; for paper runs use the config field so it enters the hash.

Every output row contains `scientific_status`; the analytics package refuses to
label a public zero-shot/contextual run confirmatory.

## Setup

~~~shell
cd calibread_openrouter
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
cp config.example.json config.json
~~~

For the actual checkpoint study, start from
`config.parametric_t2.example.json` and
`config.parametric_t0_temporal.example.json`; they already encode the primary
versus secondary R3 separation. The generic `config.example.json` is the public
OpenRouter/pipeline template.

~~~shell
cp config.parametric_t2.example.json config_t2.json
cp config.parametric_t0_temporal.example.json config_t0.json
~~~

These private `config_*.json` files are git-ignored.

Create the two attestation files only after the checkpoints exist:

~~~shell
cp checkpoint_manifest.example.json checkpoint_manifest_t2.json
cp checkpoint_manifest.example.json checkpoint_manifest_t0.json
~~~

Set each real served model ID, stage, checkpoint/corpus hashes, and training
seeds. The runner refuses a stage or served-model mismatch.

Edit only your private `config.json` initially:

~~~json
"api_key": "paste your OpenRouter API key",
"id": "author/model-slug",
"run_id": "calibread_run_001"
~~~

The example already uses `calibread_run_001`, so the only mandatory edits are
the key and model slug. Change the run ID/output directory when starting a new
immutable model or configuration run.

The key-bearing `config.json` and `outputs/` are ignored by this package's
`.gitignore`. Do not paste the key into source files or published manifests.

OpenRouter uses `POST /api/v1/chat/completions`; model slugs are available from
`GET /api/v1/models`. The runner also supports strict JSON-schema output,
log-probabilities, provider parameter enforcement, disabled provider fallback,
and data-collection controls when the chosen endpoint advertises them. See:

- <https://openrouter.ai/docs/quickstart>
- <https://openrouter.ai/docs/guides/features/structured-outputs>
- <https://openrouter.ai/docs/guides/routing/provider-selection>
- <https://openrouter.ai/docs/api/reference/parameters>

## Select a model

Search current OpenRouter models instead of copying a stale model name:

~~~shell
calibread-openrouter models --config config.json --contains llama --limit 20
calibread-openrouter validate --config config.json --online
~~~

The `models` command needs only the pasted API key; it works while the model
field still contains the placeholder. Paste one returned ID, then run online
validation.

For the frozen paper run, set a specific provider in `model.provider.only` or
`order`, retain `allow_fallbacks=false`, and archive the returned model/provider
metadata. If a model does not support seeds, logprobs, or structured output,
either choose another model or explicitly change the frozen feature plan.

## Safe workflow

Estimate the request volume without spending credits:

~~~shell
calibread-openrouter estimate --config config.json --suite R1 --split fit
~~~

For an inexpensive pilot, copy the config to a new pilot run ID/output directory
and set `limit_per_suite` to 10:

~~~shell
calibread-openrouter run --config config.json --suite R1 --split fit
~~~

The command is append-only and resume-safe. Successful compound keys are not
called again; failed requests remain visible and are retried on the next run.
Observation specs and R5 links are merged across separate suite/split commands.
An output directory is locked to one run ID, config hash, and content-addressed
scientific bundle. The bundle hashes prompts, testcase files/manifest/schema,
checkpoint manifest claims, route policy, grader, runner source, and profile
rules. Any changed scientific byte requires a new output directory instead of
silently reusing generations.

Run the development partitions before the week-20 freeze:

~~~shell
calibread-openrouter run --config config.json --split fit --split tune --split calibrate
~~~

Locked-test access is refused unless the config contains:

~~~json
"test_release_attestation": "I_CONFIRM_WEEK20_FREEZE_IS_ARCHIVED"
~~~

Only set this after the preregistration, prompts, graders, model, calibration
artifacts, and code hashes are archived. Then run test once:

~~~shell
calibread-openrouter run --config config.json --split test
~~~

The attestation is stored in the resolved config but deliberately excluded from
the scientific config hash, so adding this access acknowledgment does not make
the locked test look like a different model/prompt experiment.

## Output files

Each run directory contains:

- `raw_generations.csv`: one immutable row per request/sample, including errors,
  exact model/provider returned, tokens, latency, cost, prompt hashes, and raw
  output; the system fingerprint, exact request message array, and its hash are
  retained when the provider returns them;
- `scored_results.csv`: one row per final/component/clarification observation,
  with action/factual/commit grading and confidence features;
- `candidate_sets.csv`: ranked sampled-answer candidates used by CPR;
- `component_links.csv`: R5 parent-depth to deduplicated component-probe joins;
- `run_summary.csv`: counts, errors, tokens, and cost by suite/split;
- `observation_specs.jsonl`: immutable join metadata for rebuilding scores;
- `resolved_config.redacted.json`: API-key-free run configuration;
- `model_metadata.json`: model capabilities and pricing returned at run time.
- `scientific_bundle_manifest.json`: the canonical hashes locking every
  scientific input and every output row.

`by_suite/R0` through `by_suite/R7` contain separate scored and candidate CSVs,
so every suite can be inspected or transferred independently without filtering
the combined file.

R5 component probes are deduplicated by world and query. R4 clarification turns
reuse the frozen first-turn response and evaluate every listed clarification
choice. Auxiliary stochastic sampling is independently configurable to control
cost.

The frozen repeatability subset sends identical temperature-zero requests with
the same seed (`repeatability_repeats` and `repeatability_limit_per_suite`).
Those rows are excluded from uncertainty estimation and are analyzed separately
for exact and parsed-output nondeterminism.

## Confidence outputs

`confidence_score` defaults to exact sample agreement. Token-probability and
P(True) alternatives can be selected when supported. A missing selected method
remains missing and fails confirmatory preflight; it is never silently replaced
with another score. These are scores—not
formal per-answer probabilities. The analytics package calibrates them and
constructs:

- policy-level false-commit risk certificates; and
- split-conformal candidate sets with marginal coverage.

Neither guarantee should be described as a posterior bound for one individual
answer.

When token log-probabilities are returned, `mean_nll`, `total_nll`, and
`min_token_probability` are computed only from the greedy response's token spans
overlapping the JSON `answer` value. Greedy full-response NLL is stored
separately. If the provider's token
representation cannot be aligned to that value, answer-token fields remain
missing instead of silently substituting the full JSON likelihood.
