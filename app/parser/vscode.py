import re

from bs4 import BeautifulSoup

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$',
                             download_urls=item.download_urls)

        # Make an HTTP request.
        url, http_status_code, _, data_s = await assist.get('https://code.visualstudio.com/updates')

        soup = BeautifulSoup(data_s, 'html5lib')
        elements = soup.select('#main-content > div > div > div:nth-of-type(3) > p > strong')

        exp_1 = re.compile(r'^Update\s+(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$')

        for element in elements:
            m = exp_1.match(element.text.strip())

            if m:
                vhlp.add(m.group('version'))

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://code.visualstudio.com/',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
