from aiohttp import ClientSession


class BaseHTTPClientMixin:
    async def get_session(self) -> ClientSession:
        return ClientSession()
