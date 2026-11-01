import sys
from pathlib import Path

import pandas as pd
import pytest

# The dataset scripts live in dvc_Lab3/, one level above this tests/ folder.
LAB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_DIR))

import create_dataset  # noqa: E402

REAL_DATA_PATH = LAB_DIR / "data" / "wine.csv"


@pytest.fixture(scope="session")
def wine_v2() -> pd.DataFrame:
    """The real DVC-tracked dataset, read-only."""
    if not REAL_DATA_PATH.exists():
        pytest.fail(f"{REAL_DATA_PATH} not found. Run `dvc pull` first.")
    return pd.read_csv(REAL_DATA_PATH)


@pytest.fixture
def wine_v1() -> pd.DataFrame:
    """A fresh V1 dataset built from the copy bundled with scikit-learn (no network)."""
    return create_dataset.load_dataset()


@pytest.fixture
def v1_csv(tmp_path, wine_v1) -> Path:
    """A temporary V1 CSV the update script can safely overwrite."""
    path = tmp_path / "wine.csv"
    wine_v1.to_csv(path, index=False)
    return path
