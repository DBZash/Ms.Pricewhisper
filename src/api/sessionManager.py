"""
@file sessionManager.py
@brief Session manager class
@author DBZash
@date 2026-09-28
@version 0.1.0
"""

import aiohttp

class SessionManager:
    def __init__(self):
        self.session = None

    async def create(self):
        self.session = aiohttp.ClientSession()

    def get_session(self):
        return self.session

    async def close(self):
        await self.session.close()