import re

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=item.tag_pattern, download_urls=item.download_urls)

        # Make an HTTP request.
        url, http_status_code, _, data_s = await assist.get('https://raw.githubusercontent.com/sonatype/docker-nexus3/main/Dockerfile')

        exp = re.compile(r'ARG NEXUS_VERSION=([0-9-.]+)')
        m = exp.findall(data_s)

        if isinstance(m, list) and len(m) > 0:
            vhlp.add(m[0])

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url='https://www.sonatype.com/products/sonatype-nexus-oss-download',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
