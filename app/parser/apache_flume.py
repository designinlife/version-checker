from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import AppSettingSoftItem
from app.core.version import VersionParser
from app.inspect.parser import Parser
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    all_versions = []

    # Make an HTTP request.
    url, http_status_code, _, data_s = await assist.get('https://flume.apache.org/releases/index.html')

    soup = BeautifulSoup(data_s, 'html.parser')

    latest_a_element = soup.select_one('#releases > p:nth-child(3) > a')
    other_a_elements = soup.select('#releases > div:nth-child(6) > ul > li > a')

    all_versions.append(latest_a_element.attrs['href'].removesuffix('.html'))

    for v in other_a_elements:
        if v:
            all_versions.append(v.attrs['href'].removesuffix('.html'))

    logger.debug(f'flume: {all_versions}')

    vpsr = VersionParser(pattern=r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$')

    latest_version = vpsr.latest(all_versions)
    download_links = Parser.create_download_links(latest_version, item.download_urls)

    logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(all_versions)}')
    logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

    # Output JSON file.
    await assist.create(name=item.name,
                        url='https://flume.apache.org/',
                        version=latest_version,
                        all_versions=all_versions,
                        download_links=download_links)
