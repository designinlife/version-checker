from loguru import logger

from app.core.config import AppSettingSoftItem
from app.core.version import VersionParser
from app.inspect.parser import Parser
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    semver_versions = []

    ns, name = item.repo.split('/')

    # Make an HTTP request.
    url, http_status_code, _, data_r = await assist.get(f'https://hub.docker.com/v2/namespaces/{ns}/repositories/{name}/tags',
                                                        params={'page_size': '100'},
                                                        is_json=True)

    if 'results' in data_r and isinstance(data_r['results'], list):
        vpsr = VersionParser(pattern=item.tag_pattern)

        for v in data_r['results']:
            if vpsr.is_match(v['name']):
                semver_versions.append(v['name'])

        if item.category:
            dict_versions = vpsr.semver_split(semver_versions, only_major=item.category_by_major)

            for m, n in dict_versions.items():
                latest_version = vpsr.latest(n)
                download_links = Parser.create_download_links(latest_version, item.download_urls)

                logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
                logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

                # Output JSON file.
                await assist.create(name=f'{item.name}-{m}',
                                    url=item.url if item.url else 'https://hub.docker.com/',
                                    version=latest_version,
                                    all_versions=vpsr.clean(n),
                                    download_links=download_links)
        else:
            if semver_versions:
                latest_version = vpsr.latest(semver_versions)
                download_links = Parser.create_download_links(latest_version, item.download_urls)

                # Output JSON file.
                await assist.create(name=item.name,
                                    url=item.url if item.url else 'https://hub.docker.com/',
                                    version=latest_version,
                                    all_versions=vpsr.clean(semver_versions),
                                    download_links=download_links)
