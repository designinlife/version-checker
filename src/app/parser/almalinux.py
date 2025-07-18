from asyncio import Semaphore

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from app.core.config import AlmaLinuxSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: AlmaLinuxSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET', 'https://wiki.almalinux.org/release-notes/',
                                                      is_json=False)

            # Analyzing HTML text data.
            soup = BeautifulSoup(data_s, 'html5lib')

            os_major_vers = (10, 9, 8)

            for os_ver in os_major_vers:
                el_almalinux = soup.select_one(f'#almalinux-os-{os_ver}')
                el_almalinux_table = el_almalinux.find_next_sibling('table')
                el_almalinux_trs = el_almalinux_table.select('tbody > tr')

                for v in el_almalinux_trs:
                    if isinstance(v, Tag):
                        link_ver = v.select_one('td:nth-child(1) > a:nth-child(1)').text.strip()
                        release_date = v.select_one('td:nth-child(4)').text.strip()

                        if len(release_date) > 0:
                            vhlp.append(link_ver)

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
