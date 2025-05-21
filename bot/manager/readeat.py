from bot.manager.base_manager import BaseBManager
from bot.parser.readead_parser import ReadeatParser
from bot.processor.readead_processor import ReadeatBookProcessor


class Readeat(BaseBManager):
    def get_parser(self):
        return ReadeatParser(base_url=self.baseurl)

    def get_processor(self):
        return ReadeatBookProcessor()
