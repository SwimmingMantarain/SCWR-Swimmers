from bs4 import BeautifulSoup
from functools import wraps
import asyncio
import httpx
import time

class ScraperError(Exception):
    """Generic class for scraping related errors"""

class ScrapingError(ScraperError):
    """Failed to scrape and obtain html."""

class DataNotFoundError(ScraperError):
    """Target data not found."""

class HTMLParsingError(ScraperError):
    """Failed to find requested html."""

def rate_limited(min_interval: int = 1):
    """
    Decorator that enforces a minimum interval between calls of the wrapped coroutine.
    Thread/async safe due to the shared lock.
    """
    def decorator(func):
        last_time_called = 0.0
        lock = asyncio.Lock()

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_time_called
            async with lock:
                elapsed = time.time() - last_time_called
                wait = min_interval - elapsed
                if wait > 0:
                    await asyncio.sleep(wait)
                result = await func(*args, **kwargs)
                last_time_called = time.time()
                return result
        
        return wrapper
    
    return decorator

class BaseScraper:
    def __init__(self, url_book):
        self.url_book = url_book
        self.client = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()

    @rate_limited(1)
    async def _fetch(self, url: str):
        response = await self.client.get(url)
        if response.status_code != 200 or not response.text:
            raise ScrapingError(f"Failed to fetch {url} - status {response.status_code}")
        return response

    def _parse(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, 'lxml')
