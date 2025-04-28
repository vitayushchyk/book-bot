from bot.processor.base_processor import BaseProcessor


class ReadeatBookProcessor(BaseProcessor):
    def __init__(self):
        super().__init__(source_type="readeat")
