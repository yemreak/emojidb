import unicodedata
from json import dump, load
from pathlib import Path
from typing import Any

from platformdirs import user_cache_dir
from aiohttp import ClientSession
from bs4 import BeautifulSoup


class EmojiDBClient:
    """A client for the EmojiDB website."""
    session: ClientSession

    def __init__(self, relative_path: str = "emojidb") -> None:
        cache_dir = Path(user_cache_dir("emojidb-python", "yemreak"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = cache_dir / "emojis.json"
        if not self.cache_path.exists():
            self.cache_path.write_text("{}")

    async def __aenter__(self):
        self.session = ClientSession()
        return self

    async def __aexit__(self, *args: Any):
        await self.session.close()

    async def search_for_emojis(self, query: str) -> list[tuple[str, str]]:
        """Search emojis for query"""
        query = query.replace(" ", "-")
        with self.cache_path.open("r") as f:
            jsondb = load(f)
        if query not in jsondb:
            async with self.session.get(
                f"https://emojidb.org/{query}-emojis"
            ) as response:
                soup = BeautifulSoup(await response.content.read(), "html.parser")
                results = soup.find_all("div", class_="emoji")
                emojis = [result.text for result in results]
            jsondb[query] = emojis

            with self.cache_path.open("w") as f:
                dump(jsondb, f, ensure_ascii=False)
        
        emojis_info = []
        
        for emoji in jsondb[query]:
            try:
                info = unicodedata.name(emoji).capitalize()
            except:
                info = ""
            emojis_info.append((emoji, info))
        
        return emojis_info
