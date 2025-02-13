from typing import List, Dict, Any, Optional, Set
from bs4 import BeautifulSoup
import aiohttp
from loguru import logger
from urllib.parse import urlparse
import asyncio

class URLContentCache:
    def __init__(self):
        self._cache = {}

    def get(self, url: str) -> Optional[str]:
        return self._cache.get(url)

    def set(self, url: str, content: str) -> None:
        self._cache[url] = content

    def has(self, url: str) -> bool:
        return url in self._cache

class URLProcessor:
    def __init__(self, config):
        self.config = config
        self.cache = URLContentCache()

    async def parse_url_content(self, url: str) -> str:
        """解析URL内容"""
        if self.cache.has(url):
            logger.info(f"使用缓存的URL内容: {url}")
            return self.cache.get(url)

        logger.info(f"开始解析URL内容: {url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP错误: {response.status}")
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # 移除不需要的元素
                    for elem in soup.select('script, style, iframe, [class*="banner"], [class*="advert"]'):
                        elem.decompose()

                    # 提取标题
                    title = soup.find('h1')
                    if not title:
                        title = soup.find('title')
                    title_text = title.get_text().strip() if title else ''

                    # 提取主要内容
                    content = []
                    for p in soup.find_all(['p', 'h2', 'h3', 'h4']):
                        text = p.get_text().strip()
                        if len(text) > 20:  # 过滤短文本
                            content.append(text)

                    formatted_content = f"标题：{title_text}\n\n正文：\n{' '.join(content)}"
                    
                    # 存入缓存
                    self.cache.set(url, formatted_content)
                    return formatted_content

        except Exception as e:
            logger.error(f"解析URL失败: {url}, 错误: {str(e)}")
            return f"[无法获取 {url} 的内容: {str(e)}]"

    async def process_urls(self, urls: Set[str]) -> Dict[str, str]:
        """批量处理URL"""
        tasks = []
        for url in urls:
            if not self.cache.has(url):
                tasks.append(self.parse_url_content(url))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return {url: result for url, result in zip(urls, results) if not isinstance(result, Exception)}
        return {}

def extract_urls(text: str) -> Set[str]:
    """从文本中提取URL"""
    urls = set()
    words = text.split()
    for word in words:
        if word.startswith(('http://', 'https://')):
            try:
                parsed = urlparse(word)
                if parsed.netloc:
                    urls.add(word)
            except Exception:
                continue
    return urls

def sanitize_content(content: Any) -> Any:
    """清理和格式化内容"""
    if isinstance(content, list):
        return [sanitize_content(item) for item in content]
    elif isinstance(content, dict):
        if content.get('type') == 'image_url' and 'image_url' in content:
            return {
                **content,
                'image_url': {
                    **content['image_url'],
                    'url': content['image_url']['url'][:20] + '...[base64]...'
                }
            }
        return {k: sanitize_content(v) for k, v in content.items()}
    return content