import unittest

from src import model_metrics as mm


class TestModelMetrics(unittest.TestCase):
    def setUp(self):
        self.y_true = [1, 1, 1, 1, 0, 0, 0, 0]
        self.y_pred = [1, 1, 1, 0, 1, 0, 0, 0]

    def test_confusion_counts(self):
        self.assertEqual(mm.confusion_counts(self.y_true, self.y_pred), (3, 1, 1, 3))

    def test_precision_recall_f1(self):
        self.assertAlmostEqual(mm.precision(self.y_true, self.y_pred), 0.75)
        self.assertAlmostEqual(mm.recall(self.y_true, self.y_pred), 0.75)
        self.assertAlmostEqual(mm.f1_score(self.y_true, self.y_pred), 0.75)

    def test_zero_division_returns_zero(self):
        self.assertEqual(mm.precision([1, 1, 0], [0, 0, 0]), 0.0)
        self.assertEqual(mm.f1_score([1, 1, 0], [0, 0, 0]), 0.0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            mm.confusion_counts([1, 0], [1])
        with self.assertRaises(TypeError):
            mm.confusion_counts("10", "10")

    def test_psi_and_drift_level(self):
        ref = list(range(100))
        self.assertAlmostEqual(mm.population_stability_index(ref, ref), 0.0)
        shifted = [x + 50 for x in ref]
        self.assertEqual(mm.drift_level(mm.population_stability_index(ref, shifted)), "significant")
        self.assertEqual(mm.drift_level(0.15), "moderate")


if __name__ == "__main__":
    unittest.main()