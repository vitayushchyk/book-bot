import logging


async def get_book_details(book, source_type):

    try:
        if (
            source_type == "yakaboo"
            or source_type == "sens"
            or source_type == "readeat"
        ):
            title = book.get("title", "Title not available")
            price = book.get("price", "Price not available")
            link = book.get("url", "#")

        elif source_type == "eknygarnya":
            title = book.get("name", "Title not available")
            price = book.get("price", "Price not available")
            link = book.get("url", "#")

        elif source_type == "zhupansky_publisher":
            title = book.get("title", "Title not available")
            price = book.get("price", "Price not available")
            link = book.get("link", "#")

        else:
            raise ValueError(f"Unsupported source type: {source_type}")

        return {"title": title, "price": price, "link": link}

    except Exception as e:
        logging.error(f"Error in get_book_details: {e}")
        return None
