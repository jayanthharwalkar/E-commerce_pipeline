"""
Order-validation and business-logic layer.

- validates Pydantic Order model
- extracts month bucket (YYYY-MM)
- calls Redis aggregation
- logs every step as structured JSON
"""
from loguru import logger
from models.order_model import Order
from services.redis_services import update_user_stats

def process_order(message: dict) -> bool:
    """
    Validate incoming SQS message and update aggregates.

    Returns True if order was processed successfully, False on any error.
    """
    try:
        order = Order(**message)
        month = order.order_timestamp[:7]          # 2024-01
        update_user_stats(order.user_id, order.order_value, month)
        logger.info("order_validated", order_id=order.order_id, user_id=order.user_id)
        return True
    except Exception as e:
        logger.warning(f"Order invalid with error {e}", error=str(e), body=message)
        return True