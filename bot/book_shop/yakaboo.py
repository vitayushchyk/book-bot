import logging

import requests
from bs4 import BeautifulSoup

from bot.base.base_mixin import FetchBooksMixin
from bot.base.base_shop import BaseShop
from bot.utils.book_details import get_book_details
from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_relevance,
)


class Yakaboo(BaseShop):
    async def get_book(self, book_name: str) -> list:
        # Формуємо URL для пошуку
        search_url_yakaboo = f"{self.baseurl}/search?q={book_name.strip()}"

        try:
            response = requests.get(search_url_yakaboo)
            response.raise_for_status()

            # Встановлюємо кодування, якщо воно відсутнє або не 'utf-8'
            if response.encoding.lower() != "utf-8":
                response.encoding = "utf-8"

            soup = BeautifulSoup(response.text, features="html.parser")

            book_elements = soup.select("div.category-card")

            if not book_elements:
                logging.warning(
                    f"No books found for the query '{book_name}' on Yakaboo."
                )
                return []

            books = []
            filter_titles = set()

            for index, book in enumerate(book_elements):
                try:
                    # Оновлення класів та логіки для вибору елементів книги
                    title_tag = book.select_one("a.ui-card-title.category-card__name")
                    title = title_tag.text.strip() if title_tag else None

                    price_tag = book.select_one(
                        "div.category-card__content .category-card__price"
                    )
                    price = price_tag.text.strip() if price_tag else None
                    url_tag = book.select_one("a.category-card__image")
                    url = f"{self.baseurl}{url_tag['href']}" if url_tag else None

                    # Перевіряємо, чи була книга вже оброблена
                    if title and url and title not in filter_titles:
                        book_data = {
                            "title": title,
                            "price": price,
                            "url": url,
                        }
                        # Отримуємо детальну інформацію про книгу
                        normalized_book = await get_book_details(
                            book_data, source_type="yakaboo"
                        )
                        books.append(normalized_book)
                        filter_titles.add(title)
                    else:
                        logging.info(
                            f"Duplicate or incomplete book entry skipped: {title}"
                        )

                except Exception as e:
                    logging.error(
                        f"Error while processing book element #{index + 1}: {e}"
                    )
                    continue

            # Фільтруємо книги за точною відповідністю
            books = await filter_books_by_exact_match(books, book_name)

            # Якщо точних відповідностей немає, фільтруємо за подібністю
            if not books:
                books = await filter_books_by_similarity(books, book_name)

            # Сортуємо книги за релевантністю
            books = await sort_books_by_relevance(books, book_name)

            logging.info(f"Successfully fetched {len(books)} books from Yakaboo.")
            return books

        except requests.exceptions.RequestException as ex:
            logging.error(f"HTTP error while fetching books on Yakaboo: {ex}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error while processing Yakaboo books: {e}")
            return []
