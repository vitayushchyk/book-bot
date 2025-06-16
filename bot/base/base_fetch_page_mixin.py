import logging
import traceback
from typing import Optional

import aiohttp
from aiohttp import ClientConnectionError, ClientResponseError


class FetchPageMixin:
    """
    A mixin class for asynchronously fetching web pages, where a new session is created for every HTTP request.
    """

    @classmethod
    async def fetch_page(cls, url: str, timeout: int = 20) -> Optional[str]:
        """
        Fetches a webpage by its URL. A new HTTP session is created for every request.
        :param url: The URL of the page to fetch.
        :param timeout: Timeout for the HTTP request (default is 20 seconds).
        :return: The HTML content of the page as a string, or None in case of an error.
        """

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0 Safari/537.36"
        }
        timeout_config = aiohttp.ClientTimeout(total=timeout)

        try:
            async with aiohttp.ClientSession(
                headers=headers, timeout=timeout_config
            ) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    elif 400 <= response.status < 500:
                        logging.error(f"Client error on {url}: HTTP {response.status}")
                    elif 500 <= response.status < 600:
                        logging.error(f"Server error on {url}: HTTP {response.status}")
        except ClientConnectionError:
            logging.error(f"Connection error while fetching {url}")
        except ClientResponseError as response_error:
            logging.error(f"Invalid response from {url}: {response_error}")
        except Exception as ex:
            logging.error(f"Unknown error fetching URL {url}: {ex}")
            traceback.print_exc()
        return None
