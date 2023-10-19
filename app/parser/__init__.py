import os
from typing import Optional, Dict

import aiohttp


class HTTP:
    @staticmethod
    async def get(url: str, params: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None, timeout: float = 15, is_json: bool = False):
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}

        if headers:
            hdr = hdr.update(headers)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(url,
                                   params=params,
                                   headers=hdr,
                                   proxy=os.environ.get('PROXY')) as resp:
                if is_json:
                    return resp.url, resp.status, resp.headers, await resp.json()
                else:
                    return resp.url, resp.status, resp.headers, await resp.text()
