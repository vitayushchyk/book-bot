from bot.processor.base_processor import BaseProcessor


class ZhupanskyProcessor(BaseProcessor):
    def __init__(self):
        super().__init__(source_type="zhupansky_publisher")
