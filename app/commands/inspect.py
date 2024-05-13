import asyncio
import importlib
import json
from pathlib import Path
from typing import Optional

import click
from click.core import Context
from loguru import logger

from app.core.click import ClickStdOption
from app.core.config import Configuration
from app.parser import Base as BaseParser


@click.command('inspect', help='Batch inspect the latest version of the software.')
@click.option('--filter-name', '-i', 'filter_name', help='Filter name.', cls=ClickStdOption)
@click.option('--worker', '-w', 'worker_num', help='The number of worker. (default: 4)', cls=ClickStdOption, default=4,
              type=int)
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration, worker_num: int, filter_name: Optional[str] = None):
    logger.debug(f'app cli inspect called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})')

    asyncio.run(process(cfg, worker_num, filter_name))

    # Merge the output JSON data files into all.json.
    _combine_json(cfg)


def _combine_json(cfg: Configuration):
    p = Path(cfg.workdir).joinpath('data')

    data = []

    for file in p.glob('*.json'):
        if file.name != 'all.json':
            with open(file, 'r', encoding='utf-8') as f:
                data.append(json.loads(f.read()))

    with open(Path(cfg.workdir).joinpath('data').joinpath('all.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=True, separators=(',', ':')))


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
                    logger.error(result)
    except Exception as e:
        logger.error(e)
