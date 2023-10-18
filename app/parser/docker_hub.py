import os
from pathlib import Path

import aiofiles
import aiohttp
import arrow
from loguru import logger

from app.core.config import AppSettingSoftItem, Configuration, OutputResult
from app.core.version import VersionParser
from app.inspect.parser import Parser


async def parse(cfg: Configuration, item: AppSettingSoftItem):
    semver_versions = []

    ns, name = item.repo.split('/')

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f'https://hub.docker.com/v2/namespaces/{ns}/repositories/{name}/tags?page_size=100',
                               proxy=os.environ.get('PROXY')) as resp:
            logger.debug(f'{resp.url} | STATUS: {resp.status}')

            data_r = await resp.json()

            if 'results' in data_r and isinstance(data_r['results'], list):
                vpsr = VersionParser(pattern=item.tag_pattern)

                for v in data_r['results']:
                    semver_versions.append(v['name'])

                semver_versions = vpsr.clean(semver_versions)

    if semver_versions:
        latest_version = vpsr.latest(semver_versions)
        download_links = Parser.create_download_links(latest_version, item.download_urls)

        # 创建输出结果对象并写入 JSON 数据文件。
        result = OutputResult(name=f'{item.name}', url=item.url if item.url else 'https://hub.docker.com/', latest=latest_version,
                              versions=semver_versions,
                              download_urls=download_links,
                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

        output_path = Path(cfg.workdir).joinpath('data')

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(output_path.joinpath(f'{item.name}.json'), 'w', encoding='utf-8') as f:
            await f.write(result)

        logger.info(f'<{item.name}> data information has been generated.')
