"""Paper tables, methodology notes, and analysis report assembly."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


def write_latex_table(path: Path, columns: Sequence[str], rows: Sequence[Dict[str, Any]], caption: str, label: str) -> None:
    alignment = "l" + "r" * (len(columns) - 1)
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        f"\\begin{{tabular}}{{{alignment}}}",
        "\\toprule",
        " & ".join(_tex(column.replace("_", " ").title()) for column in columns) + " \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(_tex(_display(row.get(column))) for column in columns) + " \\\\")
    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        f"\\caption{{{_tex(caption)}}}",
        f"\\label{{{label}}}",
        "\\end{table}",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_h_methodology(path: Path) -> None:
    text = r"""# How CalibRead computes the hallucination index H(θ,Q)

CalibRead does **not** use the bibliometric h-index. For a frozen model/run and
a prespecified query slice (Q_\theta), the primary hallucination surface is

\[
H_{fc}(\theta,Q)=\frac{1}{|Q_\theta|}\sum_{i\in Q_\theta}
\mathbf 1\{D_i=\mathrm{ANSWER}\land C_i=0\},
\]

where (D_i) is the effective returned action and (C_i) is operational commit
correctness. A non-empty answer payload counts as an ANSWER even if a malformed
response labels itself ABSTAIN or CLARIFY. For schema-valid responses this is
identical to the declared action. For R4 ambiguity levels 2–4, an arbitrary singleton ANSWER has
(C_i=0) even if it matches one plausible role. Thus H measures false commits
per incoming query and cannot be improved merely by dropping wrong committed
answers from the denominator.

The analytics export also reports:

- selective hallucination risk: false commits divided by committed answers;
- factual-wrong commits per incoming query;
- answer coverage: commits divided by incoming queries;
- world-cluster bootstrap intervals.

The complexity parameter (\theta) is the controlled R1–R6 factor value (and
R7 stress profile). Cross-suite aggregate contracts apply equal total weight to
R1–R6 and equal level weight within each suite.

For aggregate policy certificates, the implementation retains those row-level
mixture weights but forms independent `(run_id, world_id)` clusters. The
weighted Hoeffding radius uses squared cluster weights. Exact binomial bounds
are used only after verifying one equal-weight Bernoulli row per world.

## What the confidence value c means

`c_point_estimate` is an isotonic estimate of correctness learned only from
fit/tune data. It is useful calibration output but is **not** a formal
per-answer posterior bound.

`estimated_error_probability=1-c_point_estimate` is the corresponding
descriptive point estimate. `c_policy_error_upper` is an alias for the formal
policy-level bound below so the meaning of c is explicit in every exported
Read pair.

`policy_false_commit_risk_upper` is a simultaneous upper confidence bound for
the complete threshold policy over the declared future-query mixture. Its
complement is a policy-level lower bound on the probability of avoiding a false
commit (which includes abstentions), not a correctness probability for one
specific answer.

CPR uses split-conformal calibration over a frozen nested family of sampled
top-k answer sets plus an all-answers vacuous fallback, on which the deployed
system abstains. Under exchangeability,
it targets marginal set coverage

\[
\Pr\{Y_{new}\in S(X_{new})\}\ge 1-\alpha.
\]

The rank cutoff is the smallest passing member of that frozen nested family.
If the calibration quantile requires the all-answers fallback, coverage is
valid but vacuous; the fallback rate is therefore always reported.

The CPR coverage population contains only operationally unique targets. R4
ambiguity levels 2--4 are excluded because no single answer label is defined.

No output from this package should claim that standard conformal prediction
bounds the probability that one particular generated string is wrong.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_report(
    path: Path,
    config: Dict[str, Any],
    model_id: str,
    status: str,
    generated: Sequence[str],
) -> None:
    paper = config.get("paper", {})
    lines = [
        f"# {paper.get('title', 'CalibRead analysis')}",
        "",
        f"Model: `{model_id}`  ",
        f"Analysis version: `{paper.get('analysis_version', '')}`  ",
        f"Scientific status: **{status}**",
        "",
        "## Primary outputs",
        "",
        "- `tables/hypothesis_results.csv` contains exactly one H1–H5 result per hypothesis.",
        "- `tables/hallucination_index.csv` defines the H(θ,Q) surface.",
        "- `tables/calibrated_read_pairs.csv` distinguishes estimated confidence from policy-level certificates.",
        "- `tables/cpr_summary.csv` reports marginal coverage, finite set size, and all-answers fallback rate.",
        "- `tables/confidence_quality.csv` reports Brier/log loss, ECE/MCE, AUROC/AP, and (excess) AURC.",
        "- `H_INDEX_AND_CONFIDENCE.md` states the estimands and guarantee scope used in the paper.",
        "",
        "## Figures",
        "",
        "![Hallucination surface](figures/fig_h_complexity.svg)",
        "",
        "![Risk coverage](figures/fig_risk_coverage.svg)",
        "",
        "![Calibration](figures/fig_calibration.svg)",
        "",
        "![Hard groups](figures/fig_hard_groups.svg)",
        "",
        "![Domain transfer](figures/fig_domain_transfer.svg)",
        "",
        "![CPR](figures/fig_cpr.svg)",
        "",
        "![Hypotheses](figures/fig_hypotheses.svg)",
        "",
        "![Error taxonomy](figures/fig_error_taxonomy.svg)",
        "",
        "![R3 update effect](figures/fig_r3_update_effect.svg)",
        "",
        "## Generated artifacts",
        "",
    ]
    lines.extend(f"- `{item}`" for item in generated)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _display(value: Any) -> str:
    if value is None or value == "":
        return "--"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _tex(value: Any) -> str:
    replacements = {
        "\\": "\\textbackslash{}", "&": "\\&", "%": "\\%", "$": "\\$",
        "#": "\\#", "_": "\\_", "{": "\\{", "}": "\\}",
    }
    return "".join(replacements.get(character, character) for character in str(value))
