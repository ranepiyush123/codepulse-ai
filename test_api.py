import subprocess
from fastapi.testclient import TestClient
from codepulse.api import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_path_traversal_blocked(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEPULSE_ROOT", str(tmp_path))
    response = client.post("/analyze", json={"path": "../"})
    assert response.status_code == 403

def test_analyze_endpoint(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEPULSE_ROOT", str(tmp_path))
    subprocess.run(["git", "-C", str(tmp_path), "init"], check=True, capture_output=True)
    response = client.post("/analyze", json={"path": ".", "limit": 10})
    assert response.status_code == 200
    assert response.json()["files"] == []

def test_bad_limit():
    assert client.post("/analyze", json={"path": ".", "limit": 1001}).status_code == 422
