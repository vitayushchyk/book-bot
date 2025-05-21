from bot.manager.base_manager import BaseManager
from bot.parser.ksd_e_knygarnya_parser import KSDeKnygarnyaParser
from bot.processor.ksd_processor import KSDProcessor


class KSD(BaseManager):
    def get_parser(self):
        return KSDeKnygarnyaParser(base_url=self.baseurl)

    def get_processor(self):
        return KSDProcessor()
