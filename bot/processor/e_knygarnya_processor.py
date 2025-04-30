from bot.processor.base_processor import BaseProcessor

# TODO: Використати, коли дороблю парсери по магазину


class E_Knygarnya_Processor(BaseProcessor):
    @property
    def title_key(self):
        return "name"

    @property
    def shop_name(self):
        return "E-Knygarnya"
