from typing import List

from app.core.config import AppSettingSoftItem
from app.core.version import VersionSummary
from . import UrlMakerBase


class UrlMaker(UrlMakerBase):
    def build_links(self, soft: AppSettingSoftItem, version_summary: VersionSummary, urls: List[str]) -> List[str]:
        r = []

        if version_summary.latest.major == 1 and version_summary.latest.minor == 1:
            r.append(
                f'https://www.openssl.org/source/old/{version_summary.latest.major}.{version_summary.latest.minor}'
                f'.{version_summary.latest.patch}/openssl-{version_summary.latest.major}.{version_summary.latest.minor}'
                f'.{version_summary.latest.patch}{version_summary.latest.letter}.tar.gz')
        else:
            r.append(f'https://www.openssl.org/source/openssl-{version_summary.latest.major}'
                     f'.{version_summary.latest.minor}.{version_summary.latest.patch}.tar.gz')

        return r
