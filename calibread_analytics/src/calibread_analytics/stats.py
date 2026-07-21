"""Deterministic statistical primitives used by the confirmatory analyses."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from statistics import NormalDist
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence, Tuple


EPS = 1e-14


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    center = mean(values)
    return sum((value - center) ** 2 for value in values) / (len(values) - 1)


def percentile(values: Sequence[float], probability: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    position = min(1.0, max(0.0, probability)) * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def bootstrap_cluster_mean(
    values_by_cluster: Mapping[str, Sequence[float]],
    replicates: int,
    seed: int,
) -> List[float]:
    clusters = sorted(values_by_cluster)
    rng = random.Random(seed)
    output = []
    for _ in range(replicates):
        sampled = [clusters[rng.randrange(len(clusters))] for _ in clusters]
        values = [value for cluster in sampled for value in values_by_cluster[cluster]]
        output.append(mean(values))
    return output


def cluster_mean_ci(
    rows: Sequence[Dict[str, Any]],
    value: Callable[[Dict[str, Any]], float],
    cluster: Callable[[Dict[str, Any]], str],
    replicates: int,
    seed: int,
    confidence: float = 0.95,
) -> Tuple[float, float, float]:
    grouped: Dict[str, List[float]] = defaultdict(list)
    for row in rows:
        grouped[cluster(row)].append(float(value(row)))
    estimate = mean([item for items in grouped.values() for item in items])
    boot = bootstrap_cluster_mean(grouped, replicates, seed)
    alpha = 1 - confidence
    return estimate, percentile(boot, alpha / 2), percentile(boot, 1 - alpha / 2)


def one_sided_mean_greater(values: Sequence[float], margin: float = 0.0) -> Tuple[float, float]:
    if len(values) < 2:
        return float("nan"), 1.0
    effect = mean(values) - margin
    standard_error = math.sqrt(variance(values) / len(values))
    if standard_error <= EPS:
        return effect, 0.0 if effect > 0 else 1.0
    z_score = effect / standard_error
    return effect, 1 - NormalDist().cdf(z_score)


def holm_adjust(p_values: Mapping[str, float]) -> Dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    adjusted: Dict[str, float] = {}
    running = 0.0
    total = len(ordered)
    for rank, (key, value) in enumerate(ordered):
        candidate = min(1.0, (total - rank) * max(0.0, min(1.0, value)))
        running = max(running, candidate)
        adjusted[key] = running
    return adjusted


def regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    log_term = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    log_term += a * math.log(x) + b * math.log1p(-x)
    front = math.exp(log_term)
    if x < (a + 1) / (a + b + 2):
        return front * _beta_continued_fraction(a, b, x) / a
    return 1 - front * _beta_continued_fraction(b, a, 1 - x) / b


def _beta_continued_fraction(a: float, b: float, x: float) -> float:
    maximum_iterations = 300
    fp_min = 1e-300
    qab = a + b
    qap = a + 1
    qam = a - 1
    c = 1.0
    d = 1 - qab * x / qap
    if abs(d) < fp_min:
        d = fp_min
    d = 1 / d
    result = d
    for iteration in range(1, maximum_iterations + 1):
        even = 2 * iteration
        numerator = iteration * (b - iteration) * x / ((qam + even) * (a + even))
        d = 1 + numerator * d
        if abs(d) < fp_min:
            d = fp_min
        c = 1 + numerator / c
        if abs(c) < fp_min:
            c = fp_min
        d = 1 / d
        result *= d * c
        numerator = -(a + iteration) * (qab + iteration) * x / ((a + even) * (qap + even))
        d = 1 + numerator * d
        if abs(d) < fp_min:
            d = fp_min
        c = 1 + numerator / c
        if abs(c) < fp_min:
            c = fp_min
        d = 1 / d
        delta = d * c
        result *= delta
        if abs(delta - 1) < 3e-12:
            break
    return result


def beta_quantile(probability: float, a: float, b: float) -> float:
    if probability <= 0:
        return 0.0
    if probability >= 1:
        return 1.0
    lower, upper = 0.0, 1.0
    for _ in range(100):
        midpoint = (lower + upper) / 2
        if regularized_beta(midpoint, a, b) < probability:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    lower = 0.0 if k == 0 else beta_quantile(alpha / 2, k, n - k + 1)
    upper = 1.0 if k == n else beta_quantile(1 - alpha / 2, k + 1, n - k)
    return lower, upper


def clopper_lower(k: int, n: int, alpha: float = 0.05) -> float:
    return 0.0 if k == 0 or n <= 0 else beta_quantile(alpha, k, n - k + 1)


def clopper_upper(k: int, n: int, alpha: float = 0.05) -> float:
    return 1.0 if n <= 0 or k == n else beta_quantile(1 - alpha, k + 1, n - k)


def binomial_p_greater(k: int, n: int, probability: float) -> float:
    if n <= 0:
        return 1.0
    if k <= 0:
        return 1.0
    return regularized_beta(probability, k, n - k + 1)


def pava_increasing(successes: Sequence[float], totals: Sequence[float]) -> List[float]:
    blocks: List[Dict[str, Any]] = []
    for index, (success, total) in enumerate(zip(successes, totals)):
        blocks.append({"start": index, "end": index, "success": success, "total": total})
        while len(blocks) >= 2:
            left, right = blocks[-2], blocks[-1]
            left_rate = left["success"] / left["total"] if left["total"] else 0.0
            right_rate = right["success"] / right["total"] if right["total"] else 0.0
            if left_rate <= right_rate + EPS:
                break
            blocks[-2:] = [{
                "start": left["start"], "end": right["end"],
                "success": left["success"] + right["success"],
                "total": left["total"] + right["total"],
            }]
    fitted = [0.0] * len(successes)
    for block in blocks:
        rate = block["success"] / block["total"] if block["total"] else 0.0
        for index in range(block["start"], block["end"] + 1):
            fitted[index] = min(1 - EPS, max(EPS, rate))
    return fitted


def bernoulli_log_likelihood(successes: Sequence[float], totals: Sequence[float], probabilities: Sequence[float]) -> float:
    total = 0.0
    for success, count, probability in zip(successes, totals, probabilities):
        p = min(1 - EPS, max(EPS, probability))
        total += success * math.log(p) + (count - success) * math.log1p(-p)
    return total


def monotone_lrt(successes: Sequence[float], totals: Sequence[float]) -> Tuple[float, List[float]]:
    fitted = pava_increasing(successes, totals)
    pooled = sum(successes) / sum(totals) if sum(totals) else 0.0
    null = [pooled] * len(successes)
    statistic = max(0.0, 2 * (
        bernoulli_log_likelihood(successes, totals, fitted)
        - bernoulli_log_likelihood(successes, totals, null)
    ))
    return statistic, fitted
