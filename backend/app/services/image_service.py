from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import json
import httpx
import asyncio
import base64
import os
from app.config import settings
from app.services.storage_service import LocalStorageService


class ImageService(ABC):
    @abstractmethod
    async def generate_image(self, prompt: str) -> Optional[str]:
        pass


class MockImageService(ImageService):
    async def generate_image(self, prompt: str) -> Optional[str]:
        return None


class WanxImageService(ImageService):
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        self.model = "wanx-v1"
    
    async def generate_image(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            print("[WanxImageService] No API key configured")
            return None
        
        try:
            print(f"[WanxImageService] Starting image generation for prompt: {prompt[:50]}...")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable"
            }
            
            payload = {
                "model": self.model,
                "input": {
                    "prompt": prompt
                },
                "parameters": {
                    "style": "<auto>",
                    "size": "1024*1024",
                    "n": 1
                }
            }
            
            print(f"[WanxImageService] Sending request to {self.base_url}")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                print(f"[WanxImageService] Response status: {response.status_code}")
                
                if response.status_code not in [200, 201]:
                    print(f"[WanxImageService] Failed to create task: {response.status_code} - {response.text}")
                    return None
                
                result = response.json()
                print(f"[WanxImageService] Response: {result}")
                
                task_id = result.get("output", {}).get("task_id")
                
                if not task_id:
                    print(f"[WanxImageService] No task_id in response")
                    return None
                
                print(f"[WanxImageService] Task created: {task_id}")
                
                task_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
                
                for attempt in range(60):
                    await asyncio.sleep(2)
                    
                    status_response = await client.get(
                        task_url,
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    
                    if status_response.status_code != 200:
                        print(f"[WanxImageService] Status check failed: {status_response.status_code}")
                        continue
                    
                    status_result = status_response.json()
                    task_status = status_result.get("output", {}).get("task_status")
                    
                    print(f"[WanxImageService] Task status (attempt {attempt+1}): {task_status}")
                    
                    if task_status == "SUCCEEDED":
                        results = status_result.get("output", {}).get("results", [])
                        if results:
                            image_url = results[0].get("url")
                            if image_url:
                                print(f"[WanxImageService] Image URL: {image_url}")
                                return await self._download_and_save(image_url, prompt)
                        return None
                    elif task_status == "FAILED":
                        print(f"[WanxImageService] Task failed: {status_result}")
                        return None
                
                print("[WanxImageService] Timeout waiting for task")
                return None
                
        except Exception as e:
            print(f"[WanxImageService] Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _download_and_save(self, url: str, prompt: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    storage = LocalStorageService()
                    image_bytes = response.content
                    
                    relative_path = await storage.upload_bytes(
                        image_bytes,
                        folder="images",
                        filename=f"ai_image_{hash(prompt) % 100000}.png"
                    )
                    
                    if relative_path:
                        full_path = os.path.join(storage.base_path, relative_path.lstrip("/uploads/"))
                        return full_path
            return None
        except Exception as e:
            print(f"[WanxImageService] Download error: {e}")
            return None


class ImageServiceFactory:
    @staticmethod
    def get_service() -> ImageService:
        if settings.DASHSCOPE_API_KEY:
            return WanxImageService()
        return MockImageService()
