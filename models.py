from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import aiohttp
from loguru import logger
from config import Config

class ModelResponse(BaseModel):
    choices: List[Dict[str, Any]]
    model: str

class ModelHandler:
    def __init__(self, config: Config):
        self.config = config
        self.active_requests = []

    async def call_deepseek_r1(self, messages: List[Dict[str, Any]], stream: bool = True) -> ModelResponse:
        """调用DeepSeek R1模型"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.config.DEEPSEEK_R1_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.config.DEEPSEEK_R1_MODEL,
                "messages": messages,
                "stream": stream,
                "max_tokens": self.config.DEEPSEEK_R1_MAX_TOKENS,
                "temperature": self.config.DEEPSEEK_R1_TEMPERATURE
            }
            try:
                async with session.post(
                    f"{self.config.PROXY_URL}/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if stream:
                        return response
                    else:
                        data = await response.json()
                        return ModelResponse(**data)
            except Exception as e:
                logger.error(f"DeepSeek R1调用失败: {str(e)}")
                raise

    async def call_gemini(self, messages: List[Dict[str, Any]], stream: bool = True) -> ModelResponse:
        """调用Gemini模型"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.config.Image_Model_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.config.Image_MODEL,
                "messages": messages,
                "stream": stream,
                "max_tokens": self.config.Image_Model_MAX_TOKENS,
                "temperature": self.config.Image_Model_TEMPERATURE
            }
            try:
                async with session.post(
                    f"{self.config.PROXY_URL}/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if stream:
                        return response
                    else:
                        data = await response.json()
                        return ModelResponse(**data)
            except Exception as e:
                logger.error(f"Gemini调用失败: {str(e)}")
                raise

    async def call_google_search(self, messages: List[Dict[str, Any]], stream: bool = True) -> ModelResponse:
        """调用Google搜索模型"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.config.GoogleSearch_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.config.GoogleSearch_MODEL,
                "messages": messages,
                "stream": stream,
                "max_tokens": self.config.GoogleSearch_Model_MAX_TOKENS,
                "temperature": self.config.GoogleSearch_Model_TEMPERATURE
            }
            try:
                async with session.post(
                    f"{self.config.PROXY_URL}/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if stream:
                        return response
                    else:
                        data = await response.json()
                        return ModelResponse(**data)
            except Exception as e:
                logger.error(f"Google搜索模型调用失败: {str(e)}")
                raise