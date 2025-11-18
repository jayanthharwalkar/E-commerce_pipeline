"""
Bulk order generator.
CLI:  python send_bulk.py 1000   # 1000 customers → ~1000 orders
"""
import argparse, boto3, json, random, string, sys, time

sqs = boto3.client(
    "sqs",
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

QUEUE_URL = "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/orders"

# ---------- helpers ----------
def random_order_id():
    return "ORD" + "".join(random.choices(string.digits, k=6))

def random_user_id():
    return "U" + "".join(random.choices(string.digits, k=4))

def random_timestamp():
    return f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}T10:00:00Z"

def random_items():
    n = random.randint(1, 3)
    items = []
    for _ in range(n):
        qty = random.randint(1, 5)
        price = round(random.uniform(5, 100), 2)
        items.append({"product_id": f"P{random.randint(1,99):03d}", "quantity": qty, "price_per_unit": price})
    return items

def calculate_total(items):
    return round(sum(i["quantity"] * i["price_per_unit"] for i in items), 2)

# ---------- main ----------
def main():
    parser = argparse.ArgumentParser(description="Bulk order generator")
    parser.add_argument("customers", type=int, help="Number of unique customers")
    args = parser.parse_args()

    print(f"Generating {args.customers} orders...")
    for i in range(1, args.customers + 1):
        user_id = f"U{i:04d}"
        order = {
            "order_id": random_order_id(),
            "user_id": user_id,
            "order_timestamp": random_timestamp(),
            "order_value": 0,  # calculated below
            "items": random_items(),
        }
        order["order_value"] = calculate_total(order["items"])

        resp = sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(order))
        print(f"Sent order {order['order_id']} for user {user_id} (MessageId: {resp['MessageId']})")

        # tiny throttle to avoid flooding
        time.sleep(0.01)

    print(f"Finished generating {args.customers} orders.")

if __name__ == "__main__":
    main()