import boto3
sqs = boto3.client(
    "sqs",
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)
url = sqs.get_queue_url(QueueName="orders")["QueueUrl"]
resp = sqs.receive_message(QueueUrl=url, MaxNumberOfMessages=1)
print('Queue URL :', url)
print('Messages  :', len(resp.get('Messages', [])))