import requests
from bs4 import BeautifulSoup

from bot.core.config import settings


class RattingBooks:
    def __init__(self, api_key, google_rating):
        self.api_key = api_key
        self.google_rating = settings.google_rating

    def search_book(self, query):
        url = self.google_rating
        params = {"q": query, "key": self.api_key}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return None
        data = response.json()
        if "items" not in data or not data["items"]:
            return None

        book = data["items"][0]
        info = book.get("volumeInfo", {})
        sale_info = book.get("saleInfo", {})
        buy_link = sale_info.get("buyLink")

        rating = info.get("averageRating", "Немає рейтингу")

        if buy_link:
            rating = self._scrape_rating_from_buylink(buy_link) or rating

        return {
            "title": info.get("title", "Немає назви"),
            "description": info.get("description", "Немає опису"),
            "authors": ", ".join(info.get("authors", ["Немає автора"])),
            "rating": rating,
        }

    def _scrape_rating_from_buylink(self, link):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the rating value ("TT9eCd" class)
            rating_tag = soup.find("div", class_="TT9eCd")
            rating_value = rating_tag.text.strip() if rating_tag else None

            # Find the reviews count ("g1rdde" class), and clean up the value
            reviews_tag = soup.find("div", class_="g1rdde")
            reviews_value = None
            if reviews_tag:
                # Extract integer from text like 'Відгуки: 125'
                import re

                match = re.search(r"\d+", reviews_tag.text)
                reviews_value = match.group(0) if match else None

            # Return combined info
            if rating_value and reviews_value:
                return f"{rating_value} ⭐️ (Відгуки: {reviews_value})"
            elif rating_value:
                return f"{rating_value} ⭐️"
            else:
                return None
        except Exception as ex:
            print(f"Scraping failed: {ex}")
        return None
