"""
SQS long-polling consumer.
- structured JSON logs to stdout
- idempotent Redis upserts
"""
import json, time, signal, sys
from loguru import logger
from services.sqs_services import receive_messages, delete_message
from services.processing import process_order

logger.remove()
logger.add(sys.stdout,
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
           level="INFO")  # JSON logs

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
        logger.info(f"message received with order id - {body['order_id']}", message_id=msg["MessageId"], body=body)
        if process_order(body):
            delete_message(msg["ReceiptHandle"])
            logger.info(f"message deleted with order id - {body['order_id']}", message_id=msg["MessageId"])
    time.sleep(1)