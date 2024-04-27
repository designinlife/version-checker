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
            if 'patch' in version.groups and version.groups['patch'] == '0':
                r.append(v.format(version=f'{version.groups['major']}.{version.groups['minor']}'))
            else:
                r.append(v.format_map(defaultdict(str, **version.groups)))

        return r
