import os
from asyncio import Semaphore
from pathlib import Path
from typing import List, Mapping, Optional

import aiofiles
import arrow
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import DockerHubSoftware
from app.core.version import VersionHelper, VersionSummary
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
    suffix: List[str] = Field(default_factory=list)
    fixed_tags: List[str] = Field(default_factory=list)
    latest_tags: List[str] = Field(default_factory=list)
    created_time: str


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: DockerHubSoftware):
        logger.debug(f'Repository: {soft.repo} ({soft.parser})')

        # 使用 arrow 解析 Tag 推送时间并转换为国内时间
        # arrow.get(a, "YYYY-MM-DDTHH:mm:ss.SSSSSSZ", tzinfo='UTC').to(tz='Asia/Shanghai')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=[])

        repo_parts = soft.repo.split('/', 1)

        async with sem:
            # Make an HTTP request.
            _, status, headers, data_r = await self.request('GET', f'https://hub.docker.com/v2/namespaces/{repo_parts[0]}/repositories/{repo_parts[1]}/tags',
                                                            params={'status': 'active', 'page': '1', 'page_size': '100'},
                                                            is_json=True)

            if status == 200:
                data = RepositoryTags.model_validate(data_r)
                data_header = RatelimitHeader.model_validate(headers)

                for v in data.results:
                    vhlp.append(v.name)

                # Write data to file.
                await self.write_data(soft, data.results, data_header, vhlp)
            else:
                data_header = RatelimitHeader.model_validate(headers)

                logger.error(f'[Docker Hub][{soft.repo}] HTTP STATUS {status} ERROR. '
                             f'({data_header.rate_remaining}/{data_header.rate_limit}, '
                             f'{arrow.get(int(data_header.rate_reset)).format('YYYY-MM-DD HH:mm:ss')})')

    async def write_data(self, soft: DockerHubSoftware, items: List[RepositoryTagItem], header: RatelimitHeader,
                         vhlp: VersionHelper):
        output_subdir = os.environ.get('OUTPUT_DATA_DIR', 'data')
        output_path = Path(self.cfg.workdir).joinpath(output_subdir)

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        # 标签过滤
        tags = []
        latests = []
        suffix = []

        for v in items:
            if vhlp.exists(v.name):
                tags.append(v)

        version_summary = vhlp.summary

        if isinstance(version_summary, Mapping):
            for k, v in version_summary.items():
                if isinstance(v, VersionSummary):
                    latests.append(v.latest.version)
        elif isinstance(version_summary, VersionSummary):
            latests.append(version_summary.latest.version)

        def is_latest_exists(sfix: str) -> bool:
            for vv in latests:
                fv = f'{vv}{sfix}'

                if vhlp.raw_exists(fv):
                    return True

            return False

        # 收集版本 Tag 可用的后缀
        for v in vhlp.raw_versions:
            if v.other and v.other not in suffix and is_latest_exists(v.other):
                suffix.append(v.other)

        soft_name = f'docker-{soft.repo.replace('/', '-')}'

        result = OutputResult(name=soft_name, repo=soft.repo, tags=tags, latest_tags=latests, suffix=suffix, fixed_tags=soft.fixed_tags,
                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

        async with aiofiles.open(output_path.joinpath(f'{soft_name}.json'), 'w', encoding='utf-8') as f:
            await f.write(result)

        logger.info(f'<\033[1;32m{soft.repo}\033[0m> done. '
                    f'({header.rate_remaining}/{header.rate_limit}, {arrow.get(int(header.rate_reset)).format('YYYY-MM-DD HH:mm:ss')})')
