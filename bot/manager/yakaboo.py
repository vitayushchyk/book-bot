from bot.manager.base_manager import BaseManager
from bot.parser.yakaboo_parser import YakabooParser
from bot.processor.yakaboo_processor import YakabooProcessor


class Yakaboo(BaseManager):
    def get_parser(self):
        return YakabooParser(base_url=self.baseurl)

    def get_processor(self):
        return YakabooProcessor()
