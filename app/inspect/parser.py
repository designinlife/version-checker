import importlib

from app.core.config import AppSettingSoftItem
from app.parser import Assistant


class Parser:
    @staticmethod
    async def create(name: str, assistant: Assistant, item: AppSettingSoftItem):
        module = importlib.import_module('app.parser.%s' % name.replace('-', '_'))
        cls = getattr(module, 'Parser')
        await cls.parse(assistant, item)
