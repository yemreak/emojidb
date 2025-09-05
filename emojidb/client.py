import unicodedata
from json import dump, load
from pathlib import Path
from typing import Any, List, Dict
from urllib.parse import quote

from platformdirs import user_cache_dir
from aiohttp import ClientSession
from easy_requests import Connection
from bs4 import BeautifulSoup



# initialize the global cache
def init_cache() -> Path:
    cache_dir = Path(user_cache_dir("emojidb-python", "yemreak"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "emojis.json"
    if not cache_path.exists():
        cache_path.write_text("{}")

    return cache_path


CACHE_PATH = init_cache()


def escape_query(query: str) -> str:
    query = query.replace("-", "--")
    query = query.replace(" ", "-")
    return quote(query, safe="")


class EmojiDBClient:
    """A client for the EmojiDB website."""

    # the kwargs have to be there for backwards compatibility
    def __init__(self, **kwargs) -> None:
        self.async_client = None

        self.connection = Connection()
        self.connection.generate_headers()

    # the synchronous context manager doesn't do anything, 
    # however it exists so that you can use this synchronous similar to how you'd use async 
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

    async def __aenter__(self):
        self.async_client = AsyncEmojiDBClient()
        return self.async_client

    async def __aexit__(self, *args: Any):
        assert self.async_client is not None, "EmojiDBClient.__aexit__ has to be called from a context manager"
        await self.async_client.close()

    def search(self, query: str) -> List[str]:
        query = escape_query(query)

        json_db: Dict[str, List[str]]
        with CACHE_PATH.open("r") as f:
            json_db = load(f)

        if query in json_db:
            return json_db[query]
        
        response = self.connection.get(f"https://emojidb.org/{query}-emojis")
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("div", class_="emoji")
        
        json_db[query] = [result.text for result in results]

        with CACHE_PATH.open("w") as f:
            dump(json_db, f, ensure_ascii=False)

        return json_db[query]


class AsyncEmojiDBClient(EmojiDBClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.session = ClientSession()

    async def close(self):
        await self.session.close()
    
    async def search(self, query: str) -> List[str]:
        query = escape_query(query)

        json_db: Dict[str, List[str]]
        with CACHE_PATH.open("r") as f:
            json_db = load(f)

        if query in json_db:
            return json_db[query]

        async with self.session.get(
            f"https://emojidb.org/{query}-emojis"
        ) as response:
            soup = BeautifulSoup(await response.content.read(), "html.parser")
            results = soup.find_all("div", class_="emoji")
            json_db[query] = [result.text for result in results]

            with CACHE_PATH.open("w") as f:
                dump(json_db, f, ensure_ascii=False)

            return json_db[query]
    
    async def search_for_emojis(self, query: str) -> list[tuple[str, str]]:
        """
        Only exists for backwards compatibility.
        Use search instead
        """
        return [(e, unicodedata.name(e, "")) for e in await self.search(query=query)]
