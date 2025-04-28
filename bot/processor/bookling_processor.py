from bot.processor.base_processor import BaseProcessor


class BooklingProcessor(BaseProcessor):
    def __init__(self):
        super().__init__(source_type="bookling")
