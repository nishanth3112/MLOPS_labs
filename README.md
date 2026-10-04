# MLOps Labs

Lab submissions for **IE 7374 / DADS 7305 – MLOps** at Northeastern University.

Each lab is based on a lab from the [course repository](https://github.com/raminmohammadi/MLOps) and modified with my own changes, as the assignment requires.

## Labs

| # | Lab | What it covers | Folder |
|---|---|---|---|
| 1 | GitHub Lab 1 | Unit testing with pytest and unittest, run automatically by GitHub Actions. Tests a machine learning metrics and data-drift module instead of the original calculator. | [`github_lab1/`](github_lab1/) |

## Tools used

- **Python** 3.12+
- **uv** for environments and dependencies
- **GitHub Actions** for automated testing

## Running a lab

```bash
git clone https://github.com/nishanth3112/MLOPS_labs.git
cd MLOPS_labs/<lab-folder>
uv sync
uv run pytest
```

Each lab folder has its own README with full details.
