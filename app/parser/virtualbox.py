import re

from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import AppSettingSoftItem
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    all_versions = []
    download_links = []

    # Make an HTTP request.
    url, http_status_code, _, data_s = await assist.get('https://www.virtualbox.org/wiki/Downloads')

    soup = BeautifulSoup(data_s, 'html5lib')

    latest_element = soup.select_one('#wikipage > h3:nth-of-type(1)')
    download_link_elements = soup.select('#wikipage > ul:nth-of-type(1) > li > a[class=ext-link]')
    extension_pack_link_elements = soup.select('#wikipage > ul:nth-of-type(3) > li > a[class=ext-link]')
    sdk_link_elements = soup.select('#wikipage > ul:nth-of-type(4) > li > a[class=ext-link]')

    exp_ver = re.compile(r'^VirtualBox (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)) platform packages$', flags=re.I)

    m = exp_ver.match(latest_element.text.strip())

    if m:
        latest_version = m.group('version')
        all_versions.append(latest_version)

        # Installer
        if download_link_elements:
            for v in download_link_elements:
                download_links.append(v.attrs['href'])

        # Extension Pack
        if extension_pack_link_elements:
            for v in extension_pack_link_elements:
                download_links.append(v.attrs['href'])

        # SDK
        if sdk_link_elements:
            for v in sdk_link_elements:
                download_links.append(v.attrs['href'])

        # Output JSON file.
        await assist.create(name=item.name,
                            url='https://www.virtualbox.org/wiki/Downloads',
                            version=latest_version,
                            all_versions=all_versions,
                            download_links=download_links)
    else:
        logger.error(f'[{item.name}] Regular expression fails when matching latest version pattern.')
