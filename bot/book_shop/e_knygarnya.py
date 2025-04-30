# from bot.base.base_mixin import FetchBooksMixin
# from bot.base.base_shop import BaseShop
# from bot.core.config import settings
#
#
# class EKnygarnya(BaseShop, FetchBooksMixin):
#     async def get_book(self, book_name: str):
#         search_url = f"{settings.search_url_eknygarnya}{book_name}&s=large"
#         return await self.fetch_books(
#             search_url, source_type="eknygarnya", book_name=book_name
#         )
