import os
import re

from loguru import logger

from app.core.config import AppSettingSoftItem
from app.core.version import VersionParser
from app.inspect.parser import Parser
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
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

    # Make an HTTP request.
    url, http_status_code, _, data_r = await assist.get(f'https://api.github.com/repos/{item.repo}/{api_by}',
                                                        params={'per_page': '100'},
                                                        headers=headers,
                                                        is_json=True)

    all_versions = []
    commit_sha_arr = {}

    exp_r = re.compile(item.tag_pattern)

    for v in data_r:
        m = exp_r.match(v['name'])

        if m:
            ver = m.group('version')

            if 'commit' in v:
                commit_sha_arr[ver] = v['commit']['sha']
            else:
                commit_sha_arr[ver] = None

            all_versions.append(v['name'])

    vpsr = VersionParser(item.tag_pattern)

    if item.category:
        # 按 <major>.<minor> 规则将版本分类为字典对象, 例如 OpenSSL 的版本划分为: 1.0, 1.1, 3.0, 3.1, 3.2 ...
        dict_versions = vpsr.split(all_versions)

        for m, n in dict_versions.items():
            latest_version = vpsr.latest(n)
            download_links = Parser.create_download_links(latest_version, item.download_urls)

            logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
            logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

            # Output JSON file.
            await assist.create(name=item.name,
                                url=f'https://github.com/{item.repo}',
                                version=latest_version,
                                all_versions=vpsr.clean(n),
                                download_links=download_links)
    else:
        latest_version = vpsr.latest(all_versions)
        download_links = Parser.create_download_links(latest_version, item.download_urls, item.ver_pattern)

        logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(all_versions)}')
        logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

        # Output JSON file.
        await assist.create(name=item.name,
                            url=f'https://github.com/{item.repo}',
                            version=latest_version,
                            all_versions=vpsr.clean(all_versions),
                            download_links=download_links)
