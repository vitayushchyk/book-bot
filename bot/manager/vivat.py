from bot.manager.base_manager import BaseBManager
from bot.parser.vivat_parser import VivatParser
from bot.processor.vivat_processor import VivatProcessor


class Vivat(BaseBManager):
    def get_parser(self):
        return VivatParser(base_url=self.baseurl)

    def get_processor(self):
        return VivatProcessor()
