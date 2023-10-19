import os
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

        logger.info(f'<{name}> data information has been generated.')

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
            hdr = hdr.update(headers)

        if self.cfg.debug:
            logger.debug(f'URL: {url}, PARAMS: {params}, HEADERS: {headers}, TIMEOUT: {timeout}, JSON RESULT: {is_json}')

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(url,
                                   params=params,
                                   headers=hdr,
                                   proxy=os.environ.get('PROXY')) as resp:
                if 200 <= resp.status < 300:
                    if is_json:
                        return resp.url, resp.status, resp.headers, await resp.json()
                    else:
                        return resp.url, resp.status, resp.headers, await resp.text()
                else:
                    raise ValueError(f'HTTP status code exception. ({resp.status} | {url})')
