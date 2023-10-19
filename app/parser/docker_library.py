import json

from loguru import logger

from app.core.config import AppSettingSoftItem
from app.core.version import VersionParser
from app.inspect.parser import Parser
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    all_versions = []

    # Make an HTTP request.
    url, http_status_code, _, data_s = await assist.get(f'https://raw.githubusercontent.com/docker-library/{item.name}/master/versions.json')

    data_r = json.loads(data_s)

    for _, v in data_r.items():
        if v:
            all_versions.append(v['version'])

    logger.debug(f'docker-library: {all_versions}')

    vpsr = VersionParser(pattern=item.tag_pattern)

    dict_versions = vpsr.semver_split(all_versions, only_major=item.category_by_major)

    logger.debug(f'docker-library Split: {dict_versions}')

    for m, n in dict_versions.items():
        latest_version = vpsr.latest(n)
        download_links = Parser.create_download_links(latest_version, item.download_urls)

        logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
        logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

        # Output JSON file.
        await assist.create(name=f'{item.name}-{m}',
                            url=item.url if item.url else 'https://github.com/',
                            version=latest_version,
                            all_versions=n,
                            download_links=download_links)
