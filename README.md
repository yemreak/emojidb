# 📦 EmojiDB

Simple python wrapper for [emojidb.com](https://emojidb.org/).

## ⭐️ Usage

```bash
pip install emojidb-python
```

```python
from asyncio import run
from emojidb import EmojiDBClient

from urllib.parse import quote


async def _main_async():
    query = "love"

    async with EmojiDBClient() as client:
        emojis = await client.search(query)
        print(*emojis, sep=", ")

        client.like(emojis[0], query)

def main_async():
    run(_main_async())


def main():
    query = "love"

    with EmojiDBClient() as client:
        emojis = client.search(query)
        print(*emojis, sep=", ")

        client.like(emojis[0], query)


if __name__ == "__main__":
    main()
    main_async()
```

## Features

- use an asynchronous client or a synchronous one
- cache the results using sqlite
- search for emojis
- like and dislike emojis (please do not abuse that)

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
