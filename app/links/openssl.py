from collections import defaultdict
from typing import List

from app.core.version import Version


class LinkAssembler:
    def __init__(self):
        ...

    @staticmethod
    def assemble(version: Version, download_urls: List[str]) -> List[str]:
        r = []

        for v in download_urls:
            if 'major' in version.groups and version.groups['major'] == '1':
                r.append(f'https://www.openssl.org/source/old/openssl-{version.groups['version']}.tar.gz')
            else:
                r.append(v.format_map(defaultdict(str, **version.groups)))

        return r
