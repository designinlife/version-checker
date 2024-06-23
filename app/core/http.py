import os
from typing import Optional, Dict, Tuple, Any

import aiohttp
from loguru import logger
from multidict import CIMultiDictProxy
from yarl import URL

from . import DEFAULT_USERAGENT


class AsyncHttpClient:
    def __init__(self, debug: bool = False):
        self.debug: bool = debug

    async def request(self, method: str, url: str,
                      params: Optional[Dict[str, str]] = None,
                      data: Optional[dict] = None,
                      headers: Optional[Dict[str, str]] = None,
                      timeout: float = 15,
                      is_json: bool = False) -> Tuple[URL, int, "CIMultiDictProxy[str]", Any | str]:
        """
        Send an HTTP request.

        Args:
            method:
            url:
            params:
            data:
            headers:
            timeout:
            is_json:

        Returns:

        """
        hdr = {'User-Agent': DEFAULT_USERAGENT}

        if headers:
            hdr.update(headers)

        if self.debug:
            logger.debug(f'URL: {url}, PARAMS: {params}, TIMEOUT: {timeout}, JSON RESULT: {is_json}')

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.request(method=method, url=url,
                                       params=params,
                                       json=data,
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
