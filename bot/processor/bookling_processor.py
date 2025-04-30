from bot.processor.base_processor import BaseProcessor


class BooklingProcessor(BaseProcessor):
    @property
    def shop_name(self):
        return "Bookling"
