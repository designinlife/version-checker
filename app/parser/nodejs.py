from loguru import logger

from app.core.config import AppSettingSoftItem
from app.core.version import VersionParser
from app.inspect.parser import Parser
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    semver_versions = []

    # Make an HTTP request.
    url, http_status_code, _, data_r = await assist.get('https://nodejs.org/download/release/index.json', is_json=True)

    for v in data_r:
        if 'lts' in v and v['lts'] is not False:
            semver_versions.append(v['version'])

    logger.debug(f'nodejs: {semver_versions}')

    vpsr = VersionParser(pattern=r'^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$')

    latest_version = vpsr.latest(semver_versions)
    download_links = Parser.create_download_links(latest_version, item.download_urls)

    logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(semver_versions)}')
    logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

    # Output JSON file.
    await assist.create(name=item.name,
                        url='https://nodejs.org/',
                        version=latest_version,
                        all_versions=semver_versions,
                        download_links=download_links)
