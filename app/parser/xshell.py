import json
from asyncio import Semaphore

from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import XShellSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: XShellSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET', 'https://update.netsarang.com/json/download/process.html',
                                                      params={
                                                          'md': 'getUpdateHistory',
                                                          'language': '2',
                                                          'productName': 'xshell-update-history',
                                                      },
                                                      is_json=False)

            data_r = json.loads(data_s)

            content = data_r['message']

            soup = BeautifulSoup(content, 'html5lib')
            elements = soup.select('dt.h4')

            # noinspection DuplicatedCode
            for element in elements:
                vhlp.append(element.text.strip())

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
