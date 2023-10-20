import asyncio
import json
import random
import sys
from pathlib import Path
from typing import List, Optional

from click.core import Context
from loguru import logger

from app.core.config import Configuration, AppSettingSoftItem
from app.inspect.parser import Parser
from app.parser import Assistant


class InspectRunner:
    def __init__(self, ctx: Context, cfg: Configuration):
        self.ctx = ctx
        self.cfg = cfg

    def start(self, filter_name: Optional[str] = None):
        asyncio.run(Assistant.ratelimit())
        asyncio.run(self._main(self.cfg.settings.softwares, filter_name))

        # Merging behavior is not performed in DEBUG mode.
        if not self.cfg.debug:
            self._combine_json()

    def _combine_json(self):
        p = Path(self.cfg.workdir).joinpath('data')

        data = []

        for file in p.glob('*.json'):
            if file.name != 'all.json':
                with open(file, 'r', encoding='utf-8') as f:
                    data.append(json.loads(f.read()))

        with open(Path(self.cfg.workdir).joinpath('data').joinpath('all.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=True, separators=(',', ':')))

    async def _worker(self, name, queue):
        assistant = Assistant(self.cfg)

        while True:
            # Get a "work item" out of the queue.
            queue_item = await queue.get()

            if isinstance(queue_item, AppSettingSoftItem):
                try:
                    await Parser.create(queue_item.parser, assistant, queue_item)
                except Exception as exc:
                    logger.exception('[{}] {}'.format(queue_item.name, exc))

                    if self.cfg.debug:
                        sys.exit(1)

            await asyncio.sleep(random.uniform(1.0, 3.0))

            # Notify the queue that the "work item" has been processed.
            queue.task_done()

            # print(f'{name} has slept for {sleep_for:.2f} seconds')

    async def _main(self, items: List[AppSettingSoftItem], filter_name: Optional[str] = None):
        # Create a queue that we will use to store our "workload".
        queue = asyncio.Queue()

        # Generate random timings and put them into the queue.
        for v in items:
            if not filter_name or filter_name == v.name:
                queue.put_nowait(v)

        # Create three worker tasks to process the queue concurrently.
        tasks = []

        for i in range(4):
            task = asyncio.create_task(self._worker(f'worker-{i}', queue))
            tasks.append(task)

        # Wait until the queue is fully processed.
        await queue.join()

        # Cancel our worker tasks.
        for task in tasks:
            task.cancel()

        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info('All done.')
