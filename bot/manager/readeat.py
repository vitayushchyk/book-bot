from bot.manager.base_manager import BaseManager
from bot.parser.readead_parser import ReadeatParser
from bot.processor.readead_processor import ReadeatBookProcessor


class Readeat(BaseManager):
    def get_parser(self):
        return ReadeatParser(base_url=self.baseurl)

    def get_processor(self):
        return ReadeatBookProcessor()
