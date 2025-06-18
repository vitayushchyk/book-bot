from bot.processor.base_processor import BaseProcessor


class ReadeatBookProcessor(BaseProcessor):
    @property
    def link_key(self):
        return "link"

    @property
    def shop_name(self):
        return "Readeat"
