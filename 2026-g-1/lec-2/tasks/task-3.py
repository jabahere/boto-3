
import argparse
import boto3
from botocore.exceptions import ClientError
import logging
from os import getenv
from dotenv import load_dotenv

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

def delete_bucket(s3_client, bucket_name):
    try:
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' has been deleted.")
        return True
    except ClientError as e:
        logging.error(e)
        return False

def main():
    parser = argparse.ArgumentParser(description="Delete an S3 bucket if it exists.")
    parser.add_argument("bucket_name", help="The name of the S3 bucket.")
    args = parser.parse_args()

    s3_client = init_client()
    if not s3_client:
        print("Could not initialize S3 client. Please check your credentials.")
        return

    try:
        s3_client.head_bucket(Bucket=args.bucket_name)
        print(f"Bucket '{args.bucket_name}' exists. Deleting it now...")
        delete_bucket(s3_client, args.bucket_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket' or e.response['Error']['Code'] == '404':
            print(f"Bucket '{args.bucket_name}' does not exist.")
        else:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
