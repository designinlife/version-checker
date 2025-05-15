from asyncio import Semaphore

from loguru import logger

from app.core.config import PhpSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: PhpSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            for major in soft.major:
                _, status, _, data_r = await self.request('GET',
                                                          f'https://www.php.net/releases/index.php?json&max=-1'
                                                          f'&version={major}',
                                                          is_json=True)

                for k, _ in data_r.items():
                    vhlp.append(k)

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
