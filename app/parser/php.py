from loguru import logger

from app.core.config import AppSettingSoftItem
from app.core.version import VersionParser
from app.inspect.parser import Parser
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    all_versions = []

    # Make an HTTP request.
    for major in item.major:
        url, http_status_code, _, data_r = await assist.get(f'https://www.php.net/releases/index.php?json&max=-1&version={major}', is_json=True)

        for k, _ in data_r.items():
            all_versions.append(k)

    vpsr = VersionParser(pattern=item.tag_pattern)

    dict_versions = vpsr.semver_split(all_versions)

    for m, n in dict_versions.items():
        latest_version = vpsr.latest(n)
        download_links = Parser.create_download_links(latest_version, item.download_urls)

        logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
        logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

        # Output JSON file.
        await assist.create(name=f'{item.name}-{m}',
                            url='https://www.php.net/',
                            version=latest_version,
                            all_versions=n,
                            download_links=download_links)
