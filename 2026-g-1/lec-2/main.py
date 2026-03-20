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

def bucket_exists(aws_s3_client, bucket_name):
    try:
        response = aws_s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        print(e)
        return False
    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code == 200:
        return True
    return False


def download_file_and_upload_to_s3(aws_s3_client,
                                   bucket_name,
                                   url,
                                   file_name,
                                   keep_local=False):
    from urllib.request import urlopen
    import io
    with urlopen(url) as response:
        content = response.read()
        try:
            aws_s3_client.upload_fileobj(
                Fileobj=io.BytesIO(content),
                Bucket=bucket_name,
                ExtraArgs={'ContentType': 'image/jpg'},
                Key=file_name)
        except Exception as e:
            print(e)

    if keep_local:
        with open(file_name, mode='wb') as file:
            file.write(content)

    return f"https://s3-us-west-2.amazonaws.com/{bucket_name}/{file_name}"


def set_object_access_policy(aws_s3_client, bucket_name, file_name):
    try:
        response = aws_s3_client.put_object_acl(ACL="public-read",
                                                Bucket=bucket_name,
                                                Key=file_name)
    except ClientError as e:
        print(e)
        return False
    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code == 200:
        return True
    return False


def generate_public_read_policy(bucket_name):
    policy = {
        "Version":
        "2012-10-17",
        "Statement": [{
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*",
        }],
    }

    return json.dumps(policy)


def create_bucket_policy(aws_s3_client, bucket_name):
    aws_s3_client.delete_public_access_block(Bucket=bucket_name)
    aws_s3_client.put_bucket_policy(
        Bucket=bucket_name, Policy=generate_public_read_policy(bucket_name))
    print("Bucket policy created successfully")


def read_bucket_policy(aws_s3_client, bucket_name):
    try:
        policy = aws_s3_client.get_bucket_policy(Bucket=bucket_name)
        policy_str = policy["Policy"]
        print(policy_str)
    except ClientError as e:
        print(e)
        return False

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