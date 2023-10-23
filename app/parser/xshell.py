import json

from bs4 import BeautifulSoup

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^Xshell (?P<version>(?P<major>\d+) Build (?P<build>\d+))(?:.+)$',
                             download_urls=item.download_urls, use_semver=False)

        # Make an HTTP request.
        url, http_status_code, _, data_s = await assist.get('https://update.netsarang.com/json/download/process.html', params={
            'md': 'getUpdateHistory',
            'language': '2',
            'productName': 'xshell-update-history',
        })
        data_r = json.loads(data_s)

        content = data_r['message']

        soup = BeautifulSoup(content, 'html5lib')
        elements = soup.select('dt.h4')

        for element in elements:
            vhlp.add(element.text.strip())

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://www.netsarang.com/en/xshell-download/',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
