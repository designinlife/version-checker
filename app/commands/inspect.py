import asyncio
import importlib
from typing import Optional

import click
from click.core import Context
from loguru import logger

from app.commands.combine import cli as cli_combine
from app.core.click import ClickStdOption
from app.core.config import Configuration
from app.parser import Base as BaseParser


@click.command('inspect', help='Batch inspect the latest version of the software.')
@click.option('--filter-name', '-i', 'filter_name', help='Filter name.', cls=ClickStdOption)
@click.option('--worker', '-w', 'worker_num', help='The number of worker. (default: 2)', cls=ClickStdOption, default=2,
              type=int)
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration, worker_num: int, filter_name: Optional[str] = None):
    logger.debug(f'app cli inspect called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})')

    asyncio.run(process(cfg, worker_num, filter_name))

    # Merge the output JSON data files into all.json.
    ctx.invoke(cli_combine)


async def process(cfg: Configuration, worker_num: int, filter_name: Optional[str] = None):
    sem = asyncio.Semaphore(worker_num)

    task_list = []

    for v in cfg.settings.softwares:
        if filter_name is None or filter_name == v.name:
            module = importlib.import_module('app.parser.%s' % v.parser.replace('-', '_'))
            cls = getattr(module, 'Parser')
            # cls_handler = getattr(cls(cfg), 'handle')
            cls_o = cls(cfg)

            if isinstance(cls_o, BaseParser):
                task_list.append(asyncio.create_task(cls_o.handle(sem, v)))

    try:
        results = await asyncio.gather(*task_list, return_exceptions=True)

        if isinstance(results, list):
            for result in results:
                if isinstance(result, Exception):
                    logger.exception(result)
    except Exception as e:
        logger.exception(e)
