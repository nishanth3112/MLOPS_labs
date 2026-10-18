# MLOps Labs

Lab submissions for **IE 7374 / DADS 7305 – MLOps** at Northeastern University.

Each lab is based on a lab from the [course repository](https://github.com/raminmohammadi/MLOps) and modified with my own changes, as the assignment requires.

## Labs

| # | Lab | What it covers | Folder |
|---|---|---|---|
| 1 | GitHub Lab 1 | Unit testing with pytest and unittest, run automatically by GitHub Actions. Tests a machine learning metrics and data-drift module instead of the original calculator. | [`github_lab1/`](github_lab1/) |
| 2 | Cloud Run Lab (Beginner) | An ML model monitoring REST API built with Flask. `POST /evaluate` checks supplied accuracy and drift (PSI) values against thresholds and returns `pass` or `review`. Includes input validation, 40 pytest tests, a Docker image, and a verified deployment on Google Cloud Run. Replaces the original Hello World app. | [`github_Lab2/`](github_Lab2/) ([README](github_Lab2/README.md)) |

## Tools used

- **Python** 3.12+
- **uv** for environments and dependencies
- **GitHub Actions** for automated testing (Lab 1)
- **Flask** and **Gunicorn** for the REST API (Lab 2)
- **Docker** and **Google Cloud Run** for containerized deployment (Lab 2)

## Running a lab

```bash
git clone https://github.com/nishanth3112/MLOPS_labs.git
cd MLOPS_labs/<lab-folder>
uv sync
uv run pytest
```

Lab 1 uses `uv`; Lab 2 uses `pip` and a `requirements.txt` (see [`github_Lab2/README.md`](github_Lab2/README.md)).

Each lab folder has its own README with full details:

- [Lab 1: `github_lab1/README.md`](github_lab1/README.md)
- [Lab 2: `github_Lab2/README.md`](github_Lab2/README.md)
