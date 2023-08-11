from django.conf import settings
import boto3
from base import django_env

django_env()
import logging

logger = logging.getLogger("phurti")
from django.utils import timezone

today = str(timezone.now())
import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath("__file__"))


def upload():
    AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
    try:
        s3 = boto3.resource("s3")
        s3.Bucket(AWS_STORAGE_BUCKET_NAME).upload_file(
            f"{BASE_DIR}/request_response.log", f"logs/request_response-{today}.log"
        )
        print("SUCCESSFULLY UPLOADED!")
        print("REMOVING PREVIOUS FILE")
        os.remove(f"{BASE_DIR}/request_response.log")
    except Exception as e:
        logger.error(str(e))
        print("UPLOAD FAILED")


if __name__ == "__main__":
    upload()
