import asyncio
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

        watch_vers = ('3.0', '2.9', '2.8', '2.6', '2.4', '2.2')

        # Make a batch request.
        tasks = []

        for ver in watch_vers:
            tasks.append(self.request('GET', f'https://git.haproxy.org/git/haproxy-{ver}.git/refs/tags/', is_json=False))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for url, http_status, _, data_s in results:
            if http_status != 200:
                logger.warning(f'HTTP status {http_status} | URL: {url}')
                continue

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
