from bot.manager.base_manager import BaseManager
from bot.parser.bookling_parser import BooklingParser
from bot.processor.bookling_processor import BooklingProcessor


class Bookling(BaseManager):
    def get_parser(self):
        return BooklingParser(base_url=self.baseurl)

    def get_processor(self):
        return BooklingProcessor()
