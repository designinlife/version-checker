import re

from bs4 import BeautifulSoup

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    # Create VersionHelper instance.
    vhlp = VersionHelper(pattern=item.tag_pattern, download_urls=item.download_urls)

    # Make an HTTP request.
    url, http_status_code, _, data_s = await assist.get('https://rubychangelog.com/versions-latest/')

    soup = BeautifulSoup(data_s, 'html5lib')

    all_elements = soup.select('body > div.md-container > main > div > div.md-sidebar.md-sidebar--secondary > div > div > nav > ul > li > a')

    exp = re.compile(r'^Ruby (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.?(?P<patch>\d+)?)$')

    for v in all_elements:
        m = exp.match(v.text.strip())

        if m:
            vhlp.add(m.group('version'))

    # Perform actions such as sorting.
    vhlp.done()

    # Output JSON file.
    await assist.create(name=item.name,
                        url='https://www.ruby-lang.org/en/downloads/',
                        version=vhlp.latest,
                        all_versions=vhlp.versions,
                        download_links=vhlp.download_links)
