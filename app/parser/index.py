from asyncio import Semaphore
from pathlib import Path

from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import IndexSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: IndexSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET', soft.url, is_json=False)

            soup = BeautifulSoup(data_s, 'html5lib')

            link_elements = soup.select('pre > a[href], td > a[href]')

            for v in link_elements:
                vhlp.append(Path(v.attrs['href']).name)

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
