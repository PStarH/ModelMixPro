from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
import json
import asyncio
from loguru import logger
from config.settings import settings
from models import ModelResponse  # Ensure ModelResponse is imported from models

class ModelHandler:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def call_openai(self, messages: List[Dict[str, Any]], stream: bool = True) -> ModelResponse:
        """调用OpenAI模型，并支持链式思考（chain-of-thought）"""
        # Prepend the chain-of-thought reasoning prompt
        new_messages = list(messages)
        new_messages.insert(0, {"role": "system", "content": settings.OPENAI_THINKING_PROMPT})
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": settings.OPENAI_MODEL,
                "messages": new_messages,
                "stream": stream,
                "max_tokens": settings.OPENAI_MAX_TOKENS,
                "temperature": settings.OPENAI_TEMPERATURE
            }
            try:
                async with client.post(
                    f"{settings.OPENAI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if stream:
                        return response
                    else:
                        data = await response.json()
                        return ModelResponse(**data)
            except Exception as e:
                logger.error(f"OpenAI调用失败: {str(e)}")
                raise
    
    async def call_custom_model(self, messages: List[Dict[str, Any]], stream: bool = True) -> ModelResponse:
        """调用自定义模型"""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {settings.CUSTOM_MODEL_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": settings.CUSTOM_MODEL_NAME,
                "messages": messages,
                "stream": stream
            }
            try:
                async with client.post(
                    f"{settings.CUSTOM_MODEL_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if stream:
                        return response
                    else:
                        data = await response.json()
                        return ModelResponse(**data)
            except Exception as e:
                logger.error(f"自定义模型调用失败: {str(e)}")
                raise
    
    async def determine_if_search_needed(self, messages: List[Dict[str, Any]]) -> bool:
        try:
            response = await self.client.post(
                f"{settings.PROXY_URL4}/v1/chat/completions",
                json={
                    "model": settings.GoogleSearch_MODEL,
                    "messages": [
                        {"role": "system", "content": settings.GoogleSearch_Determine_PROMPT},
                        *messages
                    ],
                    "max_tokens": settings.GoogleSearch_Model_MAX_TOKENS,
                    "temperature": settings.GoogleSearch_Model_TEMPERATURE,
                    "stream": False
                },
                headers={
                    "Authorization": f"Bearer {settings.GoogleSearch_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            decision = response.json()["choices"][0]["message"]["content"].strip().lower()
            return decision == "yes"
        except Exception as e:
            logger.error(f"判断是否需要搜索时出错: {str(e)}")
            return False
            
    async def perform_web_search(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        try:
            # 获取搜索关键词
            response = await self.client.post(
                f"{settings.PROXY_URL4}/v1/chat/completions",
                json={
                    "model": settings.GoogleSearch_MODEL,
                    "messages": [
                        {"role": "system", "content": settings.GoogleSearch_PROMPT},
                        *messages
                    ],
                    "max_tokens": settings.GoogleSearch_Model_MAX_TOKENS,
                    "temperature": settings.GoogleSearch_Model_TEMPERATURE,
                    "stream": False
                },
                headers={
                    "Authorization": f"Bearer {settings.GoogleSearch_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            search_terms = response.json()["choices"][0]["message"]["content"]
            
            # 执行搜索
            search_response = await self.client.post(
                f"{settings.PROXY_URL4}/v1/chat/completions",
                json={
                    "model": settings.GoogleSearch_MODEL,
                    "messages": [
                        {"role": "system", "content": "Please search the web for the following query and provide relevant information:"},
                        {"role": "user", "content": search_terms}
                    ],
                    "max_tokens": settings.GoogleSearch_Model_MAX_TOKENS,
                    "temperature": settings.GoogleSearch_Model_TEMPERATURE,
                    "stream": False,
                    "tools": [{
                        "type": "function",
                        "function": {
                            "name": "googleSearch",
                            "description": "Search the web for relevant information",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "The search query"
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    }]
                },
                headers={
                    "Authorization": f"Bearer {settings.GoogleSearch_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            search_response.raise_for_status()
            return search_response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"执行网络搜索时出错: {str(e)}")
            return None
            
    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        request: Any
    ) -> AsyncGenerator[str, None]:
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{settings.PROXY_URL}/v1/chat/completions",
                    json={
                        "model": settings.DEEPSEEK_R1_MODEL,
                        "messages": messages,
                        "max_tokens": settings.DEEPSEEK_R1_MAX_TOKENS,
                        "temperature": settings.DEEPSEEK_R1_TEMPERATURE,
                        "stream": True
                    },
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_R1_API_KEY}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            if line.strip() == "data: [DONE]":
                                yield line + "\n"
                                continue
                                
                            data = json.loads(line[6:])
                            # 转换为OpenAI格式
                            formatted_data = {
                                "id": data.get("id"),
                                "object": "chat.completion.chunk",
                                "created": data.get("created"),
                                "model": settings.HYBRID_MODEL_NAME,
                                "choices": [{
                                    "delta": {
                                        "content": data["choices"][0]["delta"].get("content", "")
                                    },
                                    "index": 0,
                                    "finish_reason": data["choices"][0].get("finish_reason")
                                }]
                            }
                            yield f"data: {json.dumps(formatted_data)}\n\n"
        except Exception as e:
            logger.error(f"流式响应处理出错: {str(e)}")
            # 如果R1失败，尝试使用Gemini
            try:
                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        "POST",
                        f"{settings.PROXY_URL2}/v1/chat/completions",
                        json={
                            "model": settings.Model_output_MODEL,
                            "messages": messages,
                            "max_tokens": settings.Model_output_MAX_TOKENS,
                            "temperature": settings.Model_output_TEMPERATURE,
                            "stream": True
                        },
                        headers={
                            "Authorization": f"Bearer {settings.Model_output_API_KEY}",
                            "Content-Type": "application/json"
                        }
                    ) as response:
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                yield line + "\n"
            except Exception as gemini_error:
                logger.error(f"Gemini也失败了: {str(gemini_error)}")
                yield "data: {\"error\": \"All models failed\"}\n\n"