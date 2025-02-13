from typing import List, Dict, Any, Optional
import httpx
from loguru import logger
from config.settings import settings

class ImageProcessor:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def process_image(self, image_message: Dict[str, Any]) -> Optional[str]:
        try:
            request_body = {
                "model": settings.Image_MODEL,
                "messages": [
                    {"role": "system", "content": settings.Image_Model_PROMPT},
                    {"role": "user", "content": [image_message]}
                ],
                "max_tokens": settings.Image_Model_MAX_TOKENS,
                "temperature": settings.Image_Model_TEMPERATURE,
                "stream": False
            }
            
            response = await self.client.post(
                f"{settings.PROXY_URL3}/v1/chat/completions",
                json=request_body,
                headers={
                    "Authorization": f"Bearer {settings.Image_Model_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"图片处理错误: {str(e)}")
            return None
            
    @staticmethod
    def has_new_images(messages: List[Dict[str, Any]]) -> bool:
        if not messages:
            return False
        last_message = messages[-1]
        return (
            isinstance(last_message.get('content'), list) and
            any(item.get('type') == 'image_url' for item in last_message['content'])
        )
        
    @staticmethod
    def extract_last_images(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not messages:
            return []
            
        last_message = messages[-1]
        if not isinstance(last_message.get('content'), list):
            return []
            
        return [
            item for item in last_message['content']
            if item.get('type') == 'image_url'
        ]