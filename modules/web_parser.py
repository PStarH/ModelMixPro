from typing import List, Dict, Any, Set
import httpx
from bs4 import BeautifulSoup
import asyncio
from loguru import logger
from urllib.parse import urlparse
import re
from config.settings import settings

class WebParser:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)
        self.url_cache = {}

    async def preprocess_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed_messages = messages.copy()
        all_urls: Set[str] = set()
        
        for message in messages:
            text_content = ''
            if isinstance(message['content'], str):
                text_content = message['content']
            elif isinstance(message['content'], list):
                text_content = '\n'.join(
                    item['text'] for item in message['content']
                    if item.get('type') == 'text'
                )
                
            if text_content:
                urls = re.findall(r'https?://[^\s)]+', text_content)
                all_urls.update(url.strip() for url in urls if self._is_valid_url(url))
                
        urls_to_process = [url for url in all_urls if url not in self.url_cache]
        if urls_to_process:
            contents = await asyncio.gather(*[self._parse_url(url) for url in urls_to_process])
            for url, content in zip(urls_to_process, contents):
                if content:
                    self.url_cache[url] = content
                    
        for message in processed_messages:
            if isinstance(message['content'], str):
                for url in all_urls:
                    if url in message['content'] and url in self.url_cache:
                        message['content'] = message['content'].replace(
                            url, f"\n\n[URL内容: {url}]\n{self.url_cache[url]}\n"
                        )
                        
        return processed_messages
        
    async def _parse_url(self, url: str) -> Optional[str]:
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除不需要的元素
            for elem in soup.select('script, style, iframe, video, [class*="banner"], [class*="advert"], [class*="ads"]'):
                elem.decompose()
                
            # 提取标题
            title = (
                soup.find('h1').get_text().strip() if soup.find('h1')
                else soup.select('[class*="title"]')[0].get_text().strip() if soup.select('[class*="title"]')
                else soup.find('title').get_text().strip() if soup.find('title')
                else ''
            )
            
            # 提取主要内容
            content_selectors = [
                'article', '[class*="article"]', '[class*="content"]',
                'main', '#main', '.text', '.body'
            ]
            
            main_content = ''
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    paragraphs = []
                    for elem in elements[0].find_all(['p', 'h2', 'h3', 'h4', 'li']):
                        text = elem.get_text().strip()
                        if text and len(text) > 20:
                            paragraphs.append(text)
                    if paragraphs:
                        main_content = '\n\n'.join(paragraphs)
                        break
                        
            if not main_content:
                paragraphs = []
                for elem in soup.find('body').find_all(['p', 'h2', 'h3', 'h4', 'li']):
                    text = elem.get_text().strip()
                    if text and len(text) > 20:
                        paragraphs.append(text)
                main_content = '\n\n'.join(paragraphs)
                
            return f"标题：{title}\n\n正文：\n{main_content}"
            
        except Exception as e:
            logger.error(f"解析URL失败 {url}: {str(e)}")
            return None
            
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url.strip())
            return all([result.scheme, result.netloc])
        except:
            return False