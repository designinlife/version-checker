import os
from asyncio import Semaphore
from pathlib import Path
from typing import List, Optional

import aiofiles
import arrow
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import DockerHubSoftware
from . import Base


class RepositoryTagItem(BaseModel):
    name: str
    full_size: int
    v2: bool
    tag_last_pushed: str


class RepositoryTags(BaseModel):
    results: List[RepositoryTagItem] = Field(default_factory=list)


class RatelimitHeader(BaseModel):
    rate_limit: Optional[str] = Field(alias='x-ratelimit-limit')
    rate_remaining: Optional[str] = Field(alias='x-ratelimit-remaining')
    rate_reset: Optional[str] = Field(alias='x-ratelimit-reset')


class OutputResult(BaseModel):
    name: str
    repo: str
    tags: List[RepositoryTagItem] = Field(default_factory=list)
    created_time: str


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: DockerHubSoftware):
        logger.debug(f'Repository: {soft.repo} ({soft.parser})')

        # 使用 arrow 解析 Tag 推送时间并转换为国内时间
        # arrow.get(a, "YYYY-MM-DDTHH:mm:ss.SSSSSSZ", tzinfo='UTC').to(tz='Asia/Shanghai')

        repo_parts = soft.repo.split('/', 1)

        async with sem:
            # Make an HTTP request.
            _, status, headers, data_r = await self.request('GET', f'https://hub.docker.com/v2/namespaces/{repo_parts[0]}/repositories/{repo_parts[1]}/tags',
                                                            params={'status': 'active', 'page': '1', 'page_size': '100'},
                                                            is_json=True)

            if status == 200:
                data = RepositoryTags.model_validate(data_r)
                data_header = RatelimitHeader.model_validate(headers)

                # Write data to file.
                await self.write_data(soft, data.results, data_header)
            else:
                data_header = RatelimitHeader.model_validate(headers)

                logger.error(f'[Docker Hub][{soft.repo}] HTTP STATUS {status} ERROR. '
                             f'({data_header.rate_remaining}/{data_header.rate_limit}, '
                             f'{arrow.get(int(data_header.rate_reset)).format('YYYY-MM-DD HH:mm:ss')})')

    async def write_data(self, soft: DockerHubSoftware, items: List[RepositoryTagItem], header: RatelimitHeader):
        output_subdir = os.environ.get('OUTPUT_DATA_DIR', 'data')
        output_path = Path(self.cfg.workdir).joinpath(output_subdir)

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        soft_name = f'docker-{soft.repo.replace('/', '-')}'

        result = OutputResult(name=soft_name, repo=soft.repo, tags=items,
                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

        async with aiofiles.open(output_path.joinpath(f'{soft_name}.json'), 'w', encoding='utf-8') as f:
            await f.write(result)

        logger.info(f'<\033[1;32m{soft.repo}\033[0m> done. '
                    f'({header.rate_remaining}/{header.rate_limit}, {arrow.get(int(header.rate_reset)).format('YYYY-MM-DD HH:mm:ss')})')
