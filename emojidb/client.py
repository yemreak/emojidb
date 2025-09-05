import unicodedata
from json import dump, load
from pathlib import Path
from typing import Any, List, Dict, Optional
from urllib.parse import quote

from aiohttp import ClientSession
from easy_requests import Connection
from bs4 import BeautifulSoup

from .cache import EmojiCache, EmojiCacheSqlite




def escape_query(query: str) -> str:
    query = query.replace("-", "--")
    query = query.replace(" ", "-")
    return quote(query, safe="")


class EmojiDBClient:
    """A client for the EmojiDB website."""

    # the kwargs have to be there for backwards compatibility
    def __init__(self, cache: Optional[EmojiCache] = None, **kwargs) -> None:
        self.async_client = None

        self.cache = EmojiCacheSqlite(expire_after_days=2) if cache is None else cache
        self.connection = Connection()
        self.connection.generate_headers()

    # the synchronous context manager doesn't do anything, 
    # however it exists so that you can use this synchronous similar to how you'd use async 
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

    async def __aenter__(self):
        self.async_client = AsyncEmojiDBClient(cache=self.cache)
        return self.async_client

    async def __aexit__(self, *args: Any):
        assert self.async_client is not None, "EmojiDBClient.__aexit__ has to be called from a context manager"
        await self.async_client.close()

    def _search_no_cache(self, query: str):
        response = self.connection.get(f"https://emojidb.org/{query}-emojis")
        soup = BeautifulSoup(response.text, "html.parser")
        results =  [r.text for r in soup.find_all("div", class_="emoji")]

        self.cache.write_cache(query=query, emojis=results)
        return results


    def search(self, query: str) -> List[str]:
        query = escape_query(query)

        if self.cache.has_cache(query):
            return self.cache.get_cache(query)
        
        return self._search_no_cache(query=query)


class AsyncEmojiDBClient(EmojiDBClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.session = ClientSession()

    async def close(self):
        await self.session.close()
    
    async def _search_no_cache(self, query: str) -> List[str]:
        print("actually downloading async")

        async with self.session.get(
            f"https://emojidb.org/{query}-emojis"
        ) as response:
            soup = BeautifulSoup(await response.content.read(), "html.parser")
            results =  [r.text for r in soup.find_all("div", class_="emoji")]
            self.cache.write_cache(query=query, emojis=results)
            return results
        
    async def search(self, query: str) -> List[str]:
        query = escape_query(query)

        if self.cache.has_cache(query):
            return self.cache.get_cache(query)
        
        return await self._search_no_cache(query)
    
    async def search_for_emojis(self, query: str) -> list[tuple[str, str]]:
        """
        Only exists for backwards compatibility.
        Use search instead
        """
        return [(e, unicodedata.name(e, "") if len(e) == 1 else "") for e in await self.search(query=query)]
