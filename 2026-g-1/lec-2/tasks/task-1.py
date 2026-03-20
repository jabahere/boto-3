
import argparse
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
        client.list_buckets()
        logging.info("Successfully connected to S3")
        return client
    except ClientError as e:
        logging.error(e)
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None

def create_bucket(aws_s3_client, bucket_name, region='us-west-2'):
    try:
        location = {'LocationConstraint': region}
        aws_s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration=location
        )
        return True
    except ClientError as e:
        logging.error(e)
        return False

def bucket_exists(aws_s3_client, bucket_name):
    try:
        aws_s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            logging.error(e)
            return False

def main():
    parser = argparse.ArgumentParser(description="Check and create an S3 bucket if it does not exist.")
    parser.add_argument("bucket_name", help="The name of the bucket to check and/or create.")
    args = parser.parse_args()
    
    s3_client = init_client()

    if s3_client is None:
        print("Could not initialize S3 client. Please check your credentials.")
        return

    if bucket_exists(s3_client, args.bucket_name):
        print(f"Bucket '{args.bucket_name}' already exists.")
    else:
        print(f"Bucket '{args.bucket_name}' does not exist. Creating it.")
        if create_bucket(s3_client, args.bucket_name):
            print(f"Bucket '{args.bucket_name}' created successfully.")
        else:
            print(f"Failed to create bucket '{args.bucket_name}'.")

if __name__ == "__main__":
    main()
