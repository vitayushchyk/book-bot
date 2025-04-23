import logging

import requests
from bs4 import BeautifulSoup

from bot.base.base_shop import BaseShop
from bot.core.config import settings
from bot.utils.book_details import get_book_details
from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_price,
    sort_books_by_relevance,
)


class PublisherParser(BaseShop):
    async def get_book(self, book_name):

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        }

        params = {
            "s": book_name,  # Search query
            "products": 1,  # Include products in the search
            "count": 3,  # Maximum number of search results
            "images": 1,  # Include images in the results
            "posts": 1,  # Include posts in the results
            "portfolio": 1,  # Include portfolio in the search results
            "pages": 1,  # Include pages in the search
            "action": "et_get_search_result",  # Trigger the search action
        }

        try:
            search_url = settings.search_url_zhupansky
            logging.info(f"Requesting URL: {search_url} with parameters: {params}")
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()

            json_data = response.json()
            if not json_data or "html" not in json_data:
                logging.warning("Field 'html' not found in the JSON response")
                return []

            embedded_html = json_data["html"]
            soup = BeautifulSoup(embedded_html, features="html.parser")
            books = soup.select("ul.et-result-products > li")
            logging.info(f"Books found: {len(books)}")

            raw_books = []

            for book in books:
                title = (
                    book.select_one("a").text.strip()
                    if book.select_one("a")
                    else "Title not available"
                )
                link = (
                    book.select_one("a")["href"]
                    if book.select_one("a")
                    else "Link not available"
                )

                price = None
                if link:
                    try:
                        product_response = requests.get(link, headers=headers)
                        product_response.raise_for_status()
                        product_soup = BeautifulSoup(
                            product_response.text, features="html.parser"
                        )

                        price_meta = product_soup.select_one("meta[itemprop=price]")
                        if price_meta and price_meta.get("content"):
                            price = f'{price_meta["content"]} ₴'

                        if not price:
                            price_element = product_soup.select_one(
                                "p.price span.woocommerce-Price-amount bdi"
                            )
                            if price_element:
                                price = price_element.text.strip()

                    except requests.exceptions.RequestException as e:
                        logging.error(f"Error fetching product page at {link}: {e}")
                        price = "Price not available"

                if not price:
                    price = "Price not available"

                raw_books.append(
                    {
                        "title": title,
                        "link": link,
                        "price": price,
                    }
                )

            processed_books = [
                await get_book_details(raw_book, source_type="zhupansky_publisher")
                for raw_book in raw_books
            ]

            processed_books = [book for book in processed_books if book]

            filtered_books = await filter_books_by_exact_match(
                processed_books, book_name
            )

            if not filtered_books:
                filtered_books = await filter_books_by_similarity(
                    processed_books, book_name
                )

            sorted_books = await sort_books_by_relevance(filtered_books, book_name)
            await sort_books_by_price(books)

            return sorted_books

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error: {http_err}")
            return []

        except requests.exceptions.RequestException as req_err:
            logging.error(f"Request error: {req_err}")
            return []

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return []
