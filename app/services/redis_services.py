"""
Redis aggregation helpers.

- user-level counters (order_count, total_spend)
- global counters (total_orders, total_revenue)
- top-N spenders (sorted set)
- monthly buckets (YYYY-MM)
All operations are **idempotent** (INCR).
"""
from loguru import logger
from redis import Redis

r = Redis(host="redis", port=6379, decode_responses=True)

def update_user_stats(user_id: str, order_value: float, month: str) -> None:
    """Update all Redis aggregates atomically."""
    pipe = r.pipeline()
    pipe.hincrby(f"user:{user_id}", "order_count", 1)
    pipe.hincrbyfloat(f"user:{user_id}", "total_spend", order_value)

    pipe.hincrby("global:stats", "total_orders", 1)
    pipe.hincrbyfloat("global:stats", "total_revenue", order_value)

    # top-N leaderboard
    pipe.zincrby("top:spend", order_value, user_id)

    # monthly bucket
    pipe.hincrby(f"month:{month}", "orders", 1)
    pipe.hincrbyfloat(f"month:{month}", "revenue", order_value)

    pipe.execute()
    logger.info("redis_updated", user_id=user_id, month=month, order_value=order_value)

def top_spenders(n: int = 10):
    """Return list[ (user_id, total_spend) ] top n spenders."""
    return r.zrevrange("top:spend", 0, n - 1, withscores=True)

def monthly_range(start: str, end: str):
    """Return dict {month: {orders, revenue}} between YYYY-MM strings."""
    months = [f"{y:04d}-{m:02d}" for y in range(int(start[:4]), int(end[:4]) + 1)
              for m in range(1, 13)]
    months = [m for m in months if start <= m <= end]
    return {m: r.hgetall(f"month:{m}") for m in months if r.exists(f"month:{m}")}