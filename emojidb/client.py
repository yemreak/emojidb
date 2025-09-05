import unicodedata
from json import dump, load
from pathlib import Path
from typing import Any

from platformdirs import user_cache_dir
from aiohttp import ClientSession
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


class EmojiDBClient:
    """A client for the EmojiDB website."""
    session: ClientSession

    # the kwargs have to be there for backwards compatibility
    def __init__(self, **kwargs) -> None:
        pass

    async def __aenter__(self):
        self.session = ClientSession()
        return self

    async def __aexit__(self, *args: Any):
        await self.session.close()

    async def search_for_emojis(self, query: str) -> list[tuple[str, str]]:
        """Search emojis for query"""
        query = query.replace(" ", "-")

        with CACHE_PATH.open("r") as f:
            json_db = load(f)

        if query not in json_db:
            async with self.session.get(
                f"https://emojidb.org/{query}-emojis"
            ) as response:
                soup = BeautifulSoup(await response.content.read(), "html.parser")
                results = soup.find_all("div", class_="emoji")
                emojis = [result.text for result in results]
            json_db[query] = emojis

            with CACHE_PATH.open("w") as f:
                dump(json_db, f, ensure_ascii=False)
        
        emojis_info = []
        
        for emoji in json_db[query]:
            try:
                info = unicodedata.name(emoji).capitalize()
            except:
                info = ""
            emojis_info.append((emoji, info))
        
        return emojis_info
