from asyncio import Semaphore
from typing import Mapping

from loguru import logger

from app.core.config import FirefoxSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: FirefoxSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        # See <https://wiki.mozilla.org/Release_Management/Product_details>

        async with sem:
            # Make an HTTP request.
            _, status, _, data_r = await self.request('GET', 'https://product-details.mozilla.org/1.0/firefox.json',
                                                      is_json=True)

            if isinstance(data_r, dict) and 'releases' in data_r and isinstance(data_r['releases'], Mapping):
                for k, v in data_r['releases'].items():
                    if v['product'] == 'firefox' and v['category'] == 'major':
                        vhlp.append(v['version'])

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
