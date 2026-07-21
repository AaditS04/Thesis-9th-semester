"""Dependency-free vector figures suitable for paper drafts."""

from __future__ import annotations

import html
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000"]
INK = "#17202A"
GRID = "#D5D8DC"
BACKGROUND = "#FFFFFF"


class Svg:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.items = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#FFFFFF"/>',
            '<style>text{font-family:Inter,Arial,sans-serif;fill:#17202A}.title{font-size:20px;font-weight:700}.label{font-size:12px}.small{font-size:10px}.panel{font-size:14px;font-weight:700}</style>',
        ]

    def line(self, x1: float, y1: float, x2: float, y2: float, color: str = INK, width: float = 1, dash: str = "") -> None:
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"{extra}/>' )

    def circle(self, x: float, y: float, radius: float, color: str, fill: str | None = None) -> None:
        self.items.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" stroke="{color}" stroke-width="1.5" fill="{fill or color}"/>')

    def rect(self, x: float, y: float, width: float, height: float, fill: str, stroke: str = "none") -> None:
        self.items.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" fill="{fill}" stroke="{stroke}"/>')

    def text(self, x: float, y: float, text: Any, css: str = "label", anchor: str = "start", rotate: int = 0) -> None:
        transform = f' transform="rotate({rotate} {x:.2f} {y:.2f})"' if rotate else ""
        self.items.append(f'<text x="{x:.2f}" y="{y:.2f}" class="{css}" text-anchor="{anchor}"{transform}>{html.escape(str(text))}</text>')

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join([*self.items, "</svg>"]), encoding="utf-8")


def h_complexity_figure(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    dimensions = [dimension for dimension in ("R1", "R2", "R3", "R4", "R5", "R6") if any(row["dimension_id"] == dimension for row in rows)]
    width, height = 1200, 760
    svg = Svg(width, height)
    svg.text(40, 32, "CalibRead hallucination surface H(θ,Q)", "title")
    svg.text(40, 52, "False commits per incoming query; bars show world-cluster 95% intervals", "label")
    panel_w, panel_h = 370, 300
    for panel_index, dimension in enumerate(dimensions):
        column, row_index = panel_index % 3, panel_index // 3
        x0, y0 = 55 + column * 390, 90 + row_index * 330
        subset = [row for row in rows if row["dimension_id"] == dimension]
        labels = [str(row["theta_value"]) for row in subset]
        svg.text(x0, y0 - 12, f"{dimension}: {subset[0]['theta_factor'] if subset else ''}", "panel")
        _axes(svg, x0, y0, panel_w, panel_h, 0, 1, labels)
        count = max(1, len(subset))
        points = []
        for index, item in enumerate(subset):
            x = x0 + 35 + index * (panel_w - 55) / max(1, count - 1)
            y = _map_y(float(item["H_false_commit"]), y0, panel_h, 0, 1)
            low = _map_y(float(item["H_ci_low"]), y0, panel_h, 0, 1)
            high = _map_y(float(item["H_ci_high"]), y0, panel_h, 0, 1)
            svg.line(x, low, x, high, COLORS[0], 1.5)
            points.append((x, y))
        for first, second in zip(points, points[1:]):
            svg.line(first[0], first[1], second[0], second[1], COLORS[0], 2)
        for x, y in points:
            svg.circle(x, y, 4, COLORS[0])
    svg.save(path)


def risk_coverage_figure(path: Path, rows: Sequence[Dict[str, Any]], target: float) -> None:
    svg = Svg(900, 560)
    svg.text(45, 32, "Risk–coverage operating curves", "title")
    x0, y0, width, height = 80, 70, 760, 420
    _axes(svg, x0, y0, width, height, 0, max(0.2, max((float(row["false_commit_risk"]) for row in rows), default=0.2)), [])
    svg.line(x0 + 35, _map_y(target, y0, height, 0, max(0.2, max((float(row["false_commit_risk"]) for row in rows), default=0.2))), x0 + width - 20, _map_y(target, y0, height, 0, max(0.2, max((float(row["false_commit_risk"]) for row in rows), default=0.2))), "#A93226", 1.5, "6 4")
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row["dimension_id"]), []).append(row)
    maximum = max(0.2, max((float(row["false_commit_risk"]) for row in rows), default=0.2))
    for index, (label, group) in enumerate(sorted(groups.items())):
        color = COLORS[index % len(COLORS)]
        points = sorted((float(item["answer_coverage"]), float(item["false_commit_risk"])) for item in group)
        for first, second in zip(points, points[1:]):
            svg.line(_map_x(first[0], x0, width), _map_y(first[1], y0, height, 0, maximum), _map_x(second[0], x0, width), _map_y(second[1], y0, height, 0, maximum), color, 2)
        for x, y in points[:: max(1, len(points) // 12)]:
            svg.circle(_map_x(x, x0, width), _map_y(y, y0, height, 0, maximum), 2.5, color)
        svg.text(690 + (index % 2) * 70, 90 + (index // 2) * 18, label, "small")
        svg.line(675 + (index % 2) * 70, 86 + (index // 2) * 18, 687 + (index % 2) * 70, 86 + (index // 2) * 18, color, 2)
    svg.text(430, 535, "Answer coverage", "label", "middle")
    svg.text(18, 290, "False-commit risk", "label", "middle", -90)
    svg.save(path)


def calibration_figure(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    svg = Svg(700, 590)
    svg.text(40, 32, "Confidence reliability", "title")
    x0, y0, width, height = 80, 70, 540, 440
    _axes(svg, x0, y0, width, height, 0, 1, [])
    svg.line(_map_x(0, x0, width), _map_y(0, y0, height, 0, 1), _map_x(1, x0, width), _map_y(1, y0, height, 0, 1), "#777777", 1.5, "6 4")
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row["model_id"]), []).append(row)
    for index, (model, group) in enumerate(sorted(groups.items())):
        color = COLORS[index % len(COLORS)]
        points = sorted((float(item["mean_confidence"]), float(item["empirical_correctness"])) for item in group)
        for first, second in zip(points, points[1:]):
            svg.line(_map_x(first[0], x0, width), _map_y(first[1], y0, height, 0, 1), _map_x(second[0], x0, width), _map_y(second[1], y0, height, 0, 1), color, 2)
        for x, y in points:
            svg.circle(_map_x(x, x0, width), _map_y(y, y0, height, 0, 1), 4, color)
        svg.text(95, 92 + index * 18, model, "small")
    svg.text(350, 555, "Reported confidence score", "label", "middle")
    svg.text(18, 290, "Empirical correctness", "label", "middle", -90)
    svg.save(path)


def hard_group_figure(path: Path, rows: Sequence[Dict[str, Any]], target: float) -> None:
    rows = [row for row in rows if row.get("group_id") != "aggregate"]
    svg = Svg(1000, 620)
    svg.text(40, 30, "Hard-group false-commit audit", "title")
    x0, y0, width, height = 80, 70, 860, 430
    maximum = max(0.12, max((float(row.get("risk_ucb", 0)) for row in rows), default=0.12))
    _axes(svg, x0, y0, width, height, 0, maximum, [])
    svg.line(x0 + 35, _map_y(target, y0, height, 0, maximum), x0 + width - 20, _map_y(target, y0, height, 0, maximum), "#A93226", 1.5, "6 4")
    bar_width = (width - 70) / max(1, len(rows)) * 0.65
    for index, row in enumerate(rows):
        x = x0 + 42 + index * (width - 70) / max(1, len(rows))
        risk = float(row.get("false_commit_risk", 0))
        y = _map_y(risk, y0, height, 0, maximum)
        base = _map_y(0, y0, height, 0, maximum)
        svg.rect(x - bar_width / 2, y, bar_width, base - y, COLORS[0])
        svg.line(x, _map_y(float(row.get("risk_lcb", 0)), y0, height, 0, maximum), x, _map_y(float(row.get("risk_ucb", 0)), y0, height, 0, maximum), INK, 1.2)
        svg.text(x, 520, str(row.get("group_id", "")).replace("_", " "), "small", "end", -45)
    svg.text(20, 285, "False-commit risk", "label", "middle", -90)
    svg.save(path)


def domain_transfer_figure(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    domains = ["general", "biomedical", "legal", "technical"]
    values = {(row.get("source"), row.get("target")): row.get("gap") for row in rows if row.get("supported")}
    svg = Svg(680, 620)
    svg.text(35, 32, "Cross-domain calibration degradation", "title")
    x0, y0, cell = 180, 100, 95
    maximum = max((abs(float(value)) for value in values.values() if value is not None), default=0.05)
    maximum = max(maximum, 0.02)
    for row_index, source in enumerate(domains):
        svg.text(x0 - 12, y0 + row_index * cell + cell / 2 + 4, source, "label", "end")
        svg.text(x0 + row_index * cell + cell / 2, y0 - 14, domains[row_index], "label", "middle", -25)
        for column_index, target in enumerate(domains):
            value = values.get((source, target))
            color = "#F2F3F4" if value is None else _diverging(float(value), maximum)
            svg.rect(x0 + column_index * cell, y0 + row_index * cell, cell - 2, cell - 2, color, "#FFFFFF")
            svg.text(x0 + column_index * cell + cell / 2, y0 + row_index * cell + cell / 2 + 4, "—" if value is None else f"{100*float(value):.1f} pp", "label", "middle")
    svg.text(370, 545, "Target domain", "label", "middle")
    svg.text(40, 290, "Calibration source", "label", "middle", -90)
    svg.save(path)


def cpr_figure(path: Path, summary: Mapping[str, Any]) -> None:
    svg = Svg(760, 480)
    svg.text(35, 32, "Conformal Parametric Read operating point", "title")
    labels = ["Target coverage", "Empirical coverage", "Fallback rate"]
    values = [float(summary.get("coverage_target") or 0), float(summary.get("empirical_coverage") or 0), float(summary.get("fallback_rate") or 0)]
    x0, y0, width, height = 90, 75, 600, 300
    _axes(svg, x0, y0, width, height, 0, 1, labels)
    spacing = (width - 70) / len(values)
    for index, (label, value) in enumerate(zip(labels, values)):
        x = x0 + 55 + index * spacing
        y = _map_y(value, y0, height, 0, 1)
        base = _map_y(0, y0, height, 0, 1)
        svg.rect(x - 32, y, 64, base - y, COLORS[index])
        svg.text(x, y - 8, f"{value:.3f}", "label", "middle")
        svg.text(x, 405, label, "label", "middle")
    svg.text(35, 448, f"Rank cutoff: {summary.get('rank_cutoff')} · mean non-vacuous size: {summary.get('mean_nonvacuous_set_size')}", "label")
    svg.save(path)


def hypothesis_figure(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    svg = Svg(900, 480)
    svg.text(35, 32, "Distance from each hypothesis-specific success boundary", "title")
    x0, y0, width, height = 230, 70, 600, 330
    centered = []
    for row in rows:
        threshold = 0.0 if row.get("hypothesis_id") == "H2" else float(row.get("preregistered_margin") or 0)
        centered.extend(float(value) - threshold for value in (
            row.get("ci_low"), row.get("ci_high"), row.get("effect_estimate")
        ) if value not in (None, ""))
    finite = centered
    low, high = (min(finite + [-0.05]), max(finite + [0.1])) if finite else (-0.05, 0.1)
    span = high - low or 1
    low -= 0.1 * span
    high += 0.1 * span
    svg.line(_scale(0, low, high, x0, x0 + width), y0, _scale(0, low, high, x0, x0 + width), y0 + height, "#777777", 1, "5 4")
    for index, row in enumerate(rows):
        y = y0 + 38 + index * 58
        svg.text(x0 - 15, y + 4, row.get("hypothesis_id"), "panel", "end")
        estimate = row.get("effect_estimate")
        if estimate in (None, ""):
            svg.text(x0 + 10, y + 4, "unsupported", "label")
            continue
        threshold = 0.0 if row.get("hypothesis_id") == "H2" else float(row.get("preregistered_margin") or 0)
        estimate = float(estimate) - threshold
        lower = float(row.get("ci_low") if row.get("ci_low") not in (None, "") else estimate + threshold) - threshold
        upper = float(row.get("ci_high") if row.get("ci_high") not in (None, "") else estimate + threshold) - threshold
        color = COLORS[2] if row.get("decision") == "SUPPORTED" else COLORS[1]
        svg.line(_scale(lower, low, high, x0, x0 + width), y, _scale(upper, low, high, x0, x0 + width), y, color, 3)
        svg.circle(_scale(float(estimate), low, high, x0, x0 + width), y, 5, color)
        svg.text(x0 + width - 4, y - 9, str(row.get("decision", "")), "small", "end")
    svg.text(x0 + width / 2, 445, "Probability-point distance from prespecified success boundary", "label", "middle")
    svg.save(path)


def error_taxonomy_figure(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    totals: Dict[str, int] = {}
    for row in rows:
        code = str(row.get("error_code", "other"))
        totals[code] = totals.get(code, 0) + int(row.get("count", 0))
    ordered = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    svg = Svg(920, 520)
    svg.text(35, 30, "Error taxonomy", "title")
    x0, y0, width, height = 290, 65, 560, 390
    maximum = max((value for _, value in ordered), default=1)
    for index, (label, value) in enumerate(ordered[:10]):
        y = y0 + 20 + index * 35
        svg.text(x0 - 12, y + 11, label.replace("_", " "), "small", "end")
        bar = value / maximum * width
        svg.rect(x0, y, bar, 22, COLORS[index % len(COLORS)])
        svg.text(x0 + bar + 7, y + 15, value, "label")
    svg.save(path)


def temporal_update_figure(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    svg = Svg(720, 500)
    svg.text(35, 32, "R3 paired controlled-update effect", "title")
    test = next((row for row in rows if row.get("split") == "test"), rows[0] if rows else None)
    x0, y0, width, height = 90, 70, 560, 330
    _axes(svg, x0, y0, width, height, 0, 1, ["T0", "T2"])
    if test:
        values = [float(test.get("t0_current_accuracy") or 0), float(test.get("t2_current_accuracy") or 0)]
        for index, (label, value) in enumerate(zip(("T0", "T2"), values)):
            x = x0 + 175 + index * 250
            y = _map_y(value, y0, height, 0, 1)
            base = _map_y(0, y0, height, 0, 1)
            svg.rect(x - 45, y, 90, base - y, COLORS[index])
            svg.text(x, y - 10, f"{value:.3f}", "label", "middle")
            svg.text(x, 425, label, "panel", "middle")
        gain = float(test.get("current_accuracy_gain") or 0)
        low = test.get("current_gain_ci_low")
        high = test.get("current_gain_ci_high")
        interval = "" if low is None or high is None else f" (95% CI {float(low):.3f}, {float(high):.3f})"
        svg.text(360, 465, f"Paired gain: {gain:.3f}{interval}; n={test.get('n_pairs')}", "label", "middle")
    else:
        svg.text(360, 245, "No matched T0/T2 current-after-update rows supplied", "label", "middle")
    svg.text(22, 250, "Current-value accuracy", "label", "middle", -90)
    svg.save(path)


def _axes(svg: Svg, x0: float, y0: float, width: float, height: float, ymin: float, ymax: float, labels: Sequence[str]) -> None:
    left, right, top, bottom = x0 + 35, x0 + width - 20, y0 + 10, y0 + height - 35
    svg.line(left, top, left, bottom, INK, 1)
    svg.line(left, bottom, right, bottom, INK, 1)
    for index in range(5):
        value = ymin + index * (ymax - ymin) / 4
        y = _map_y(value, y0, height, ymin, ymax)
        svg.line(left, y, right, y, GRID, 0.8)
        svg.text(left - 8, y + 4, f"{value:.2f}", "small", "end")
    if labels:
        for index, label in enumerate(labels):
            x = left + index * (right - left) / max(1, len(labels) - 1)
            svg.text(x, bottom + 18, label, "small", "end", -25)


def _map_x(value: float, x0: float, width: float) -> float:
    return x0 + 35 + value * (width - 55)


def _map_y(value: float, y0: float, height: float, ymin: float, ymax: float) -> float:
    return y0 + 10 + (1 - (value - ymin) / max(1e-12, ymax - ymin)) * (height - 45)


def _scale(value: float, low: float, high: float, start: float, end: float) -> float:
    return start + (value - low) / max(1e-12, high - low) * (end - start)


def _diverging(value: float, maximum: float) -> str:
    ratio = min(1.0, abs(value) / maximum)
    if value >= 0:
        base = (213, 94, 0)
    else:
        base = (0, 114, 178)
    rgb = tuple(round(255 - ratio * (255 - component)) for component in base)
    return "#%02X%02X%02X" % rgb
