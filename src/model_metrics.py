"""Evaluation and drift-monitoring helpers for a binary classifier."""

import math


def _validate_labels(y_true, y_pred):
    if not isinstance(y_true, (list, tuple)) or not isinstance(y_pred, (list, tuple)):
        raise TypeError("y_true and y_pred must be lists or tuples")
    if len(y_true) == 0:
        raise ValueError("inputs must not be empty")
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    if any(v not in (0, 1) for v in [*y_true, *y_pred]):
        raise ValueError("labels must be 0 or 1")


def confusion_counts(y_true, y_pred):
    """Return (tp, fp, fn, tn), treating 1 as the positive class."""
    _validate_labels(y_true, y_pred)
    tp = fp = fn = tn = 0
    for t, p in zip(y_true, y_pred):
        if t == 1 and p == 1:
            tp += 1
        elif t == 0 and p == 1:
            fp += 1
        elif t == 1 and p == 0:
            fn += 1
        else:
            tn += 1
    return tp, fp, fn, tn


def precision(y_true, y_pred):
    tp, fp, _, _ = confusion_counts(y_true, y_pred)
    return tp / (tp + fp) if (tp + fp) else 0.0


def recall(y_true, y_pred):
    tp, _, fn, _ = confusion_counts(y_true, y_pred)
    return tp / (tp + fn) if (tp + fn) else 0.0


def f1_score(y_true, y_pred):
    p, r = precision(y_true, y_pred), recall(y_true, y_pred)
    return 2 * p * r / (p + r) if (p + r) else 0.0


def population_stability_index(expected, actual, bins=10):
    """PSI between a reference sample (e.g. training scores) and a new sample.

    Uses equal-width bins over the reference range; values outside that range
    go into the edge bins. A small epsilon avoids log(0) for empty bins.
    """
    if not expected or not actual:
        raise ValueError("samples must not be empty")
    if bins < 1:
        raise ValueError("bins must be >= 1")
    lo, hi = min(expected), max(expected)
    if lo == hi:
        raise ValueError("expected sample must contain more than one distinct value")
    width = (hi - lo) / bins

    def proportions(sample):
        counts = [0] * bins
        for x in sample:
            idx = min(max(int((x - lo) / width), 0), bins - 1)
            counts[idx] += 1
        return [c / len(sample) for c in counts]

    eps = 1e-6
    psi = 0.0
    for e, a in zip(proportions(expected), proportions(actual)):
        e, a = max(e, eps), max(a, eps)
        psi += (a - e) * math.log(a / e)
    return psi


def drift_level(psi):
    """Rule-of-thumb PSI bands: <0.1 stable, 0.1-0.25 moderate, >=0.25 significant."""
    if psi < 0:
        raise ValueError("PSI cannot be negative")
    if psi < 0.1:
        return "stable"
    if psi < 0.25:
        return "moderate"
    return "significant"