import httpx
from loguru import logger

async def make_request(url: str, method: str = "GET", data: dict = None, headers: dict = None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")