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
            r.append(f'{v.format(version=version.semver)}#composer-{version.semver}.phar')

        return r
