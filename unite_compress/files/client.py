from functools import lru_cache
from typing import Any

import boto3
from attrs import define
from botocore.client import Config

from unite_compress.files.utils import assert_settings


@define
class S3Credentials:
    access_key_id: str
    secret_access_key: str
    region_name: str
    bucket_name: str
    # default_acl: str
    presigned_expiry: int
    max_size: int
    endpoint_url: str


@lru_cache
def s3_get_credentials() -> S3Credentials:
    required_config = assert_settings(
        [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_S3_REGION_NAME",
            "AWS_STORAGE_BUCKET_NAME",
            # "AWS_DEFAULT_ACL",
            "_AWS_EXPIRY",
            "FILE_MAX_SIZE",
            "AWS_S3_ENDPOINT_URL",
        ],
        "S3 credentials not found.",
    )

    return S3Credentials(
        access_key_id=required_config["AWS_ACCESS_KEY_ID"],
        secret_access_key=required_config["AWS_SECRET_ACCESS_KEY"],
        region_name=required_config["AWS_S3_REGION_NAME"],
        bucket_name=required_config["AWS_STORAGE_BUCKET_NAME"],
        # default_acl=required_config["AWS_DEFAULT_ACL"],
        presigned_expiry=required_config["_AWS_EXPIRY"],
        max_size=required_config["FILE_MAX_SIZE"],
        endpoint_url=required_config["AWS_S3_ENDPOINT_URL"],
    )


def s3_get_client():
    credentials = s3_get_credentials()

    return boto3.client(
        service_name="s3",
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.secret_access_key,
        region_name=credentials.region_name,
        endpoint_url=credentials.endpoint_url,
        config=Config(s3={"addressing_style": "virtual"}),
    )


def s3_generate_presigned_post(*, file_path: str, file_type: str) -> dict[str, Any]:
    credentials = s3_get_credentials()
    s3_client = s3_get_client()

    # acl = credentials.default_acl
    # acl = "private"
    expires_in = credentials.presigned_expiry

    """
    TODO: Create a type for the presigned_data
    It looks like this:
    {
        'fields': {
            'Content-Type': 'image/png',
            'acl': 'private',
            'key': 'files/bafdccb665a447468e237781154883b5.png',
            'policy': 'some-long-base64-string',
            'x-amz-algorithm': 'AWS4-HMAC-SHA256',
            'x-amz-credential': 'AKIASOZLZI5FJDJ6XTSZ/20220405/eu-central-1/s3/aws4_request',
            'x-amz-date': '20220405T114912Z',
            'x-amz-signature': '7d8be89aabec12b781d44b5b3f099d07be319b9a41d9a9c804bd1075e1ef5735'
        },
        'url': 'https://django-styleguide-example.s3.amazonaws.com/'
    }
    """
    presigned_data = s3_client.generate_presigned_post(
        Bucket=credentials.bucket_name,
        Key=file_path,
        ExpiresIn=expires_in,
    )

    return presigned_data


def s3_generate_presigned_get(*, file_path: str) -> str:
    credentials = s3_get_credentials()
    s3_client = s3_get_client()

    expires_in = credentials.presigned_expiry

    presigned_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": credentials.bucket_name, "Key": file_path},
        ExpiresIn=expires_in,
    )
    return presigned_url
