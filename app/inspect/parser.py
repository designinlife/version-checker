import importlib
import re
from abc import ABC, abstractmethod
from typing import List

from app.core.config import AppSettingSoftItem, Configuration


class Parser(ABC):
    @staticmethod
    @abstractmethod
    def parse(cfg: Configuration, item: AppSettingSoftItem):
        pass

    @staticmethod
    async def create(name: str, cfg: Configuration, item: AppSettingSoftItem):
        module = importlib.import_module('app.parser.%s' % name.replace('-', '_'))
        await module.parse(cfg, item)

    @staticmethod
    def create_download_links(version: str, links: List[str]) -> List[str]:
        r = []

        exp = re.compile(r'^(?P<major>\d+)\.(?P<minor>\d+)(.*)$')
        m = exp.match(version)

        if m:
            for v in links:
                r.append(v.format(version=version, major=m.group('major'), minor=m.group('minor')))
        else:
            for v in links:
                r.append(v.format(version=version))

        return r
