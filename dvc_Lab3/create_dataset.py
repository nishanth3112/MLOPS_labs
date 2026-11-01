"""Export the scikit-learn Wine dataset to data/wine.csv for DVC tracking."""

from pathlib import Path

import pandas as pd
from sklearn.datasets import load_wine

# Resolve paths from this file so the output location does not depend on the cwd.
DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_PATH = DATA_DIR / "wine.csv"

EXPECTED_ROWS = 178
EXPECTED_FEATURES = 13
EXPECTED_COLUMNS = EXPECTED_FEATURES + 1  # features + target
TARGET_COLUMN = "target"
EXPECTED_CLASSES = {0, 1, 2}


def load_dataset() -> pd.DataFrame:
    # load_wine reads a file bundled with scikit-learn, so the output is identical on every run.
    return load_wine(as_frame=True).frame


def validate_dataset(df: pd.DataFrame) -> None:
    if df.shape != (EXPECTED_ROWS, EXPECTED_COLUMNS):
        raise ValueError(
            f"Expected shape ({EXPECTED_ROWS}, {EXPECTED_COLUMNS}), got {df.shape}"
        )

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Missing '{TARGET_COLUMN}' column")

    missing = int(df.isna().sum().sum())
    if missing != 0:
        raise ValueError(f"Dataset contains {missing} missing values")

    classes = set(df[TARGET_COLUMN].unique().tolist())
    if classes != EXPECTED_CLASSES:
        raise ValueError(
            f"Expected target classes {sorted(EXPECTED_CLASSES)}, got {sorted(classes)}"
        )


def main() -> None:
    df = load_dataset()
    validate_dataset(df)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Wine dataset created")
    print(f"  Shape:          {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"  Missing values: {int(df.isna().sum().sum())}")
    print(f"  Output path:    {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
