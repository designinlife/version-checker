from asyncio import Semaphore

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
            _, status, _, data_r = await self.request('GET', 'https://nodejs.org/download/release/index.json',
                                                      is_json=True)

            for v in data_r:
                if 'lts' in v and v['lts'] is not False:
                    vhlp.append(v['version'])

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
