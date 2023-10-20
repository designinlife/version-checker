from bs4 import BeautifulSoup

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Make an HTTP request.
        url, http_status_code, _, data_s = await assist.get('https://flume.apache.org/releases/index.html')

        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=item.tag_pattern, download_urls=item.download_urls)

        # Analyzing HTML text data.
        soup = BeautifulSoup(data_s, 'html5lib')

        latest_a_element = soup.select_one('#releases > p:nth-child(3) > a')
        other_a_elements = soup.select('#releases > div:nth-child(6) > ul > li > a')

        vhlp.add(latest_a_element.attrs['href'].removesuffix('.html'))

        for v in other_a_elements:
            if v:
                vhlp.add(v.attrs['href'].removesuffix('.html'))

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url='https://flume.apache.org/',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
