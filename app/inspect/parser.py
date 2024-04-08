import importlib

from loguru import logger

from app.core.config import AppSettingSoftItem
from app.parser import Assistant


class Parser:
    @staticmethod
    async def create(name: str, assistant: Assistant, item: AppSettingSoftItem):
        if item.disabled:
            logger.warning(f'Skipping {item.name}')
            return

        module = importlib.import_module('app.parser.%s' % name.replace('-', '_'))
        cls = getattr(module, 'Parser')
        await cls.parse(assistant, item)
