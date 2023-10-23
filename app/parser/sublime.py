from bs4 import BeautifulSoup

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^Version: Build (?P<version>(?P<build>\d+))$',
                             download_urls=item.download_urls)

        # Make an HTTP request.
        url, http_status_code, _, data_s = await assist.get('https://www.sublimetext.com/download')

        soup = BeautifulSoup(data_s, 'html5lib')
        element = soup.select_one('div.downloads > p.latest')

        vhlp.add(element.text.strip())

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://www.sublimetext.com/',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
