from bot.processor.base_processor import BaseProcessor


class MegogoBooksProcessor(BaseProcessor):

    @property
    def shop_name(self):
        return "Megogo Books"
