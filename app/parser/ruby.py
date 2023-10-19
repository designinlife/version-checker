import re

from bs4 import BeautifulSoup

from app.core.config import AppSettingSoftItem
from app.core.version import VersionParser
from app.inspect.parser import Parser
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    all_versions = []

    # Make an HTTP request.
    url, http_status_code, _, data_s = await assist.get('https://rubychangelog.com/versions-latest/')

    soup = BeautifulSoup(data_s, 'html.parser')

    all_elements = soup.select('body > div.md-container > main > div > div.md-sidebar.md-sidebar--secondary > div > div > nav > ul > li > a')

    exp = re.compile(r'^Ruby (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.?(?P<patch>\d+)?)$')

    for v in all_elements:
        m = exp.match(v.text.strip())

        if m:
            all_versions.append(m.group('version'))

    vpsr = VersionParser(pattern=r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.?(?P<patch>\d+)?)$')

    latest_version = vpsr.latest(all_versions)
    download_links = Parser.create_download_links(latest_version, item.download_urls)

    # Output JSON file.
    await assist.create(name=item.name,
                        url='https://www.ruby-lang.org/en/downloads/',
                        version=latest_version,
                        all_versions=all_versions,
                        download_links=download_links)
