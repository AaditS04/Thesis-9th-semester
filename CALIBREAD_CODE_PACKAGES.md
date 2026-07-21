# CalibRead executable code packages

## Package 1 — OpenRouter experiment runner

Location: `calibread_openrouter/`

~~~shell
cd calibread_openrouter
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
cp config.example.json config.json
~~~

Use `config.parametric_t2.example.json` plus
`config.parametric_t0_temporal.example.json` for the real two-checkpoint study,
and run the matching R0 T2/T0 checkpoint-gate configs before accepting either
checkpoint;
the generic example is for public-model/pipeline runs.

Paste the private OpenRouter API key and selected `author/model` slug into
`config.json`. Then:

~~~shell
calibread-openrouter validate --config config.json --online
calibread-openrouter estimate --config config.json --suite R1 --split fit
calibread-openrouter run --config config.json --suite R1 --split fit
~~~

Remove the pilot limit only after validating counts, costs, output parsing, and
model capabilities. The command resumes from successful request keys only when
the complete content-addressed scientific bundle is unchanged.

R3 uses a primary all-suite T2 run plus a secondary T0 run containing only
`current_after_update`. Give both real endpoints the same frozen
`model.analysis_id`, but separate `model.id`, run IDs, manifests, output
directories, `analysis_role`, `checkpoint_stage`, and archived level selectors.
Analytics pairs T0/T2 worlds while excluding secondary rows from every primary
hypothesis and H surface. The runner README gives the exact mapping.

## Package 2 — paper analytics

Location: `calibread_analytics/`

~~~shell
cd calibread_analytics
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
cp analysis_config.example.json analysis_config.json
calibread-analyze --config analysis_config.json
~~~

`analysis_config.parametric.example.json` is the ready-made four-input template
for primary T2, secondary R3 T0, and both R0 development gates. Confirmatory
preflight requires every runner artifact and fails on incomplete/malformed,
mixed-stage, mixed-score, route-drifted, or hash-inconsistent input.

The output contains H(θ,Q), R1–R7 metrics, H1–H5 decisions, CPR sets,
calibrated Read pairs, contracts, SVG figures, CSV/LaTeX tables, diagnostics,
and an integrity manifest.

Read these before using any result in the paper:

1. `calibread_openrouter/README.md`
2. `calibread_analytics/README.md`
3. `calibread_analytics/PAPER_CLAIM_GUARDRAILS.md`
4. the generated `H_INDEX_AND_CONFIDENCE.md`

## Offline verification

~~~shell
PYTHONPATH=calibread_openrouter/src \
python3 -m unittest discover -s calibread_openrouter/tests -v

PYTHONPATH=calibread_analytics/src \
python3 -m unittest discover -s calibread_analytics/tests -v
~~~

These tests use fake responses and spend no API credits.
