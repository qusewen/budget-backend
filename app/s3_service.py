import os
import uuid
from fastapi import HTTPException, UploadFile
from typing import BinaryIO
from io import BytesIO
import httpx


class S3Service:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")  # Project URL
        self.supabase_key = os.getenv("SUPABASE_KEY")  # anon public key
        self.bucket_name = os.getenv("SUPABASE_BUCKET", "images")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.storage_url = f"{self.supabase_url}/storage/v1"
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
        }

    def upload_file(self, file: UploadFile, object_name: str = None) -> str:
        try:
            if object_name is None:
                ext = file.filename.split(".")[-1] if "." in file.filename else "png"
                object_name = f"{uuid.uuid4()}.{ext}"

            file_bytes = file.file.read()

            response = httpx.post(
                f"{self.storage_url}/object/{self.bucket_name}/{object_name}",
                headers={
                    **self.headers,
                    "Content-Type": file.content_type or "application/octet-stream",
                },
                content=file_bytes,
            )

            if response.status_code not in (200, 201):
                raise HTTPException(
                    status_code=500,
                    detail=f"Supabase upload error: {response.text}"
                )

            # Возвращаем публичную ссылку на файл
            public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{object_name}"
            return public_url

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

    def download_file(self, object_name: str) -> BinaryIO:
        try:
            response = httpx.get(
                f"{self.storage_url}/object/{self.bucket_name}/{object_name}",
                headers=self.headers,
            )

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="File not found")

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Download error: {response.text}")

            return BytesIO(response.content)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

    def delete_file(self, object_name: str):
        try:
            response = httpx.delete(
                f"{self.storage_url}/object/{self.bucket_name}/{object_name}",
                headers=self.headers,
            )

            if response.status_code not in (200, 204):
                raise HTTPException(
                    status_code=500,
                    detail=f"Delete error: {response.text}"
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")

    def list_files(self, prefix: str = "") -> list:
        try:
            response = httpx.post(
                f"{self.storage_url}/object/list/{self.bucket_name}",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"prefix": prefix, "limit": 100, "offset": 0},
            )

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"List error: {response.text}")

            files = []
            for obj in response.json():
                files.append({
                    "name": obj.get("name"),
                    "size": obj.get("metadata", {}).get("size"),
                    "last_modified": obj.get("updated_at"),
                })
            return files

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"List error: {str(e)}")