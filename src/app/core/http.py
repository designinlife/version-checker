import os
from typing import Any, Dict, Optional, Tuple

import aiohttp
from loguru import logger
from multidict import CIMultiDictProxy
from yarl import URL

from . import DEFAULT_USERAGENT


class AsyncHttpClient:
    def __init__(self, debug: bool = False, session: aiohttp.ClientSession | None = None):
        self.debug: bool = debug
        self.session = session

    async def _response_excerpt(self, resp, limit: int = 300) -> str:
        try:
            text = await resp.text()
        except Exception:
            return ""

        text = " ".join(text.split())
        return text[:limit]

    async def _read_response(self, resp, url: str, is_json: bool):
        if 200 <= resp.status < 300:
            # for k, v in resp.headers.items():
            #     if 'ratelimit' in k.lower():
            #         logger.debug(f'Response Header: {k}={v}')

            if is_json:
                try:
                    return resp.url, resp.status, resp.headers, await resp.json()
                except Exception as e:
                    excerpt = await self._response_excerpt(resp)
                    raise ValueError(f"Invalid JSON response. ({resp.status} | {url} | {excerpt})") from e
            else:
                return resp.url, resp.status, resp.headers, await resp.text()
        else:
            excerpt = await self._response_excerpt(resp)
            raise ValueError(f"HTTP request failed. ({resp.status} | {url} | {excerpt})")

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, str]] = None,
        data: Optional[dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 15,
        is_json: bool = False,
    ) -> Tuple[URL, int, "CIMultiDictProxy[str]", Any | str]:
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
        hdr = {"User-Agent": DEFAULT_USERAGENT}

        if headers:
            hdr.update(headers)

        if self.debug:
            logger.debug(f"URL: {url}, PARAMS: {params}, TIMEOUT: {timeout}, JSON RESULT: {is_json}")

        request_kwargs = {
            "method": method,
            "url": url,
            "params": params,
            "allow_redirects": True,
            "json": data,
            "headers": hdr,
            "proxy": os.environ.get("PROXY"),
        }

        if self.session is not None:
            async with self.session.request(**request_kwargs) as resp:
                return await self._read_response(resp, url, is_json)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.request(**request_kwargs) as resp:
                return await self._read_response(resp, url, is_json)
