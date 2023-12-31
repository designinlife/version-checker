import os
import time
from datetime import timedelta
from pathlib import Path
from typing import Optional, Dict, List

import aiofiles
import aiohttp
import arrow
from loguru import logger

from app.core.config import Configuration, OutputResult


class Assistant:
    def __init__(self, cfg: Configuration):
        self.cfg = cfg

    async def create(self, name: str, url: str, version: str, all_versions: List[str], download_links: List[str]):
        """Write JSON data file.

        Args:
            name:
            url:
            version:
            all_versions:
            download_links:
        """
        result = OutputResult(name=f'{name}', url=f'{url}', latest=version,
                              versions=all_versions,
                              download_urls=download_links,
                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

        output_subdir = os.environ.get('OUTPUT_DATA_DIR', 'data')
        output_path = Path(self.cfg.workdir).joinpath(output_subdir)

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(output_path.joinpath(f'{name}.json'), 'w', encoding='utf-8') as f:
            await f.write(result)

        logger.info(f'<\033[1;32m{name}\033[0m> done.')

    async def get(self, url: str,
                  params: Optional[Dict[str, str]] = None,
                  headers: Optional[Dict[str, str]] = None,
                  timeout: float = 15,
                  is_json: bool = False):
        """Performs an HTTP GET request and returns text or JSON object results.

        Args:
            url:
            params:
            headers:
            timeout:
            is_json:

        Returns:

        """
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}

        if headers:
            hdr.update(headers)

        if self.cfg.debug:
            # logger.debug(f'URL: {url}, PARAMS: {params}, HEADERS: {headers}, TIMEOUT: {timeout}, JSON RESULT: {is_json}')
            logger.debug(f'URL: {url}, PARAMS: {params}, TIMEOUT: {timeout}, JSON RESULT: {is_json}')

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(url,
                                   params=params,
                                   headers=hdr,
                                   proxy=os.environ.get('PROXY')) as resp:
                if 200 <= resp.status < 300:
                    # for k, v in resp.headers.items():
                    #     if 'ratelimit' in k.lower():
                    #         logger.debug(f'Response Header: {k}={v}')

                    if is_json:
                        return resp.url, resp.status, resp.headers, await resp.json()
                    else:
                        return resp.url, resp.status, resp.headers, await resp.text()
                else:
                    raise ValueError(f'HTTP status code exception. ({resp.status} | {url})')

    async def post(self, url: str,
                   params: Optional[Dict[str, str]] = None,
                   headers: Optional[Dict[str, str]] = None,
                   json: Optional[dict] = None,
                   is_json: bool = False,
                   timeout: float = 15):
        """Performs an HTTP POST request and returns JSON object results.

        Args:
            url:
            params:
            headers:
            json:
            is_text:
            timeout:

        Returns:

        """
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}

        if headers:
            hdr.update(headers)

        if self.cfg.debug:
            # logger.debug(f'URL: {url}, PARAMS: {params}, HEADERS: {headers}, TIMEOUT: {timeout}, JSON RESULT: {is_json}')
            logger.debug(f'URL: {url}, PARAMS: {params}, TIMEOUT: {timeout}, JSON: {json}')

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.post(url,
                                    params=params,
                                    headers=hdr,
                                    json=json,
                                    proxy=os.environ.get('PROXY')) as resp:
                if 200 <= resp.status < 300:
                    # for k, v in resp.headers.items():
                    #     if 'ratelimit' in k.lower():
                    #         logger.debug(f'Response Header: {k}={v}')

                    if is_json:
                        return resp.url, resp.status, resp.headers, await resp.json()
                    else:
                        return resp.url, resp.status, resp.headers, await resp.text()
                else:
                    raise ValueError(f'HTTP status code exception. ({resp.status} | {url})')

    @staticmethod
    async def ratelimit():
        """Print GitHub ratelimit data.

        """
        github_token = os.environ.get("GITHUB_TOKEN")

        headers = {}

        if github_token:
            headers = {
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {github_token}',
                'X-GitHub-Api-Version': '2022-11-28',
            }

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            async with session.get('https://api.github.com/rate_limit', headers=headers, proxy=os.environ.get('PROXY')) as resp:
                if 200 <= resp.status < 300:
                    data_r = await resp.json()

                    logger.info(
                        f'Rate Limit | CPU: {os.cpu_count()} '
                        f'| Remaining: \033[1;32m{data_r["rate"]["remaining"]}\033[0m/\033[1;33m{data_r["rate"]["limit"]}\033[0m'
                        f',\033[1;34m{timedelta(seconds=data_r["rate"]["reset"] - int(time.time()))}\033[0m '
                        f'| Current Time: {arrow.now("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss ZZ")} '
                        f'| Reset: {arrow.get(data_r["rate"]["reset"]).to("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss ZZ")}')
                else:
                    logger.warning('Ratelimit data reading failed.')
