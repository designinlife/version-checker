from asyncio import Semaphore
from typing import List

from loguru import logger
from pydantic import BaseModel, TypeAdapter

from app.core.config import GoSoftware
from app.core.version import VersionHelper
from . import Base


class File(BaseModel):
    filename: str
    os: str
    arch: str
    version: str
    sha256: str
    size: int
    kind: str


class DataItem(BaseModel):
    version: str
    stable: bool
    files: List[File]


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: GoSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        async with sem:
            # Make an HTTP request.
            _, status, _, data_r = await self.request('GET', 'https://go.dev/dl/?mode=json&include=all', is_json=True)

            ta = TypeAdapter(List[DataItem])
            data = ta.validate_python(data_r)

            vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

            for v in data:
                # 仅支持 Stable 版本号 ...
                if v.stable:
                    vhlp.append(v.version)

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
