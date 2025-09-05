# 📦 EmojiDB

- Simple python wrapper for emojidb.com

## REPO MOVED
This project is now maintained by @hazel-noack
See: [https://github.com/hazel-noack/emojidb](https://github.com/hazel-noack/emojidb-python)

## ⭐️ Usage

```bash
pip install emojidb-python
```

```python
from asyncio import run
from emojidb import EmojiDBClient


async def main():
    query = "love"
    async with EmojiDBClient() as client:
        for emoji, info in await client.search_for_emojis(query):
            print(emoji, info)


if __name__ == "__main__":
    run(main)
```

## 🪪 License

```
Copyright 2023 Yunus Emre Ak ~ YEmreAk.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
