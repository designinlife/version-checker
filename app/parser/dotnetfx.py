from asyncio import Semaphore

from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import DotNetFxSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: DotNetFxSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET',
                                                      'https://dotnet.microsoft.com/en-us/download/dotnet-framework',
                                                      is_json=False)

            soup = BeautifulSoup(data_s, 'html5lib')
            elements = soup.select('#supported-versions-table > div > table > tbody > tr td:nth-of-type(1)')

            for element in elements:
                vhlp.append(element.text.strip())

            # Continue to crawling the offline package download URL.
            vlatest = vhlp.versions[0]

            suffixes = ('developer-pack-offline-installer', 'developer-pack-chs', 'offline-installer', 'chs')

            for suffix in suffixes:
                _, status, _, data_s = await self.request('GET',
                                                          'https://dotnet.microsoft.com/zh-cn/download'
                                                          '/dotnet-framework/thank-you'
                                                          f'/net{vlatest.major}{vlatest.minor}{vlatest.patch}-{suffix}',
                                                          is_json=False)

                if data_s:
                    soup = BeautifulSoup(data_s, 'html5lib')
                    element = soup.select_one(
                        'body > div.main-container > div.swim-container > div:nth-child(1) > div > p > a')
                    if element:
                        href = element.attrs['href']

                        if href and '/fwlink/?linkid=' in href:
                            vhlp.add_download_url(href)

                        logger.debug(f'.NET Framework {suffix} {vlatest.version}: {href}')

        logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

        if soft.split > 0:
            logger.debug(f'Split Versions: {vhlp.split_versions}')

        # Write data to file.
        await self.write(soft, vhlp.summary)
