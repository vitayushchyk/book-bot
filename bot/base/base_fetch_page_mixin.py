import logging

from bot.base.base_client import BaseHTTPClientMixin


class FetchPageMixin(BaseHTTPClientMixin):
    async def fetch_page(self, url: str, timeout: int = 5) -> str | None:

        session = await self.get_session()
        async with session:
            try:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        return await response.text()
                    logging.error(f"Failed to fetch URL {url}: {response.status}")
            except Exception as e:
                logging.error(f"Request error: {e}")
        return None
