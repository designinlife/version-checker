from typing import List

import arrow

from app.core.config import AppSettingSoftItem
from app.core.version import VersionSummary
from . import UrlMakerBase


class UrlMaker(UrlMakerBase):
    def build_links(self, soft: AppSettingSoftItem, version_summary: VersionSummary, urls: List[str]) -> List[str]:
        r = []

        latest = version_summary.latest
        file_ver_str = '%d%d%02d%02d' % (latest.major, latest.minor, latest.patch, 0)
        year = arrow.now().format('YYYY')

        r.append(f'https://www.sqlite.org/{year}/sqlite-amalgamation-{file_ver_str}.zip')
        r.append(f'https://www.sqlite.org/{year}/sqlite-autoconf-{file_ver_str}.tar.gz')
        r.append(f'https://www.sqlite.org/{year}/sqlite-doc-{file_ver_str}.zip')
        r.append(f'https://www.sqlite.org/{year}/sqlite-tools-linux-x64-{file_ver_str}.zip')
        r.append(f'https://www.sqlite.org/{year}/sqlite-dll-win-x64-{file_ver_str}.zip')
        r.append(f'https://www.sqlite.org/{year}/sqlite-tools-win-x64-{file_ver_str}.zip')

        return r
