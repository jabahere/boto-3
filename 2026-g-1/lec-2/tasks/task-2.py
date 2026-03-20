
import argparse
import boto3
from botocore.exceptions import ClientError
import json
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

def get_bucket_policy(s3_client, bucket_name):
    try:
        policy = s3_client.get_bucket_policy(Bucket=bucket_name)
        return json.loads(policy['Policy'])
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            return None
        else:
            logging.error(e)
            return None

def generate_public_read_policy(bucket_name):
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadForDevAndTest",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}/dev/*",
                    f"arn:aws:s3:::{bucket_name}/test/*"
                ]
            }
        ]
    }
    return json.dumps(policy)

def create_bucket_policy(s3_client, bucket_name):
    try:
        policy = generate_public_read_policy(bucket_name)
        s3_client.delete_public_access_block(Bucket=bucket_name)
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=policy)
        print(f"Successfully created a public read policy for /dev/* and /test/* in bucket '{bucket_name}'.")
        return True
    except ClientError as e:
        logging.error(e)
        return False

def main():
    parser = argparse.ArgumentParser(description="Manage S3 bucket policies.")
    parser.add_argument("bucket_name", help="The name of the S3 bucket.")
    args = parser.parse_args()

    s3_client = init_client()
    if not s3_client:
        print("Could not initialize S3 client. Please check your credentials.")
        return

    try:
        s3_client.head_bucket(Bucket=args.bucket_name)
    except ClientError as e:
        print(f"Bucket '{args.bucket_name}' not found or you don't have access.")
        return

    print(f"Checking policy for bucket: {args.bucket_name}")
    policy = get_bucket_policy(s3_client, args.bucket_name)

    if policy:
        print("Bucket already has a policy:")
        print(json.dumps(policy, indent=4))
    else:
        print(f"No policy found for bucket '{args.bucket_name}'. Creating a new policy.")
        create_bucket_policy(s3_client, args.bucket_name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
