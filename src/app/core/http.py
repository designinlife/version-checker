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
        """读取响应正文摘要，用于错误日志，避免把完整远端响应写入异常。"""
        try:
            text = await resp.text()
        except Exception:
            return ""

        text = " ".join(text.split())
        return text[:limit]

    async def _read_response(self, resp, url: str, is_json: bool, raise_for_status: bool = True):
        """解析 HTTP 响应，并把状态码或 JSON 解析问题转换为带上下文的异常。"""
        if 200 <= resp.status < 300 or not raise_for_status:
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
        raise_for_status: bool = True,
    ) -> Tuple[URL, int, "CIMultiDictProxy[str]", Any | str]:
        """发送 HTTP 请求并返回最终 URL、状态码、响应头和响应内容。

        当传入外部 session 时复用调用方的连接池；否则为单次请求创建短生命周期 session。
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
            "timeout": timeout,
        }

        if self.session is not None:
            async with self.session.request(**request_kwargs) as resp:
                return await self._read_response(resp, url, is_json, raise_for_status=raise_for_status)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.request(**request_kwargs) as resp:
                return await self._read_response(resp, url, is_json, raise_for_status=raise_for_status)
