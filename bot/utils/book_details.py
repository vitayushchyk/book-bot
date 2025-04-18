import logging


async def get_book_details(book, source_type):
    try:
        if source_type in ["yakaboo", "sens", "readeat", "bookling"]:
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

        shop_name = {
            "yakaboo": "Yakaboo",
            "sens": "Sens",
            "readeat": "Readeat",
            "eknygarnya": "E-Knygarnya",
            "zhupansky_publisher": "Видавництво Жупанського",
            "bookling": "Bookling",
        }

        return {
            "title": title,
            "price": price,
            "link": link,
            "shop": shop_name.get(source_type, "Unknown"),
        }

    except Exception as e:
        logging.error(f"Error in get_book_details: {e}")
        return None
