"""
FastAPI service exposing order statistics.

Endpoints:
  GET /users/{user_id}/stats   - user counters
  GET /stats/global            - global counters
  GET /stats/top/{n}           - top-N spenders
  GET /stats/monthly           - monthly buckets (date range)
  GET /health                  - liveness probe
  GET /metrics                 - Prometheus metrics
"""
from fastapi import FastAPI, HTTPException, Query
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from redis import Redis
from loguru import logger
import time

r = Redis(host="redis", port=6379, decode_responses=True)
app = FastAPI(title="Qyrus Order Stats API", version="1.0.0")

# Prometheus metrics
REQ_COUNT = Counter('api_requests_total', 'Total API requests', ['endpoint'])
LATENCY   = Histogram('api_request_duration_seconds', 'Request latency')

@app.get("/health", tags=["probe"])
def health():
    """Liveness probe for Docker."""
    REQ_COUNT.labels("/health").inc()
    return {"status": "ok"}

@app.get("/metrics", tags=["monitoring"])
def metrics():
    """Prometheus metrics endpoint."""
    REQ_COUNT.labels("/metrics").inc()
    return generate_latest(REGISTRY)

@app.get("/users/{user_id}/stats", tags=["users"])
def user_stats(user_id: str):
    """Return order count and total spend for a user."""
    with LATENCY.time():
        REQ_COUNT.labels("/users/{user_id}/stats").inc()
        data = r.hgetall(f"user:{user_id}")
        if not data:
            raise HTTPException(status_code=404, detail="user not found")
        return {
            "user_id": user_id,
            "order_count": int(data["order_count"]),
            "total_spend": float(data["total_spend"]),
        }

@app.get("/stats/global", tags=["global"])
def global_stats():
    """Return total order count and revenue across all users."""
    with LATENCY.time():
        REQ_COUNT.labels("/stats/global").inc()
        data = r.hgetall("global:stats")
        return {
            "total_orders": int(data["total_orders"]),
            "total_revenue": float(data["total_revenue"]),
       }

@app.get("/stats/top/{n}", tags=["analytics"])
def top_spenders(n: int):
    """Return top-N users by total spend."""
    with LATENCY.time():
        REQ_COUNT.labels("/stats/top/{n}").inc()
        top = r.zrevrange("top:spend", 0, n - 1, withscores=True)
        return [{"user_id": uid, "total_spend": float(score)} for uid, score in top]

@app.get("/stats/monthly", tags=["analytics"])
def monthly_stats(
    start: str = Query("2024-01", regex=r"^\d{4}-\d{2}$"),
    end: str = Query("2024-12", regex=r"^\d{4}-\d{2}$"),
):
    """Return monthly order counts and revenue between YYYY-MM strings."""
    with LATENCY.time():
        REQ_COUNT.labels("/stats/monthly").inc()
        months = [f"{y:04d}-{m:02d}" for y in range(int(start[:4]), int(end[:4]) + 1)
                  for m in range(1, 13)]
        months = [m for m in months if start <= m <= end]
        return {m: r.hgetall(f"month:{m}") for m in months if r.exists(f"month:{m}")}