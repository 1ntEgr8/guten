import asyncio
import httpx
import feedparser
import pandas as pd

from .config import Config
from .source import Source, SourceGroup
from .backend import Loader
from .utils import eprint

from dataclasses import dataclass
from typing import List, Tuple
from urllib.parse import urlparse
from pathlib import Path


RESPONSE_OK_STATUS = 200

class PressException(Exception):
    def __init__(self, message, exc):
        self.message = message
        self.exc = exc
        super().__init__(self.message, exc)


def is_path(s: str):
    return urlparse(s).scheme == ""

FetchedSource = Tuple[Source, pd.DataFrame]
FetchedSourceGroup = Tuple[SourceGroup, List[FetchedSource]]

@dataclass
class Press:
    config: Config

    async def fetch_source(self, client: httpx.AsyncClient, source: Source) -> FetchedSource:
        try:
            # Fetch feed
            if is_path(source.url):
                path = Path(source.url).expanduser()
                with open(path, 'r') as f:
                    feed = f.read()
            else:
                response = await client.get(source.url, follow_redirects=True)
                response.raise_for_status()
                feed = response.text

            # Parse feed
            data = feedparser.parse(feed)

            # Convert to data frame
            df = pd.DataFrame(data["entries"])

            eprint(f"Fetched '{source}'")

            return (source, df)
        except Exception as e:

            eprint(f"FAILED to fetch source '{source}'. Exception = '{e}'")

            raise PressException(f"Failed to fetch source '{source}'", e)

    async def fetch_source_group(self, client: httpx.AsyncClient, source_group: SourceGroup) -> FetchedSourceGroup:
        tasks = [
            self.fetch_source(client, source)
            for source in source_group.sources
        ]
        sources = await asyncio.gather(*tasks, return_exceptions=True)
        sources = [source for source in sources if not isinstance(source, Exception)]
        return (source_group, sources)

    async def fetch_source_groups(self) -> List[FetchedSourceGroup]:
        async with httpx.AsyncClient() as client:
            tasks = [
                self.fetch_source_group(client, source_group)
                for source_group in self.config.source_groups
            ]
            data = await asyncio.gather(*tasks)
        return data

    async def run(self, backend_key: str, output_dir: Path) -> Path:
        loader = Loader(self.config.settings.backends_dir)
        backend = loader.load(backend_key)()
        data = await self.fetch_source_groups()
        output_dir = output_dir / Path(backend_key)
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        return await backend.run(data, output_dir)
