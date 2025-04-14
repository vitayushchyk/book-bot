import logging

import requests
from bs4 import BeautifulSoup

from bot.book_shop.base_shop import BaseShop
from bot.utils.book_details import get_book_details
from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_relevance,
)


class Bookling(BaseShop):

    async def get_book(self, query: str):

        search_url = f"{self.baseurl}/catalog/?q={query.strip()}"
        logging.info(f"Searching books with URL: {search_url}")

        try:
            response = requests.get(search_url)
            logging.info(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, features="html.parser")

                books = soup.select(".item_info.TYPE_1")

                if not books:
                    return []

                results = []
                for book in books:

                    title_element = book.select_one(".item-title a span")
                    title = (
                        title_element.text.strip()
                        if title_element
                        else "Title not available"
                    )

                    price_element = book.select_one(".price .price_value")
                    price = (
                        f"{price_element.text.strip()} грн"
                        if price_element
                        else "Price not available"
                    )

                    url_element = book.select_one(".item-title a")
                    url = (
                        f"{self.baseurl}{url_element['href']}"
                        if url_element
                        else "URL not available"
                    )

                    book_data = {
                        "title": title,
                        "price": price,
                        "url": url,
                    }

                    detailed_book = await get_book_details(
                        book_data, source_type="bookling"
                    )
                    if detailed_book:
                        results.append(detailed_book)

                filtered_books = await filter_books_by_exact_match(results, query)

                if not filtered_books:

                    filtered_books = await filter_books_by_similarity(results, query)

                if not filtered_books:

                    return results

                sorted_books = await sort_books_by_relevance(filtered_books, query)

                return sorted_books

            else:
                logging.error(
                    f"Failed to fetch books. Status code: {response.status_code}"
                )
                return []
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return []
