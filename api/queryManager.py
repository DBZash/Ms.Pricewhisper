"""
@File: queryManager.py
@brief: Query Manager Class
@author:DBZash
@date 2026-09-28
@version 0.1.0
"""

from api.itad import IsThereAnyDeal
from api.sessionManager import SessionManager
import asyncio

class QueryManager:
    def __init__(self):
        self.sessionManager = SessionManager()

    async def itad_lookup(self, game_title):
        lookup_session_manager = self.sessionManager
        await lookup_session_manager.create()
        lookup_session = lookup_session_manager.get_session()

        itad = IsThereAnyDeal()

        async with lookup_session.get(
            itad.get_game_lookup_url(),
            headers=itad.headers,
            params=itad.get_game_lookup_params(game_title)
        ) as response:
            print("Status:", response.status)

            data = await response.json()
            game_id= [data[0]["id"]]

        async with lookup_session.post(
            itad.get_price_lookup_url(),
            headers=itad.headers,
            params=itad.get_price_lookup_params(),
            json=game_id
        ) as response:
            print("Status:", response.status)

            data = await response.json()
            value = data[0]["deals"][0]["price"]["amount"]

        await lookup_session_manager.close()
        return value