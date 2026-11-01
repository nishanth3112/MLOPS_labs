"""Add an alcohol_band feature to data/wine.csv to create dataset version 2."""

from pathlib import Path

import pandas as pd

# Resolve paths from this file so the output location does not depend on the cwd.
DATA_PATH = Path(__file__).resolve().parent / "data" / "wine.csv"

EXPECTED_ROWS = 178
ORIGINAL_COLUMNS = 14
UPDATED_COLUMNS = ORIGINAL_COLUMNS + 1
SOURCE_COLUMN = "alcohol"
NEW_COLUMN = "alcohol_band"
BINS = [0, 12, 13.5, float("inf")]
LABELS = ["low", "medium", "high"]


def add_alcohol_band(df: pd.DataFrame) -> pd.DataFrame:
    # Drop any band from a previous run so re-running rebuilds it from the original columns.
    base = df.drop(columns=[NEW_COLUMN], errors="ignore")

    if base.shape != (EXPECTED_ROWS, ORIGINAL_COLUMNS):
        raise ValueError(
            f"Expected original shape ({EXPECTED_ROWS}, {ORIGINAL_COLUMNS}), got {base.shape}"
        )
    if SOURCE_COLUMN not in base.columns:
        raise ValueError(f"Missing '{SOURCE_COLUMN}' column")

    updated = base.copy()
    updated[NEW_COLUMN] = pd.cut(updated[SOURCE_COLUMN], bins=BINS, labels=LABELS)
    return updated


def validate_dataset(df: pd.DataFrame) -> None:
    if df.shape != (EXPECTED_ROWS, UPDATED_COLUMNS):
        raise ValueError(
            f"Expected updated shape ({EXPECTED_ROWS}, {UPDATED_COLUMNS}), got {df.shape}"
        )

    missing = int(df.isna().sum().sum())
    if missing != 0:
        raise ValueError(f"Dataset contains {missing} missing values after update")


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    updated = add_alcohol_band(df)
    validate_dataset(updated)

    updated.to_csv(DATA_PATH, index=False)

    print("Wine dataset updated")
    print(f"  Shape:       {updated.shape[0]} rows x {updated.shape[1]} columns")
    print(f"  Output path: {DATA_PATH}")
    print(f"  {NEW_COLUMN} distribution:")
    for band, count in updated[NEW_COLUMN].value_counts(sort=False).items():
        print(f"    {band:<7} {count}")


if __name__ == "__main__":
    main()
