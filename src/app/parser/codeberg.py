from asyncio import Semaphore

import feedparser
from loguru import logger

from app.core.config import CodebergSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: CodebergSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            if soft.release:
                api_url = f'https://{soft.host}/{soft.repo}/releases.rss'
            else:
                api_url = f'https://{soft.host}/{soft.repo}/tags.rss'

            _, status, _, data_s = await self.request('GET', api_url)

            rss = feedparser.parse(data_s)

            if rss and isinstance(rss.entries, list):
                for v in rss.entries:
                    if isinstance(v, feedparser.FeedParserDict):
                        vhlp.append(v['title'])

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
