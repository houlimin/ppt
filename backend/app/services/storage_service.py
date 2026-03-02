import os
import uuid
from typing import Optional, BinaryIO
from datetime import datetime

try:
    import oss2
    HAS_OSS = True
except ImportError:
    HAS_OSS = False

from app.config import settings


class StorageService:
    def __init__(self):
        self.access_key_id = settings.OSS_ACCESS_KEY_ID
        self.access_key_secret = settings.OSS_ACCESS_KEY_SECRET
        self.endpoint = settings.OSS_ENDPOINT
        self.bucket_name = settings.OSS_BUCKET_NAME
        self._bucket = None
    
    @property
    def bucket(self):
        if self._bucket is None and self.access_key_id and self.access_key_secret and HAS_OSS:
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self._bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
        return self._bucket
    
    def _generate_key(self, folder: str, filename: str) -> str:
        ext = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        date_prefix = datetime.now().strftime("%Y/%m/%d")
        return f"{folder}/{date_prefix}/{unique_name}"
    
    async def upload_file(
        self,
        file: BinaryIO,
        folder: str = "files",
        filename: Optional[str] = None
    ) -> Optional[str]:
        if self.bucket is None:
            return None
        
        key = self._generate_key(folder, filename or "file")
        try:
            self.bucket.put_object(key, file.read())
            return self.get_url(key)
        except Exception as e:
            print(f"Upload error: {e}")
            return None
    
    async def upload_bytes(
        self,
        data: bytes,
        folder: str = "files",
        filename: str = "file.bin"
    ) -> Optional[str]:
        if self.bucket is None:
            return None
        
        key = self._generate_key(folder, filename)
        try:
            self.bucket.put_object(key, data)
            return self.get_url(key)
        except Exception as e:
            print(f"Upload error: {e}")
            return None
    
    def get_url(self, key: str, expires: int = 3600 * 24 * 7) -> str:
        if self.bucket is None:
            return ""
        
        try:
            url = self.bucket.sign_url('GET', key, expires)
            return url
        except Exception:
            return f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/{key}"
    
    async def delete_file(self, key: str) -> bool:
        if self.bucket is None:
            return False
        
        try:
            self.bucket.delete_object(key)
            return True
        except Exception:
            return False
    
    async def file_exists(self, key: str) -> bool:
        if self.bucket is None:
            return False
        
        try:
            return self.bucket.object_exists(key)
        except Exception:
            return False


class LocalStorageService:
    def __init__(self, base_path: str = "uploads"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def _generate_path(self, folder: str, filename: str) -> str:
        ext = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        date_prefix = datetime.now().strftime("%Y/%m/%d")
        relative_path = f"{folder}/{date_prefix}/{unique_name}"
        full_path = os.path.join(self.base_path, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        return full_path, relative_path
    
    async def upload_file(
        self,
        file: BinaryIO,
        folder: str = "files",
        filename: Optional[str] = None
    ) -> Optional[str]:
        full_path, relative_path = self._generate_path(folder, filename or "file")
        try:
            with open(full_path, 'wb') as f:
                f.write(file.read())
            return f"/uploads/{relative_path}"
        except Exception as e:
            print(f"Upload error: {e}")
            return None
    
    async def upload_bytes(
        self,
        data: bytes,
        folder: str = "files",
        filename: str = "file.bin"
    ) -> Optional[str]:
        full_path, relative_path = self._generate_path(folder, filename)
        try:
            with open(full_path, 'wb') as f:
                f.write(data)
            return f"/uploads/{relative_path}"
        except Exception as e:
            print(f"Upload error: {e}")
            return None
    
    async def delete_file(self, relative_path: str) -> bool:
        full_path = os.path.join(self.base_path, relative_path.lstrip("/uploads/"))
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
            return True
        except Exception:
            return False
    
    async def file_exists(self, relative_path: str) -> bool:
        full_path = os.path.join(self.base_path, relative_path.lstrip("/uploads/"))
        return os.path.exists(full_path)


def get_storage_service() -> StorageService | LocalStorageService:
    if HAS_OSS and settings.OSS_ACCESS_KEY_ID and settings.OSS_ACCESS_KEY_SECRET:
        return StorageService()
    return LocalStorageService()
