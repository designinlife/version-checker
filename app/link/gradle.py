from typing import List

from app.core.config import AppSettingSoftItem
from app.core.version import VersionSummary
from . import UrlMakerBase


class UrlMaker(UrlMakerBase):
    def build_links(self, soft: AppSettingSoftItem, version_summary: VersionSummary, urls: List[str]) -> List[str]:
        r = []

        ver = version_summary.latest.version

        if version_summary.latest.patch == 0:
            ver = f'{version_summary.latest.major}.{version_summary.latest.minor}'

        r.append(f'https://services.gradle.org/distributions/gradle-{ver}-bin.zip')
        r.append(f'https://services.gradle.org/distributions/gradle-{ver}-all.zip')
        r.append(f'https://services.gradle.org/distributions/gradle-{ver}-src.zip')
        r.append(f'https://services.gradle.org/distributions/gradle-{ver}-docs.zip')

        return r
