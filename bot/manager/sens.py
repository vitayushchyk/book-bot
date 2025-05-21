from bot.manager.base_manager import BaseBManager
from bot.parser.sens_parser import SensBookParser
from bot.processor.sens_processor import SensBookProcessor


class Sens(BaseBManager):
    def get_parser(self):
        return SensBookParser(base_url=self.baseurl)

    def get_processor(self):
        return SensBookProcessor()
