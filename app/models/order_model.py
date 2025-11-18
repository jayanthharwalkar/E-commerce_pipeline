from pydantic import BaseModel, model_validator
from typing import List
from loguru import logger
class Item(BaseModel):
    product_id: str
    quantity: int
    price_per_unit: float

class Order(BaseModel):
    order_id: str
    user_id: str
    order_timestamp: str
    order_value: float
    items: List[Item]

    @model_validator(mode="after")
    def fix_order_value(self):
        computed_total = sum(i.quantity * i.price_per_unit for i in self.items)
        
        # If mismatch → log it but DON'T reject
        if abs(computed_total - self.order_value) > 0.01:
            logger.warning(
                f"Order value mismatch for order_num - {self.order_id}",
                order_id=self.order_id,
                claimed=self.order_value,
                computed=computed_total
            )
            # Override the order_value with correct computed truth
            self.order_value = computed_total

        return self