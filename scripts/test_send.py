"""
Host-side helper to push one valid order into LocalStack SQS.
Uses the same hostname that the worker proved works.
"""
import boto3, json

sqs = boto3.client(
    "sqs",
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

order = {
    "order_id": "205",
    "user_id": "U1034",
    "order_timestamp": "2024-01-01T10:00:00Z",
    "order_value": 10.0,
    "items": [
        {"product_id": "X", "quantity": 2, "price_per_unit": 250.0},
    ],
}

url = "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/orders"
resp = sqs.send_message(QueueUrl=url, MessageBody=json.dumps(order))
print("Sent OK  :", resp["ResponseMetadata"]["HTTPStatusCode"])
print("MessageId:", resp["MessageId"])