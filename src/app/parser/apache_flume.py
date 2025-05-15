from asyncio import Semaphore

from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import ApacheFlumeSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: ApacheFlumeSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET', 'https://flume.apache.org/releases/index.html',
                                                      is_json=False)

            # Analyzing HTML text data.
            soup = BeautifulSoup(data_s, 'html5lib')

            latest_a_element = soup.select_one('#releases > p:nth-child(3) > a')
            other_a_elements = soup.select('#releases > div:nth-child(6) > ul > li > a')

            vhlp.append(latest_a_element.attrs['href'].removesuffix('.html'))

            for v in other_a_elements:
                if v:
                    vhlp.append(v.attrs['href'].removesuffix('.html'))

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
