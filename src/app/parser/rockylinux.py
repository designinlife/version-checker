from asyncio import Semaphore

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from app.core.config import RockyLinuxSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: RockyLinuxSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Download Links: https://download.rockylinux.org/pub/rocky/
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET', 'https://wiki.rockylinux.org/rocky/version/',
                                                      is_json=False)

            # Analyzing HTML text data.
            soup = BeautifulSoup(data_s, 'html5lib')

            # RockyLinux 8/9
            el_table_rows = soup.select('.tabbed-block > table > tbody > tr')

            for el_row in el_table_rows:
                if isinstance(el_row, Tag):
                    ver_s = el_row.select_one('td:nth-child(1)').text
                    release_date_s = el_row.select_one('td:nth-child(3)').text

                    if len(release_date_s.strip()) > 0:
                        vhlp.append(ver_s)

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
