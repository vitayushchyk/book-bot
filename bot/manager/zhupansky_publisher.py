from bot.manager.base_manager import BaseManager
from bot.parser.zhupansky_parser import ZhupanskyParser
from bot.processor.zhupansky_processor import ZhupanskyProcessor


class ZhupanskyPublisher(BaseManager):

    def get_parser(self):
        return ZhupanskyParser(base_url=self.baseurl)

    def get_processor(self):
        return ZhupanskyProcessor()
