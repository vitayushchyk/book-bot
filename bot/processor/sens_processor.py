from bot.processor.base_processor import BaseProcessor

# TODO: Використати, коли дороблю парсери по магазину


class SensBookProcessor(BaseProcessor):
    @property
    def shop_name(self):
        return "Сенс"
