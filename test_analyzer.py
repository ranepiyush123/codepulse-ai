import subprocess
import pytest
from codepulse.analyzer import analyze_repository, score_file, AnalysisError

def git(path, *args):
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True)

def test_score_is_bounded_and_explained():
    score, level, reasons = score_file(999, 100000, 100000, 20)
    assert score == 94
    assert level == "high"
    assert "High line churn" in reasons

def test_analyze_real_temporary_git_repo(tmp_path):
    git(tmp_path, "init")
    git(tmp_path, "config", "user.name", "Test User")
    git(tmp_path, "config", "user.email", "test@example.com")
    (tmp_path / "app.py").write_text("print('hello')\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "initial")
    result = analyze_repository(tmp_path)
    assert result["commits_analyzed"] == 1
    assert result["files_analyzed"] == 1
    assert result["files"][0]["path"] == "app.py"
    assert result["files"][0]["lines_added"] == 1

def test_non_repo_rejected(tmp_path):
    with pytest.raises(AnalysisError):
        analyze_repository(tmp_path)

def test_invalid_limit_rejected(tmp_path):
    with pytest.raises(AnalysisError):
        analyze_repository(tmp_path, 1001)
