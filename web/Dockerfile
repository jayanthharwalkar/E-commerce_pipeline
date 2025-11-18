FROM python:3.10-slim

# curl for health-check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy from repo-root (relative to build context)
COPY web/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY web /app                

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]