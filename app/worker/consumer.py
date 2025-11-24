"""
SQS long-polling consumer.
- structured JSON logs to stdout
- idempotent Redis upserts
"""
import json
import time
import sys
import redis
from loguru import logger
from services.sqs_services import receive_messages, delete_message
from services.processing import process_order

# ---------- Logging ----------
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)

# ---------- Redis ----------
r = redis.Redis(host="redis", port=6379, decode_responses=True)
IDEMPOTENCY_PREFIX = "order_processed:"

def is_duplicate(order_id: str) -> bool:
    key = IDEMPOTENCY_PREFIX + order_id
    return r.exists(key)

def mark_processed(order_id: str):
    key = IDEMPOTENCY_PREFIX + order_id
    r.setex(key, 86400, "1")   # keep for 24h


print("Worker starting…", flush=True)
logger.info("Worker started")

while True:
    messages = receive_messages()

    for msg in messages:
        raw = msg["Body"]

        # SQS sometimes returns JSON as a quoted string — unwrap once
        if raw.startswith('"') and raw.endswith('"'):
            raw = json.loads(raw)

        body = json.loads(raw)
        order_id = body["order_id"]

        logger.info(
            f"message received with order id - {order_id}",
            message_id=msg["MessageId"],
            body=body
        )

        # ---------- Idempotency Check ----------
        if is_duplicate(order_id):
            logger.warning(
                f"duplicate order detected - skipping | order_id={order_id}",
                message_id=msg["MessageId"]
            )

            # Still delete from queue so it doesn't get retried
            delete_message(msg["ReceiptHandle"])
            logger.info(
                f"duplicate message deleted | order_id={order_id}",
                message_id=msg["MessageId"]
            )
            continue

        # ---------- Normal Processing ----------
        if process_order(body):
            mark_processed(order_id)
            delete_message(msg["ReceiptHandle"])
            logger.info(
                f"message deleted with order id - {order_id}",
                message_id=msg["MessageId"]
            )

    time.sleep(1)
