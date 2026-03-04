import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile
import os
from typing import BinaryIO


class S3Service:
    def __init__(self):
        # Получаем настройки из переменных окружения
        self.endpoint_url = os.getenv("S3_ENDPOINT", "http://localhost:9000")
        self.access_key = os.getenv("S3_ACCESS_KEY")
        self.secret_key = os.getenv("S3_SECRET_KEY")
        self.bucket_name = os.getenv("S3_IMAGES_BUCKET", "my-bucket")

        # Создаем клиент S3
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            use_ssl=False if "http://" in self.endpoint_url else True,
        )

    def upload_file(self, file: UploadFile, object_name: str = None) -> str:
        try:
            if object_name is None:
                object_name = file.filename

            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                object_name,
                ExtraArgs={"ContentType": file.content_type}
            )
            return f"{self.endpoint_url}/{self.bucket_name}/{object_name}"
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"S3 upload error: {str(e)}")

    def download_file(self, object_name: str) -> BinaryIO:
        try:
            from io import BytesIO
            file_stream = BytesIO()

            self.s3_client.download_fileobj(
                self.bucket_name,
                object_name,
                file_stream
            )
            file_stream.seek(0)
            return file_stream
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise HTTPException(status_code=404, detail="File not found")
            raise HTTPException(status_code=500, detail=f"S3 download error: {str(e)}")

    def delete_file(self, object_name: str):
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"S3 delete error: {str(e)}")

    def list_files(self, prefix: str = "") -> list:
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'name': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            return files
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"S3 list error: {str(e)}")