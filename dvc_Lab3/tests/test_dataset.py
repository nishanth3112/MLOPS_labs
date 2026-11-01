"""Checks on the real V2 dataset at data/wine.csv."""

EXPECTED_SHAPE = (178, 15)
EXPECTED_CLASSES = {0, 1, 2}
EXPECTED_BANDS = {"low", "medium", "high"}
EXPECTED_DISTRIBUTION = {"low": 22, "medium": 101, "high": 55}


def expected_band(alcohol: float) -> str:
    # Written out by hand so it independently checks pd.cut's right-inclusive bins.
    if alcohol <= 12:
        return "low"
    if alcohol <= 13.5:
        return "medium"
    return "high"


def test_shape(wine_v2):
    assert wine_v2.shape == EXPECTED_SHAPE


def test_no_missing_values(wine_v2):
    assert wine_v2.isna().sum().sum() == 0


def test_target_classes(wine_v2):
    assert set(wine_v2["target"].unique().tolist()) == EXPECTED_CLASSES


def test_alcohol_band_values(wine_v2):
    assert "alcohol_band" in wine_v2.columns
    assert set(wine_v2["alcohol_band"].unique().tolist()) == EXPECTED_BANDS


def test_alcohol_band_distribution(wine_v2):
    assert wine_v2["alcohol_band"].value_counts().to_dict() == EXPECTED_DISTRIBUTION


def test_alcohol_band_matches_bin_boundaries(wine_v2):
    expected = wine_v2["alcohol"].apply(expected_band)
    mismatches = wine_v2[wine_v2["alcohol_band"] != expected]
    assert mismatches.empty, mismatches[["alcohol", "alcohol_band"]]
