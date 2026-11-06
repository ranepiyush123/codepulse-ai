"""HTTP API for local repository analytics."""
from pathlib import Path
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .analyzer import analyze_repository, AnalysisError

app = FastAPI(title="CodePulse AI", version="0.1.0", description="Explainable Git change-risk analytics")
WEB = Path(__file__).resolve().parents[2] / "web" / "index.html"

class AnalyzeRequest(BaseModel):
    # Only paths inside CODEPULSE_ROOT may be analyzed, to avoid arbitrary filesystem reads.
    path: str = Field(min_length=1, max_length=4096)
    limit: int = Field(default=100, ge=1, le=1000)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def dashboard():
    if WEB.exists():
        return FileResponse(WEB)
    return {"message": "Dashboard not found; use /docs for API documentation"}

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    root = Path(os.environ.get("CODEPULSE_ROOT", os.getcwd())).expanduser().resolve()
    requested = Path(request.path).expanduser()
    target = (root / requested).resolve() if not requested.is_absolute() else requested.resolve()
    if not target.is_relative_to(root):
        raise HTTPException(status_code=403, detail="Repository must be inside CODEPULSE_ROOT")
    try:
        return analyze_repository(target, request.limit)
    except AnalysisError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
