# CodePulse AI — Explainable Git Change-Risk Analytics

![Python CI](https://github.com/ranepiyush123/codepulse-ai/actions/workflows/ci.yml/badge.svg)

A portfolio-ready **Python + FastAPI + Git analytics** application that highlights files with elevated change activity. Includes a web dashboard, REST API, CLI, automated tests, GitHub Actions CI, and Docker.

> **Accuracy and scope:** Version 0.1 is an **explainable heuristic system**, not a trained machine-learning model. Its scores are **not** defect probabilities, and the app does not claim to predict actual bugs. “AI” is part of the project name, not a claim about the current algorithm.

## What it does

- Reads the last N commits from a **local Git repository**.
- Aggregates per-file commits, lines added/deleted, and distinct author names.
- Assigns a transparent risk score (0–100) and low/medium/high category.
- Shows results in a browser dashboard, JSON API, or terminal.
- Restricts API access to repositories under a configured root directory.

## Tech stack

Python 3.10+, Git, FastAPI, Pydantic, vanilla HTML/CSS/JavaScript, pytest, Docker, GitHub Actions.

## Screens and endpoints

- Dashboard: `http://127.0.0.1:8000/`
- Interactive API docs: `http://127.0.0.1:8000/docs`
- Health: `GET /health`
- Analyze: `POST /analyze` with `{"path":".","limit":100}`

## Quick start (Windows / macOS / Linux)

Install **Python 3.10+** and **Git**, then from the extracted project folder:

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -e '.[dev]'
pytest -q
```

Analyze a repository with the CLI:

```bash
codepulse . --limit 100
codepulse . --json
```

Run the web app (default root is your current working directory):

```bash
uvicorn codepulse.api:app --reload
```

Open `http://127.0.0.1:8000/` and enter `.` for the current Git repository. To analyze another repo, set `CODEPULSE_ROOT` to a parent folder containing the repo and enter its relative folder name. Example on macOS/Linux:

```bash
export CODEPULSE_ROOT="$HOME/projects"
uvicorn codepulse.api:app --reload
# Dashboard repository path: my-other-repo
```

PowerShell equivalent:

```powershell
$env:CODEPULSE_ROOT = "$HOME\projects"
uvicorn codepulse.api:app --reload
```

## Docker

```bash
docker build -t codepulse-ai .
docker run --rm -p 8000:8000 -v "$(pwd):/repos:ro" codepulse-ai
```

On Windows PowerShell, use `${PWD}:/repos:ro` for the volume argument. The bind-mounted folder must be a Git repository, or contain one; the dashboard's `.` refers to `/repos`. This container is intended for **local development**, not deployment to an untrusted public network.

## Scoring method

The score is intentionally simple and auditable:

```text
score = min(commits × 5, 30)
      + min((lines_added + lines_deleted) // 20, 40)
      + min(max(distinct_authors - 1, 0) × 8, 24)
```

Risk bands: **low** 0–29, **medium** 30–64, **high** 65–100. The theoretical maximum with these weights is 94. Binary-file changes are skipped, and renamed files are treated separately (`--no-renames`). Metrics depend on the selected commit window; this is not a quality judgment about individual developers.

## Example API request

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"path":".","limit":100}'
```

Response includes `repository`, `commits_analyzed`, `files_analyzed`, a ranked `files` array, and a disclaimer.

## Project structure

```text
codepulse-ai/
├── src/codepulse/
│   ├── analyzer.py      # Git history parser + transparent scoring
│   ├── api.py           # FastAPI endpoints and path validation
│   └── cli.py           # Terminal interface
├── web/index.html       # Browser dashboard
├── tests/               # Unit and integration tests
├── .github/workflows/   # GitHub Actions CI
├── Dockerfile
├── pyproject.toml
├── LICENSE
└── README.md
```

## Limitations and responsible use

- A change-risk heuristic **cannot establish the presence of a defect**.
- Git author names may differ for the same contributor, and commit history may be incomplete or rewritten.
- Merge commits, binary files, renames, and unusual filenames have limited handling.
- The API is for trusted local use; it has no authentication, rate limiting, or production hardening.
- Do not use scores to rank employees or make personnel decisions.

## Roadmap

1. Add labeled defect datasets and evaluate supervised models against this heuristic baseline.
2. Add repository-level time-window trends and richer charts.
3. Integrate GitHub pull-request metadata with explicit user authorization.
4. Add model explanations, calibration, and out-of-sample validation before claiming predictive accuracy.

## Author

**Piyush Rane** — [GitHub](https://github.com/ranepiyush123)

## License

MIT — see [LICENSE](LICENSE).
