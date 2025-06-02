from bot.manager.base_manager import BaseManager
from bot.parser.fabula_parser import FabulaParser
from bot.processor.fabula_processor import FabulaProcessor


class Fabula(BaseManager):
    def get_parser(self):
        return FabulaParser(base_url=self.baseurl)

    def get_processor(self):
        return FabulaProcessor()
