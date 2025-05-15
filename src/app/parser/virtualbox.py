import re
from asyncio import Semaphore
from urllib.parse import urljoin

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
            _, status, _, data_s = await self.request('GET', 'https://download.virtualbox.org/virtualbox/',
                                                      is_json=False)

            soup = BeautifulSoup(data_s, 'html5lib')

            link_elements = soup.select('pre > a[href]')

            exp_ver = re.compile(
                r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$',
                flags=re.I)

            for v in link_elements:
                m = exp_ver.match(v.attrs['href'].rstrip('/'))

                if m:
                    version = m.group('version')
                    vhlp.append(version)

                    # Installer
                    # if download_link_elements:
                    #     for v in download_link_elements:
                    #         if v.attrs['href'].endswith('Win.exe'):
                    #             vhlp.add_download_url(v.attrs['href'])

                    # Extension Pack
                    # if extension_pack_link_elements:
                    #     for v in extension_pack_link_elements:
                    #         if v.attrs['href'].endswith('.vbox-extpack'):
                    #             vhlp.add_download_url(v.attrs['href'])

                    # SDK
                    # if sdk_link_elements:
                    #     for v in sdk_link_elements:
                    #         vhlp.add_download_url(v.attrs['href'])

            latest_version = vhlp.latest_version
            # print(latest_version)

            url, status, _, data_s = await self.request('GET', f'https://download.virtualbox.org/virtualbox/{latest_version.version}/',
                                                        is_json=False)

            soup = BeautifulSoup(data_s, 'html5lib')

            link_elements = soup.select('pre > a[href]')

            for v in link_elements:
                href = v.attrs['href']

                if isinstance(href, str):
                    if href.endswith('.exe') or href.endswith('.zip') or href.endswith('.vbox-extpack'):
                        vhlp.add_download_url(urljoin(url.__str__(), href))

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
