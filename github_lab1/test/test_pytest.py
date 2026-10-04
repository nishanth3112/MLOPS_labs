import csv
from pathlib import Path

import pytest

from src import model_metrics as mm

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "predictions.csv"


def load_predictions():
    with DATA_FILE.open(newline="") as f:
        rows = list(csv.DictReader(f))
    return [int(r["y_true"]) for r in rows], [int(r["y_pred"]) for r in rows]


def test_confusion_counts():
    y_true = [1, 1, 1, 1, 0, 0, 0, 0]
    y_pred = [1, 1, 1, 0, 1, 0, 0, 0]
    assert mm.confusion_counts(y_true, y_pred) == (3, 1, 1, 3)


@pytest.mark.parametrize(
    "y_true, y_pred, exp_precision, exp_recall, exp_f1",
    [
        ([1, 0, 1, 0], [1, 0, 1, 0], 1.0, 1.0, 1.0),        # perfect model
        ([1, 1, 1, 0], [1, 0, 0, 0], 1.0, 1 / 3, 0.5),      # cautious model, misses positives
        ([1, 1, 0], [0, 0, 0], 0.0, 0.0, 0.0),              # never predicts positive
        ([0, 0, 1], [1, 1, 1], 1 / 3, 1.0, 0.5),            # flags everything
    ],
)
def test_precision_recall_f1(y_true, y_pred, exp_precision, exp_recall, exp_f1):
    assert mm.precision(y_true, y_pred) == pytest.approx(exp_precision)
    assert mm.recall(y_true, y_pred) == pytest.approx(exp_recall)
    assert mm.f1_score(y_true, y_pred) == pytest.approx(exp_f1)


def test_metrics_on_csv_dataset():
    y_true, y_pred = load_predictions()
    assert mm.confusion_counts(y_true, y_pred) == (6, 2, 3, 9)
    assert mm.precision(y_true, y_pred) == pytest.approx(0.75)
    assert mm.recall(y_true, y_pred) == pytest.approx(6 / 9)
    assert mm.f1_score(y_true, y_pred) == pytest.approx(12 / 17)


@pytest.mark.parametrize(
    "y_true, y_pred, error",
    [
        ([1, 0], [1], ValueError),        # length mismatch
        ([], [], ValueError),             # empty
        ([1, 2], [1, 0], ValueError),     # non-binary label
        ("10", "10", TypeError),          # wrong type
    ],
)
def test_invalid_inputs_raise(y_true, y_pred, error):
    with pytest.raises(error):
        mm.confusion_counts(y_true, y_pred)


def test_psi_identical_samples_is_zero():
    ref = list(range(100))
    assert mm.population_stability_index(ref, ref) == pytest.approx(0.0)


def test_psi_detects_shift():
    ref = list(range(100))
    shifted = [x + 50 for x in ref]
    psi = mm.population_stability_index(ref, shifted)
    assert psi > 0.25
    assert mm.drift_level(psi) == "significant"


@pytest.mark.parametrize(
    "psi, level",
    [(0.0, "stable"), (0.099, "stable"), (0.1, "moderate"), (0.249, "moderate"), (0.25, "significant")],
)
def test_drift_level_bands(psi, level):
    assert mm.drift_level(psi) == level


def test_psi_rejects_bad_input():
    with pytest.raises(ValueError):
        mm.population_stability_index([], [1, 2])
    with pytest.raises(ValueError):
        mm.population_stability_index([5, 5, 5], [1, 2])
    with pytest.raises(ValueError):
        mm.drift_level(-0.1)