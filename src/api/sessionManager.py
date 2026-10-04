"""
@file sessionManager.py
@brief Session manager class
@author DBZash
@date 2026-10-04
@version 0.1.1
"""

import aiohttp

class SessionManager:
    def __init__(self):
        self.session = None

    async def create(self) -> None:
        self.session = aiohttp.ClientSession()

    def get_session(self) -> aiohttp.ClientSession:
        return self.session

    async def close(self) -> None:
        await self.session.close()