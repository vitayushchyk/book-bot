import logging


class LogMaker:

    @staticmethod
    async def log_books_pretty(books, description=None):
        """
        Logs the list of books in short format: - title | price | url/link (first available)
        :param books: List of books
        :param description: Optional descriptive note for the log entry
        """

        if books:
            books_list = "\n".join(
                [
                    f"- {book.get('title')} | {book.get('price')} | {book.get('url') or book.get('link', '')}"
                    for book in books
                ]
            )
            head = f"{description}\n" if description else ""
            logging.info(f"{head}{books_list}")
        else:
            msg = f"{description}: " if description else ""
            logging.info(f"{msg}no books found.")
