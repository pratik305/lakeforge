import boto3
import os 



def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name = os.environ.get("AWS_REGION","us-east-1"),
        endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
    )

def ensure_bucket(client,bucket_name):
    existing_buckets = [bucket['Name'] for bucket in client.list_buckets()['Buckets']]
    if bucket_name not in existing_buckets:
        client.create_bucket(Bucket=bucket_name)

 

