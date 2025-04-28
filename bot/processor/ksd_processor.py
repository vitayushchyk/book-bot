from bot.processor.base_processor import BaseProcessor

# TODO: Використати, коли дороблю парсери по магазину


class KSDProcessor(BaseProcessor):
    def __init__(self):
        super().__init__(source_type="ksd")
