# sqs_services.py
import boto3
import os

def get_sqs_client():
    return boto3.client(
        "sqs",
        endpoint_url="http://localstack:4566",   # container name
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
    )

sqs = get_sqs_client()
try:
    sqs.create_queue(QueueName="orders")
except sqs.exceptions.QueueNameExists:
    pass
QUEUE_URL = sqs.get_queue_url(QueueName="orders")["QueueUrl"]

def receive_messages():
    resp = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=2,
    )
    return resp.get("Messages", [])

def delete_message(receipt_handle: str):
    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)