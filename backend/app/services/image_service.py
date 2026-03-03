from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import json
import httpx
import asyncio
import base64
import os
import logging
from app.config import settings
from app.services.storage_service import LocalStorageService

logger = logging.getLogger(__name__)


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
        self.max_retries = 3
        self.retry_delay = 2
    
    async def generate_image(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            logger.warning("No API key configured for WanxImageService")
            return None
        
        try:
            logger.info(f"Starting image generation for prompt: {prompt[:80]}...")
            
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
            
            logger.debug(f"Sending request to {self.base_url}")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                logger.debug(f"Response status: {response.status_code}")
                
                if response.status_code not in [200, 201]:
                    logger.error(f"Failed to create task: {response.status_code} - {response.text}")
                    return None
                
                result = response.json()
                logger.debug(f"Response: {json.dumps(result, indent=2)}")
                
                task_id = result.get("output", {}).get("task_id")
                
                if not task_id:
                    logger.error("No task_id in response")
                    return None
                
                logger.info(f"Task created: {task_id}")
                
                task_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
                
                for attempt in range(60):
                    await asyncio.sleep(2)
                    
                    try:
                        status_response = await client.get(
                            task_url,
                            headers={"Authorization": f"Bearer {self.api_key}"}
                        )
                        
                        if status_response.status_code != 200:
                            logger.warning(f"Status check failed: {status_response.status_code}")
                            continue
                        
                        status_result = status_response.json()
                        task_status = status_result.get("output", {}).get("task_status")
                        
                        logger.debug(f"Task status (attempt {attempt+1}): {task_status}")
                        
                        if task_status == "SUCCEEDED":
                            results = status_result.get("output", {}).get("results", [])
                            if results:
                                image_url = results[0].get("url")
                                if image_url:
                                    logger.info(f"Image URL obtained: {image_url}")
                                    return await self._download_and_save(image_url, prompt)
                            logger.warning("No results in successful response")
                            return None
                        elif task_status == "FAILED":
                            error_msg = status_result.get("output", {}).get("message", "Unknown error")
                            logger.error(f"Task failed: {error_msg}")
                            return None
                        elif task_status in ["PENDING", "RUNNING"]:
                            continue
                        else:
                            logger.warning(f"Unknown task status: {task_status}")
                            
                    except Exception as e:
                        logger.error(f"Error checking task status: {e}")
                        continue
                
                logger.error("Timeout waiting for task completion")
                return None
                
        except httpx.TimeoutException:
            logger.error("Request timeout")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in image generation: {e}", exc_info=True)
            return None
    
    async def _download_and_save(self, url: str, prompt: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    storage = LocalStorageService()
                    image_bytes = response.content
                    
                    logger.debug(f"Downloaded image: {len(image_bytes)} bytes")
                    
                    relative_path = await storage.upload_bytes(
                        image_bytes,
                        folder="images",
                        filename=f"ai_image_{hash(prompt) % 100000}.png"
                    )
                    
                    if relative_path:
                        full_path = os.path.join(storage.base_path, relative_path.lstrip("/uploads/"))
                        logger.info(f"Image saved to: {full_path}")
                        return full_path
                    else:
                        logger.error("Failed to save image to storage")
                else:
                    logger.error(f"Failed to download image: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error downloading and saving image: {e}", exc_info=True)
            return None


class ImageServiceFactory:
    @staticmethod
    def get_service() -> ImageService:
        if settings.DASHSCOPE_API_KEY:
            return WanxImageService()
        return MockImageService()
