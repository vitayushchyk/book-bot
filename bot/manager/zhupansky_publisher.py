from bot.manager.base_manager import BaseBManager
from bot.parser.zhupansky_parser import ZhupanskyParser
from bot.processor.zhupansky_processor import ZhupanskyProcessor


class ZhupanskyPublisher(BaseBManager):

    def get_parser(self):
        return ZhupanskyParser(base_url=self.baseurl)

    def get_processor(self):
        return ZhupanskyProcessor()
