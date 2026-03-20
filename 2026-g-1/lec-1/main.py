import boto3
from os import getenv
from dotenv import load_dotenv
import logging
from botocore.exceptions import ClientError

load_dotenv()

def init_client():
    try:
        client = boto3.client(
            "s3",
            aws_access_key_id=getenv("aws_access_key_id"),
            aws_secret_access_key=getenv("aws_secret_access_key"),
            aws_session_token=getenv("aws_session_token"),
            region_name=getenv("aws_region_name"),
        )
        # check if credentials are correct
        client.list_buckets()
        logging.info("Successfully connected to S3")
        return client
    except ClientError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

def create_bucket (aws_s3_client, bucket_name, region='us-west-2'):
    # Create bucket
    try:
        location = {'LocationConstraint': region}
        aws_s3_client. create_bucket (
            Bucket=bucket_name,
            CreateBucketConfiguration=location
        )
    except ClientError as e:
        logging.error(e)
        return False
    return True

def delete_bucket (aws_s3_client, bucket_name) :
    # Delete bucket
    try:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/delete_bucket.html
        aws_s3_client. delete_bucket (Bucket=bucket_name)
    except ClientError as e:
        Logging-error(e)
        return false
    return True

def main():
    s3_client = init_client()

    if s3_client:
        print("S3 client is initialized.")
    else:
        print("Failed to initialize S3 client.")

    create_bucket(s3_client, '2026-btu-jaba-new')

    buckets = s3_client.list_buckets()

    if buckets:
        for bucket in buckets['Buckets']:
            print(bucket['Name'])

if __name__ == "__main__":
    main()