FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY src ./src
COPY web ./web
RUN pip install --no-cache-dir .
ENV CODEPULSE_ROOT=/repos
EXPOSE 8000
CMD ["uvicorn", "codepulse.api:app", "--host", "0.0.0.0", "--port", "8000"]
