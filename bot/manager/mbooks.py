from bot.manager.base_manager import BaseManager
from bot.parser.mbooks_parser import MegogoBooksParser
from bot.processor.mbooks import MegogoBooksProcessor


class MegogoBooks(BaseManager):
    def get_parser(self):
        return MegogoBooksParser(base_url=self.baseurl)

    def get_processor(self):
        return MegogoBooksProcessor()
