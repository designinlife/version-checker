from asyncio import Semaphore

from loguru import logger

from app.core.config import DartSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: DartSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_r = await self.request('GET',
                                                      'https://storage.googleapis.com/storage/v1/b/dart-archive/o',
                                                      params={'delimiter': '/', 'prefix': 'channels/stable/release/',
                                                              'alt': 'json'},
                                                      is_json=True)

            if isinstance(data_r, dict) and 'prefixes' in data_r:
                for v in data_r['prefixes']:
                    vhlp.append(str(v).removeprefix('channels/stable/release/').rstrip('/'))

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
