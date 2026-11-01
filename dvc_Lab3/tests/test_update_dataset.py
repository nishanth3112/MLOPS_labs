"""Checks on update_dataset.py, run against temporary data only."""

import pandas as pd

import update_dataset


def test_bin_edges_are_right_inclusive(wine_v1):
    df = wine_v1.copy()
    cases = [(11.0, "low"), (12.0, "low"), (12.01, "medium"), (13.5, "medium"), (13.51, "high")]
    df.loc[: len(cases) - 1, "alcohol"] = [alcohol for alcohol, _ in cases]

    updated = update_dataset.add_alcohol_band(df)

    actual = updated["alcohol_band"].iloc[: len(cases)].tolist()
    assert actual == [band for _, band in cases]


def test_update_is_idempotent(v1_csv, monkeypatch):
    # Point the script at the temporary copy so the real data/wine.csv is never touched.
    monkeypatch.setattr(update_dataset, "DATA_PATH", v1_csv)

    update_dataset.main()
    first_run = v1_csv.read_bytes()
    update_dataset.main()
    second_run = v1_csv.read_bytes()

    assert first_run == second_run
    assert pd.read_csv(v1_csv).shape == (178, 15)
