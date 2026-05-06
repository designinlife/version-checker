import asyncio
from typing import Optional

import aiohttp
import click
from click.core import Context
from loguru import logger

from app.commands.combine import cli as cli_combine
from app.core.click import ClickStdOption
from app.core.config import Configuration
from app.core.github import GithubHelper
from app.core.http import AsyncHttpClient
from app.core.inspect_result import InspectItemResult, InspectResult
from app.parser import Base as BaseParser
from app.parser.registry import load_parser_class


@click.command("inspect", help="Batch inspect the latest version of the software.")
@click.option("--filter-name", "-i", "filter_name", help="Filter name.", cls=ClickStdOption)
@click.option(
    "--worker",
    "-w",
    "worker_num",
    help="The number of worker. (default: 2)",
    cls=ClickStdOption,
    default=2,
    type=click.IntRange(min=1),
)
@click.option("--strict", "strict", help="Exit with non-zero code if any item fails.", is_flag=True)
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration, worker_num: int, strict: bool, filter_name: Optional[str] = None):
    logger.debug(f"app cli inspect called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})")

    if not cfg.debug:
        asyncio.run(show_rate_limit_best_effort())

    result = asyncio.run(process(cfg, worker_num, filter_name))

    if result.failed:
        logger.error(f"Inspect completed with {len(result.failed)} failed item(s).")
        for item in result.failed:
            logger.error(f"[{item.name}] {item.error_type}: {item.message}")

    if strict and result.has_failed:
        raise click.ClickException("Inspect completed with failed item(s).")

    if not cfg.debug:
        asyncio.run(show_rate_limit_best_effort())

    # Merge the output JSON data files into all.json.
    ctx.invoke(cli_combine)


async def show_rate_limit_best_effort():
    try:
        await GithubHelper.show_rate_limit()
    except Exception as e:
        logger.warning(f"GitHub rate limit check skipped: {type(e).__name__}: {e}")


async def process(cfg: Configuration, worker_num: int, filter_name: Optional[str] = None):
    if worker_num < 1:
        raise ValueError("worker_num must be greater than or equal to 1.")

    sem = asyncio.Semaphore(worker_num)

    task_list = []
    items = []

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
        for v in cfg.settings.softwares:
            if filter_name is not None and filter_name != v.name:
                continue

            if v.disabled:
                items.append(InspectItemResult.skipped(v.name, "Software item is disabled."))
                continue

            cls = load_parser_class(v.parser)
            # cls_handler = getattr(cls(cfg), 'handle')
            cls_o = cls(cfg)
            cls_o.httpc = AsyncHttpClient(debug=cfg.debug, session=session)

            if isinstance(cls_o, BaseParser):
                task_list.append(asyncio.create_task(cls_o.wrap_handle(sem, v)))

        try:
            results = await asyncio.gather(*task_list, return_exceptions=True)

            if isinstance(results, list):
                for result in results:
                    if isinstance(result, InspectItemResult):
                        items.append(result)
                    elif isinstance(result, Exception):
                        logger.exception(result)
                        items.append(InspectItemResult.failed("<unknown>", type(result).__name__, str(result)))

            return InspectResult(items=items)
        except Exception as e:
            logger.exception(e)
            return InspectResult(items=[InspectItemResult.failed("<process>", type(e).__name__, str(e))])
