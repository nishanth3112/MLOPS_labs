# GitHub Lab 1: Testing an ML Metrics Module with GitHub Actions

Based on `Labs/Github_Labs/Lab1` from the [course repo](https://github.com/raminmohammadi/MLOps). The original lab tests a small calculator. This version tests code that measures **how well a machine learning model performs**, and GitHub runs the tests automatically on every change.

## What the code does

`src/model_metrics.py` answers simple questions about a model that predicts whether a loan will default:

| Function | Question it answers |
|---|---|
| `confusion_counts` | How many predictions were right or wrong, and in which way? |
| `precision` | Of the loans the model flagged, how many actually defaulted? |
| `recall` | Of the loans that actually defaulted, how many did the model catch? |
| `f1_score` | One number that balances precision and recall |
| `population_stability_index` | Has new data shifted compared to the data the model was trained on? |
| `drift_level` | Turns that shift score into *stable*, *moderate*, or *significant* |

## The data

`data/predictions.csv` holds 20 made-up loan predictions. It was designed so the correct answers are known in advance (precision 0.75, recall ≈ 0.67, F1 ≈ 0.71), which makes it easy to test against.

## The tests

- `test/test_pytest.py`: 18 tests using **pytest**
- `test/test_unittest.py`: 6 tests using Python's built-in **unittest**

They check that every function returns the right answer and rejects bad input (empty lists, mismatched lengths, labels other than 0/1).

## What runs automatically

Every push or pull request to `main` triggers GitHub Actions, which:

1. Sets up Python 3.12, 3.13, and 3.14 in parallel
2. Installs the exact package versions listed in `uv.lock`
3. Runs all tests and requires at least 90% of the code to be tested
4. Saves a test report for each Python version

The `main` branch is protected: a pull request can only be merged if all checks pass. The workflow files live in the repo's root `.github/workflows/` folder.

## Proof that it works

[PR #1](https://github.com/nishanth3112/MLOPS_labs/pull/1) deliberately added a bug: `precision` was secretly calculating recall instead. The pytest checks failed on all three Python versions, GitHub blocked the merge, and the PR was closed without merging.

One interesting finding: the unittest suite **missed** the bug at first, because its only example happened to have equal precision and recall. A new test with different values was added, so both test suites now catch it.

## Run it yourself

You need [uv](https://docs.astral.sh/uv/) installed.

```bash
git clone https://github.com/nishanth3112/MLOPS_labs.git
cd MLOPS_labs/github_lab1
uv sync
uv run pytest -v
```

Expected result: **24 passed**.

## Changes from the original lab

| | Original lab | This version |
|---|---|---|
| Code being tested | Calculator (add, subtract, multiply) | ML metrics and data-drift checks |
| Data | None | 20-row predictions file |
| Setup tool | `venv` + `pip` | `uv` |
| Number of tests | 4 pytest + 4 unittest | 18 pytest + 6 unittest |
| Python versions tested | 3.8 | 3.12, 3.13, 3.14 |
| Coverage requirement | None | At least 90% |
| Merge protection | None | All checks must pass |

## Folder layout

```
github_lab1/
├── data/
│   └── predictions.csv     # 20 sample predictions
├── src/
│   └── model_metrics.py    # metrics and drift functions
├── test/
│   ├── test_pytest.py      # pytest tests
│   └── test_unittest.py    # unittest tests
├── pyproject.toml          # project settings and dependencies
├── uv.lock                 # exact package versions
└── .python-version         # Python version (3.12)
```
