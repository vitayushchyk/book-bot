from bot.processor.base_processor import BaseProcessor


class VivatProcessor(BaseProcessor):
    @property
    def title_key(self):
        return "name"

    @property
    def shop_name(self):
        return "Vivat"
