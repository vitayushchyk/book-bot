from bot.processor.base_processor import BaseProcessor


class YakabooProcessor(BaseProcessor):
    @property
    def shop_name(self):
        return "Yakaboo"
