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
        return client
    except ClientError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    s3_client = init_client()