from asyncio import Semaphore

from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import HAProxySoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: HAProxySoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET',
                                                      'https://git.haproxy.org/git/haproxy-3.0.git/refs/tags/',
                                                      is_json=False)

            # Analyzing HTML text data.
            soup = BeautifulSoup(data_s, 'html5lib')

            elements = soup.select('pre > a')

            # noinspection DuplicatedCode
            for el in elements:
                vhlp.append(el.text.strip())

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
