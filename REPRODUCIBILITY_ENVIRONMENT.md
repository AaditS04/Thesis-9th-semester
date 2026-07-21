# CalibRead reproducibility environment

The executable packages have no third-party runtime dependencies. Their
pyproject files declare an empty dependency list and Python 3.9 or newer. The
offline repair verification on 2026-07-22 used:

- Python 3.9.6;
- macOS/Darwin host environment;
- only the Python standard library;
- calibread-openrouter 0.1.0;
- calibread-analytics 0.1.0.

For each paid or scientific run, record the exact output of python --version,
the installed-package export, OS/accelerator/driver details, and the environment
file hash in the run manifest. The code also writes the Python version and
source hashes into the scientific/analysis manifests.

This file is not a substitute for a milestone-specific frozen Git tag. The
complete project baseline was committed on 2026-07-22 as `180fdca`
(`Build complete CalibRead research and evaluation framework`) and is released
under the annotated tag `calibread-research-framework-v1.0`. A fresh checkout
regenerated and validated all 70,000 testcases against the tracked manifest
while `git status --porcelain` remained empty. Pilot, calibration-freeze, and
locked-test tags must still be created at those real events.

The eight generated testcase JSONL files are intentionally release artifacts,
not Git objects. The generator, validator, schema, and manifest are tracked.
A clean checkout must regenerate all eight files byte-identically and verify
their SHA-256 values against the tracked manifest before any run.
