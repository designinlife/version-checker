import asyncio
import os
import re
from pathlib import Path
from typing import List

import aiofiles
import aiohttp
import arrow
from loguru import logger
from semver.version import Version

from app.core.config import Configuration, AppSettingGithubItem, OutputResult


class GithubInspect:
    def __init__(self):
        pass

    def start(self, cfg: Configuration, items: List[AppSettingGithubItem]):
        self.cfg = cfg

        asyncio.run(self._main(items))

    def _create_download_links(self, version: str, links: List[str]) -> List[str]:
        r = []

        for v in links:
            r.append(v.format(version=version))

        return r

    async def _worker(self, name, queue):
        while True:
            # Get a "work item" out of the queue.
            queue_item = await queue.get()

            if isinstance(queue_item, AppSettingGithubItem):
                # Sleep for the "sleep_for" seconds.
                # await asyncio.sleep(3)
                timeout = aiohttp.ClientTimeout(total=15)

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(f'https://api.github.com/repos/{queue_item.repo}/tags', proxy=os.environ.get('PROXY')) as resp:
                        logger.debug(f'{resp.url} | STATUS: {resp.status}')

                        data_r = await resp.json()

                        semver_versions = []
                        commit_sha_arr = {}

                        exp_r = re.compile(queue_item.tag_pattern)

                        for v in data_r:
                            m = exp_r.match(v['name'])

                            if m:
                                ver = '{}.{}.{}'.format(m.group('major'), m.group('minor'), m.group('patch'))

                                commit_sha_arr[ver] = v['commit']['sha']
                                semver_versions.append(ver)

                        latest_version = max(semver_versions, key=Version.parse)

                        logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(semver_versions)}')
                        logger.debug('DOWNLOADS: {}'.format('\n'.join(self._create_download_links(latest_version, queue_item.download_urls))))

                        # 创建输出结果对象并写入 JSON 数据文件。
                        result = OutputResult(name=queue_item.name, url=f'https://github.com/{queue_item.repo}', latest=latest_version,
                                              versions=semver_versions, commit_sha=commit_sha_arr[latest_version],
                                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                        output_path = Path(self.cfg.workdir).joinpath('data')

                        if not output_path.is_dir():
                            output_path.mkdir(parents=True, exist_ok=True)

                        async with aiofiles.open(output_path.joinpath(f'{queue_item.name}.json'), 'w', encoding='utf-8') as f:
                            await f.write(result)

                        logger.info(f'<{queue_item.name}> data information has been generated.')

            # Notify the queue that the "work item" has been processed.
            queue.task_done()

            # print(f'{name} has slept for {sleep_for:.2f} seconds')

    async def _main(self, items: List[AppSettingGithubItem]):
        # Create a queue that we will use to store our "workload".
        queue = asyncio.Queue()

        # Generate random timings and put them into the queue.
        for v in items:
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
