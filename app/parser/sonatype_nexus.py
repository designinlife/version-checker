import re

from app.core.config import AppSettingSoftItem
from app.core.version import VersionParser
from app.inspect.parser import Parser
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    all_versions = []

    # Make an HTTP request.
    url, http_status_code, _, data_s = await assist.get('https://raw.githubusercontent.com/sonatype/docker-nexus3/main/Dockerfile')

    exp = re.compile(r'ARG NEXUS_VERSION=([0-9-.]+)')
    m = exp.findall(data_s)
    if isinstance(m, list) and len(m) > 0:
        all_versions.append(m[0])

    if all_versions:
        vpsr = VersionParser(pattern=r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)-(\d+))$')

        latest_version = vpsr.latest(all_versions)
        download_links = Parser.create_download_links(latest_version, item.download_urls)

        # Output JSON file.
        await assist.create(name=item.name,
                            url='https://www.sonatype.com/products/sonatype-nexus-oss-download',
                            version=latest_version,
                            all_versions=all_versions,
                            download_links=download_links)
