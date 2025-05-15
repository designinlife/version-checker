from abc import ABCMeta, abstractmethod
from typing import List

from app.core.config import AppSettingSoftItem
from app.core.config import Configuration
from app.core.version import VersionSummary


class UrlMakerBase(metaclass=ABCMeta):
    def __init__(self, cfg: Configuration):
        self.cfg = cfg

    @abstractmethod
    def build_links(self, soft: AppSettingSoftItem, version_summary: VersionSummary, urls: List[str]) -> List[str]:
        ...
