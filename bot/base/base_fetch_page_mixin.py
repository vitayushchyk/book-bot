import logging
import traceback
from typing import Optional

import aiohttp


class FetchPageMixin:
    @classmethod
    async def fetch_page(cls, url: str, timeout: int = 20) -> Optional[str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        try:
            async with aiohttp.ClientSession(
                headers=headers, timeout=timeout_config
            ) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
        except Exception as ex:
            logging.error(f"Error fetching URL {url}: {ex}")
            traceback.print_exc()
        return None
