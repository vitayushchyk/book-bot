from bot.manager.base_manager import BaseBManager
from bot.parser.old_lion_parser import OldLionParser
from bot.processor.old_lion_processor import OldLionProcessor


class OldLion(BaseBManager):
    def get_parser(self):
        return OldLionParser(base_url=self.baseurl)

    def get_processor(self):
        return OldLionProcessor()
