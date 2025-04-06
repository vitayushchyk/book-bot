import logging

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


async def get_book_details(book, source_type):
    try:
        if source_type == "yakaboo":
            title_element = book.find_element(By.CSS_SELECTOR, "a.ui-card-title")
            title = title_element.text.strip()
            link = title_element.get_attribute("href")

            price_element = book.find_element(
                By.CSS_SELECTOR, "div.ui-price-display__main span"
            )
            price = (
                price_element.text.strip() if price_element else "Price not available"
            )

        elif source_type == "sens":
            title = book.get("title", "Title not available")
            price = book.get("price", "Price not available")
            link = book.get("url", "#")

        elif source_type == "readeat":
            title = book.get("title", "Title not available")
            price = book.get("price", "Price not available")
            link = book.get("url", "#")

        else:
            raise ValueError(f"Unsupported source type: {source_type}")

        return {"title": title, "price": price, "link": link}

    except NoSuchElementException as e:
        logging.error(f"Failed to locate book details: {e}")
        return None
    except Exception as e:
        logging.error(f"Error in get_book_details: {e}")
        return None


async def get_book_details_from_element(book_element, driver):
    try:

        book_url = book_element.find_element(By.TAG_NAME, "a").get_attribute("href")
        book_title = book_element.find_element(By.TAG_NAME, "img").get_attribute("alt")

        try:

            price_wrapper = driver.find_element(By.CSS_SELECTOR, ".price-new")
            price_element = price_wrapper.find_element(
                By.CSS_SELECTOR, ".fn_visiblePrice"
            )
            book_price = f"{price_element.text.strip()} грн"
        except Exception:
            book_price = "Price not available"

        return {
            "title": book_title,
            "price": book_price,
            "url": book_url,
        }

    except Exception as ex:
        logging.error(f"Error parsing book element: {str(ex)}")
        return None
