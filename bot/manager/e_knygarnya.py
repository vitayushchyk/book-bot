from bot.manager.base_manager import BaseManager
from bot.parser.ksd_e_knygarnya_parser import KSDeKnygarnyaParser
from bot.processor.e_knygarnya_processor import E_Knygarnya_Processor


class EKnygarnya(BaseManager):
    def get_parser(self):
        return KSDeKnygarnyaParser(base_url=self.baseurl)

    def get_processor(self):
        return E_Knygarnya_Processor()
