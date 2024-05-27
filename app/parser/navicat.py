from asyncio import Semaphore

from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import NavicatSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: NavicatSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        # US: https://www.navicat.com/en/products/navicat-premium-release-note
        # CN: https://www.navicat.com.cn/products/navicat-premium-release-note

        async with sem:
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET',
                                                      'https://www.navicat.com.cn/products/navicat-premium-release-note',
                                                      is_json=False)

            # Analyzing HTML text data.
            soup = BeautifulSoup(data_s, 'html5lib')

            elements = soup.select('div.note-title > b')

            for el in elements:
                vhlp.append(el.text.strip())

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
