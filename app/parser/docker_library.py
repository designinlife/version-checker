import json
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

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f'https://raw.githubusercontent.com/docker-library/{item.name}/master/versions.json',
                               proxy=os.environ.get('PROXY')) as resp:
            logger.debug(f'{resp.url} | STATUS: {resp.status}')

            data_s = await resp.text()
            data_r = json.loads(data_s)

            for _, v in data_r.items():
                if v:
                    semver_versions.append(v['version'])

    logger.debug(f'docker-library: {semver_versions}')

    vpsr = VersionParser(pattern=item.tag_pattern)

    dict_versions = vpsr.semver_split(semver_versions, only_major=item.category_by_major)

    logger.debug(f'docker-library Split: {dict_versions}')

    for m, n in dict_versions.items():
        latest_version = vpsr.latest(n)
        download_links = Parser.create_download_links(latest_version, item.download_urls)

        logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
        logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

        # 创建输出结果对象并写入 JSON 数据文件。
        result = OutputResult(name=f'{item.name}-{m}', url=item.url if item.url else 'https://github.com/', latest=latest_version,
                              versions=n,
                              download_urls=download_links,
                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

        output_path = Path(cfg.workdir).joinpath('data')

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(output_path.joinpath(f'{item.name}-{m}.json'), 'w', encoding='utf-8') as f:
            await f.write(result)

        logger.info(f'<{item.name}-{m}> data information has been generated.')
