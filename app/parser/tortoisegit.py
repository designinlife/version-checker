import re

from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import AppSettingSoftItem
from . import Assistant

TORTOISE_GIT_DOWNLOAD_BASE_URL = 'https://download.tortoisegit.org/tgit'


async def parse(assist: Assistant, item: AppSettingSoftItem):
    all_versions = []
    download_links = []

    # Make an HTTP request.
    url, http_status_code, _, data_s = await assist.get('https://tortoisegit.org/download/')

    soup = BeautifulSoup(data_s, 'html5lib')

    latest_element = soup.select_one('div[class="wrap_content contentpage"] > p:nth-of-type(1)')
    latest_exp = re.compile(r'^The current stable version is: (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(\.(?P<suffix>\d+))?)$')

    m = latest_exp.match(latest_element.text)
    if m:
        latest_version = m.group('version')
        all_versions.append(latest_version)

        ver_split = latest_version.split('.')
        ver_split_len = len(ver_split)

        if ver_split_len > 3:
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}/TortoiseGit-{latest_version}-32bit.msi')
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}/TortoiseGit-{latest_version}-64bit.msi')
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}/TortoiseGit-{latest_version}-arm64.msi')
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}/TortoiseGit-LanguagePack-{latest_version}-32bit-zh_CN.msi')
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}/TortoiseGit-LanguagePack-{latest_version}-64bit-zh_CN.msi')
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}/TortoiseGit-LanguagePack-{latest_version}-arm64-zh_CN.msi')
        elif ver_split_len == 3:
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}.0/TortoiseGit-{latest_version}.0-32bit.msi')
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}.0/TortoiseGit-{latest_version}.0-64bit.msi')
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}.0/TortoiseGit-{latest_version}.0-arm64.msi')
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}.0/TortoiseGit-LanguagePack-{latest_version}.0-32bit-zh_CN.msi')
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}.0/TortoiseGit-LanguagePack-{latest_version}.0-64bit-zh_CN.msi')
            download_links.append(f'{TORTOISE_GIT_DOWNLOAD_BASE_URL}/{latest_version}.0/TortoiseGit-LanguagePack-{latest_version}.0-arm64-zh_CN.msi')
        else:
            raise ValueError(f'[{item.name}] TORTOISEGIT VERSION NUMBER IS NOT STANDARDIZED. ({latest_version})')

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else f'https://sourceforge.net/projects/{item.name}/',
                            version=latest_version,
                            all_versions=all_versions,
                            download_links=download_links)
    else:
        logger.error(f'[{item.name}] Regular expression fails when matching latest version pattern.')
