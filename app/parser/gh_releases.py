import os
from pathlib import Path

import aiofiles
import aiohttp
import arrow
from loguru import logger

from app.core.config import Configuration, AppSettingSoftItem, OutputResult


async def parse(cfg: Configuration, item: AppSettingSoftItem):
    timeout = aiohttp.ClientTimeout(total=15)

    github_token = os.environ.get("GITHUB_TOKEN")

    headers = {}

    if github_token:
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {github_token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }

        logger.debug('Using GITHUB_TOKEN env.')

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f'https://api.github.com/repos/{item.repo}/releases?per_page=100', headers=headers,
                               proxy=os.environ.get('PROXY')) as resp:
            logger.debug(f'{resp.url} | STATUS: {resp.status}')

            data_r = await resp.json()

            if len(data_r) > 0:
                data = data_r[0]

                download_links = []

                for v2 in data['assets']:
                    download_links.append(v2['browser_download_url'])

                # 创建输出结果对象并写入 JSON 数据文件。
                result = OutputResult(name=f'{item.name}', url=f'https://github.com/{item.repo}', latest=data['name'],
                                      versions=[data['name']],
                                      download_urls=download_links,
                                      created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                output_path = Path(cfg.workdir).joinpath('data')

                if not output_path.is_dir():
                    output_path.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(output_path.joinpath(f'{item.name}.json'), 'w', encoding='utf-8') as f:
                    await f.write(result)

                logger.info(f'<{item.name}> data information has been generated.')
