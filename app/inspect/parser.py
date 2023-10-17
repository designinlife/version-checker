import importlib
import re
from typing import List

from app.core.config import AppSettingSoftItem, Configuration


class Parser:
    @staticmethod
    async def create(name: str, cfg: Configuration, item: AppSettingSoftItem):
        module = importlib.import_module('app.parser.%s' % name.replace('-', '_'))
        await module.parse(cfg, item)

    @staticmethod
    def create_download_links(version: str, links: List[str], pattern: str = None) -> List[str]:
        r = []

        if pattern:
            exp = re.compile(pattern)
        else:
            exp = re.compile(r'^(?P<major>\d+)\.(?P<minor>\d+)(.*)$')

        m = exp.match(version)

        if m:
            grpdict = m.groupdict()

            for v in links:
                # r.append(v.format(version=version, major=m.group('major'), minor=m.group('minor')))
                r.append(v.format(**grpdict))
        else:
            for v in links:
                r.append(v.format(version=version))

        return r
