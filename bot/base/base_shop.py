from abc import ABC, abstractmethod


class BaseShop(ABC):
    def __init__(self, driver, baseurl: str):
        self.driver = driver
        self.baseurl = baseurl

    @abstractmethod
    async def get_book(self, book_name: str): ...
