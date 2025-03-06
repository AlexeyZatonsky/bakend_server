import asyncio
from aiobotocore.session import get_session
from contextlib import asynccontextmanager
from .settings.config import settings



s3_access_key = settings.S3_ACCESS_KEY
s3_secret_key = settings.S3_SECRET_KEY
s3_url = settings.S3_URL
s3_bucket_name = settings.S3_BUCKET_NAME


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        bucket_name: str
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "region_name": "ru-msk-1"
        }
        
        self.bucket_name = bucket_name
        self.session = get_session()


    @asynccontextmanager    
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client


    async def upload_file(
            self,
            file_path: str,
            object_name: str   #позже будем принимать файл с фронтенда 
            ):
        async with self.get_client() as client:
            with open(file_path, "rb") as file:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=file,
                )


async def main():
    s3_client = S3Client (
        access_key= s3_access_key,
        secret_key= s3_secret_key,
        endpoint_url= s3_url,
        bucket_name=s3_bucket_name   
    )
    
    await s3_client.upload_file("Цветы.jpg")        

if __name__ == "__main__":
    asyncio.run(main())