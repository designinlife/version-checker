from loguru import logger

from app.core.config import AppSettingSoftItem
from app.core.version import VersionParser
from app.inspect.parser import Parser
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    all_versions = []

    # Make an HTTP request.
    url, http_status_code, _, data_r = await assist.get('https://go.dev/dl/?mode=json&include=all', is_json=True)

    for v in data_r:
        all_versions.append(v['version'])

    logger.debug(f'Go: {all_versions}')

    vpsr = VersionParser(pattern=r'^go(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$')

    dict_versions = vpsr.semver_split(all_versions)

    logger.debug(f'Go Split: {dict_versions}')

    for m, n in dict_versions.items():
        latest_version = vpsr.latest(n)
        download_links = Parser.create_download_links(latest_version, item.download_urls)

        logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
        logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

        # Output JSON file.
        await assist.create(name=f'{item.name}-{m}',
                            url='https://go.dev/dl/',
                            version=latest_version,
                            all_versions=n,
                            download_links=download_links)
