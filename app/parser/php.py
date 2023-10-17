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
        for major in item.major:
            async with session.get(f'https://www.php.net/releases/index.php?json&max=-1&version={major}', proxy=os.environ.get('PROXY')) as resp:
                logger.debug(f'{resp.url} | STATUS: {resp.status}')

                data_r = await resp.json()

                for k, _ in data_r.items():
                    semver_versions.append(k)

    logger.debug(f'PHP: {semver_versions}')

    vpsr = VersionParser(pattern=item.tag_pattern)

    dict_versions = vpsr.semver_split(semver_versions)

    logger.debug(f'PHP Split: {dict_versions}')

    for m, n in dict_versions.items():
        latest_version = vpsr.latest(n)
        download_links = Parser.create_download_links(latest_version, item.download_urls)

        logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
        logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

        # 创建输出结果对象并写入 JSON 数据文件。
        result = OutputResult(name=f'{item.name}-{m}', url=f'https://github.com/php/php-src', latest=latest_version,
                              versions=n,
                              download_urls=download_links,
                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

        output_path = Path(cfg.workdir).joinpath('data')

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(output_path.joinpath(f'{item.name}-{m}.json'), 'w', encoding='utf-8') as f:
            await f.write(result)

        logger.info(f'<{item.name}-{m}> data information has been generated.')
