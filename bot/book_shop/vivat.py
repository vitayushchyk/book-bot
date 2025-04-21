import logging

import requests
from bs4 import BeautifulSoup

from bot.base.base_shop import BaseShop
from bot.utils.book_details import get_book_details


class Vivat(BaseShop):
    async def get_book(self, book_name):
        try:

            search_url = f"{self.baseurl}{book_name}"
            response = requests.get(search_url)
            response.raise_for_status()

            data = response.json()
            logging.info("Data successfully fetched.")

            item_groups = data.get("results", {}).get("item_groups", [])
            book_data = None
            for group in item_groups:
                for item in group.get("items", []):
                    book_data = {
                        "url": item.get("url", "#"),
                    }
                    break
                if book_data:
                    break

            if not book_data or not book_data.get("url"):
                logging.warning("Book data or URL not found.")
                return []

            try:
                book_page_response = requests.get(book_data["url"])
                book_page_response.raise_for_status()

                soup = BeautifulSoup(book_page_response.text, "html.parser")

                title = soup.find("meta", attrs={"property": "og:title"})
                book_data["name"] = title["content"] if title else book_data["name"]

                price_meta = soup.find(
                    "meta", attrs={"property": "product:price:amount"}
                )
                if price_meta:
                    book_data["price"] = f'{price_meta["content"]} грн'

                canonical_link = soup.find("link", attrs={"rel": "canonical"})
                book_data["url"] = (
                    canonical_link["href"] if canonical_link else book_data["url"]
                )

            except requests.RequestException as e:
                logging.error(f"Error fetching/parsing book page: {e}")
            except Exception as e:
                logging.error(f"Unexpected error while parsing book page: {e}")

            formatted_book_data = await get_book_details(book_data, source_type="vivat")
            return [formatted_book_data] if formatted_book_data else []

        except requests.RequestException as e:
            logging.error(f"API request error: {e}")
            return []

        except Exception as e:
            logging.error(f"Unexpected error while fetching books: {e}")
            return []
