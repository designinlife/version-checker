import os
import re
from pathlib import Path

import aiofiles
import aiohttp
import arrow
from loguru import logger

from app.core.config import AppSettingSoftItem, Configuration, OutputResult
from app.core.version import VersionParser
from app.inspect.parser import Parser


async def parse(cfg: Configuration, item: AppSettingSoftItem):
    # Sleep for the "sleep_for" seconds.
    # await asyncio.sleep(3)
    timeout = aiohttp.ClientTimeout(total=15)
    api_by = 'releases' if item.by_release else 'tags'

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
        async with session.get(f'https://api.github.com/repos/{item.repo}/{api_by}?per_page=100', headers=headers,
                               proxy=os.environ.get('PROXY')) as resp:
            logger.debug(f'{resp.url} | STATUS: {resp.status}')

            data_r = await resp.json()

            semver_versions = []
            commit_sha_arr = {}

            exp_r = re.compile(item.tag_pattern)

            for v in data_r:
                m = exp_r.match(v['name'])

                if m:
                    # if 'suffix' in m.groupdict() and m.group('suffix') is not None:
                    #     ver = '{}.{}.{}{}'.format(m.group('major'), m.group('minor'), m.group('patch'), m.group('suffix'))
                    # else:
                    #     ver = '{}.{}.{}'.format(m.group('major'), m.group('minor'), m.group('patch'))
                    ver = m.group('version')

                    if 'commit' in v:
                        commit_sha_arr[ver] = v['commit']['sha']
                    else:
                        commit_sha_arr[ver] = None

                    semver_versions.append(v['name'])

            vpsr = VersionParser(item.tag_pattern)

            if item.category:
                # 按 <major>.<minor> 规则将版本分类为字典对象, 例如 OpenSSL 的版本划分为: 1.0, 1.1, 3.0, 3.1, 3.2 ...
                dict_versions = vpsr.semver_split(semver_versions)

                for m, n in dict_versions.items():
                    latest_version = vpsr.latest(n)
                    download_links = Parser.create_download_links(latest_version, item.download_urls)

                    logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
                    logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

                    # 创建输出结果对象并写入 JSON 数据文件。
                    result = OutputResult(name=f'{item.name}-{m}', url=f'https://github.com/{item.repo}', latest=latest_version,
                                          versions=vpsr.clean(n),
                                          download_urls=download_links,
                                          created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                    output_path = Path(cfg.workdir).joinpath('data')

                    if not output_path.is_dir():
                        output_path.mkdir(parents=True, exist_ok=True)

                    async with aiofiles.open(output_path.joinpath(f'{item.name}-{m}.json'), 'w', encoding='utf-8') as f:
                        await f.write(result)

                    logger.info(f'<{item.name}-{m}> data information has been generated.')
            else:
                # latest_version = max(semver_versions, key=Version.parse)
                latest_version = vpsr.latest(semver_versions)
                download_links = Parser.create_download_links(latest_version, item.download_urls, item.ver_pattern)

                logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(semver_versions)}')
                logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

                # 创建输出结果对象并写入 JSON 数据文件。
                result = OutputResult(name=item.name, url=f'https://github.com/{item.repo}', latest=latest_version,
                                      versions=vpsr.clean(semver_versions),
                                      download_urls=download_links,
                                      created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                output_path = Path(cfg.workdir).joinpath('data')

                if not output_path.is_dir():
                    output_path.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(output_path.joinpath(f'{item.name}.json'), 'w', encoding='utf-8') as f:
                    await f.write(result)

                logger.info(f'<{item.name}> data information has been generated.')
