from pydantic import BaseModel
from typing import List


class S3Bucket(BaseModel):
    name: str


class S3Object(BaseModel):
    key: str


class S3Entity(BaseModel):
    bucket: S3Bucket
    object: S3Object


class Record(BaseModel):
    s3: S3Entity


class MinioWebhookPayloadSchema(BaseModel):
    Records: List[Record]
