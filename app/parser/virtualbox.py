import re
from asyncio import Semaphore

from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import VirtualBoxSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: VirtualBoxSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET', 'https://www.virtualbox.org/wiki/Downloads',
                                                      is_json=False)

            soup = BeautifulSoup(data_s, 'html5lib')

            latest_element = soup.select_one('#wikipage > h3:nth-of-type(1)')
            download_link_elements = soup.select('#wikipage > ul:nth-of-type(1) > li > a[class=ext-link]')
            extension_pack_link_elements = soup.select('#wikipage > ul:nth-of-type(3) > li > a[class=ext-link]')
            sdk_link_elements = soup.select('#wikipage > ul:nth-of-type(4) > li > a[class=ext-link]')

            exp_ver = re.compile(
                r'^VirtualBox (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)) platform packages$',
                flags=re.I)

            m = exp_ver.match(latest_element.text.strip())

            if m:
                latest_version = m.group('version')
                vhlp.append(latest_version)

                # Installer
                if download_link_elements:
                    for v in download_link_elements:
                        if v.attrs['href'].endswith('Win.exe'):
                            vhlp.add_download_url(v.attrs['href'])

                # Extension Pack
                if extension_pack_link_elements:
                    for v in extension_pack_link_elements:
                        if v.attrs['href'].endswith('.vbox-extpack'):
                            vhlp.add_download_url(v.attrs['href'])

                # SDK
                if sdk_link_elements:
                    for v in sdk_link_elements:
                        vhlp.add_download_url(v.attrs['href'])

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
