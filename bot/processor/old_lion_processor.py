from bot.processor.base_processor import BaseProcessor


class OldLionProcessor(BaseProcessor):

    @property
    def shop_name(self):
        return "Видавництво Старого Лева"
