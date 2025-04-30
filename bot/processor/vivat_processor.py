from bot.processor.base_processor import BaseProcessor

# TODO: Використати, коли дороблю парсери по магазину


class VivatProcessor(BaseProcessor):

    @property
    def price_key(self):
        return "name"

    @property
    def shop_name(self):
        return "Vivat"
