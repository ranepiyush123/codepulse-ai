"""Git-based change analytics; never executes code from analyzed repositories."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
from collections import defaultdict

class AnalysisError(ValueError):
    pass

@dataclass
class FileMetrics:
    path: str
    commits: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    authors: int = 0
    risk_score: int = 0
    risk_level: str = "low"
    explanations: list[str] | None = None

def _git(repo: Path, *args: str) -> str:
    try:
        proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=20,
                              check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AnalysisError(f"Unable to run git: {exc}") from exc
    if proc.returncode:
        raise AnalysisError(proc.stderr.strip() or "Git command failed")
    return proc.stdout

def score_file(commits: int, added: int, deleted: int, authors: int) -> tuple[int, str, list[str]]:
    """Transparent heuristic; NOT a calibrated probability of defects."""
    churn = added + deleted
    score = min(commits * 5, 30) + min(churn // 20, 40) + min(max(authors - 1, 0) * 8, 24)
    score = min(score, 100)
    reasons = []
    if commits >= 4:
        reasons.append("Frequently modified file")
    if churn >= 200:
        reasons.append("High line churn")
    if authors >= 3:
        reasons.append("Multiple contributors")
    if not reasons:
        reasons.append("Limited recent change activity")
    level = "high" if score >= 65 else "medium" if score >= 30 else "low"
    return score, level, reasons

def analyze_repository(path: str | Path, limit: int = 100) -> dict:
    repo = Path(path).expanduser().resolve()
    if not repo.is_dir():
        raise AnalysisError("Repository path is not a directory")
    if not 1 <= limit <= 1000:
        raise AnalysisError("limit must be between 1 and 1000")
    _git(repo, "rev-parse", "--show-toplevel")
    # Record separators avoid ambiguity between commits. Paths may contain tabs/newlines;
    # this MVP supports ordinary UTF-8 paths without embedded newlines.
    try:
        raw = _git(repo, "log", f"-n{limit}", "--format=COMMIT:%H%x09%an", "--numstat", "--no-renames")
    except AnalysisError as exc:
        # A newly initialized repository has no HEAD yet.
        if "does not have any commits yet" in str(exc) or "your current branch" in str(exc).lower():
            raw = ""
        else:
            raise
    stats: dict[str, dict] = defaultdict(lambda: {"commits": 0, "added": 0, "deleted": 0, "authors": set()})
    commit_count = 0
    author = None
    touched: set[str] = set()
    for line in raw.splitlines():
        if line.startswith("COMMIT:"):
            commit_count += 1
            author = line.split("	", 1)[1] if "	" in line else "unknown"
            touched = set()
            continue
        fields = line.split("	", 2)
        if len(fields) != 3 or not fields[0].isdigit() or not fields[1].isdigit():
            continue  # Ignore binary file stats and non-numstat lines.
        added, deleted, filename = fields
        entry = stats[filename]
        entry["added"] += int(added)
        entry["deleted"] += int(deleted)
        entry["authors"].add(author)
        if filename not in touched:
            entry["commits"] += 1
            touched.add(filename)
    files = []
    for name, item in stats.items():
        n_authors = len(item["authors"])
        score, level, reasons = score_file(item["commits"], item["added"], item["deleted"], n_authors)
        files.append(asdict(FileMetrics(name, item["commits"], item["added"], item["deleted"], n_authors, score, level, reasons)))
    files.sort(key=lambda f: (-f["risk_score"], f["path"]))
    return {"repository": str(repo), "commits_analyzed": commit_count,
            "files_analyzed": len(files), "files": files,
            "disclaimer": "Scores are heuristic change-risk indicators, not probabilities or verified bug predictions."}
