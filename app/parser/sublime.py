from asyncio import Semaphore

from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import SublimeSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: SublimeSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET', 'https://www.sublimetext.com/download',
                                                      is_json=False)

            soup = BeautifulSoup(data_s, 'html5lib')
            element = soup.select_one('div.downloads > p.latest')

            vhlp.append(element.text.strip())

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
