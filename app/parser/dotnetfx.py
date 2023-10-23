from bs4 import BeautifulSoup

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^\.NET Framework (?P<version>(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<patch>\d+))?)$',
                             download_urls=item.download_urls)

        # Make an HTTP request.
        url, http_status_code, _, data_s = await assist.get('https://dotnet.microsoft.com/en-us/download/dotnet-framework')

        soup = BeautifulSoup(data_s, 'html5lib')
        elements = soup.select('#supported-versions-table > div > table > tbody > tr td:nth-of-type(1)')

        for element in elements:
            vhlp.add(element.text.strip())

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://dotnet.microsoft.com/en-us/download/dotnet-framework',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
