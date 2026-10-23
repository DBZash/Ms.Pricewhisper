"""
@file: queryManager.py
@brief: Query Manager Class
@author:DBZash
@date 2026-10-23
@version 0.3.0
"""

from api.itad import IsThereAnyDeal
from api.sessionManager import SessionManager
from exception.badstatus import BadStatusException
from sql.sqliteManager import SQLiteManager


class QueryManager:

    def __init__(self):
        self.sessionManager = SessionManager()
        self.itad = IsThereAnyDeal()
        self._isAlive = False

    def alive(self):
        return self._isAlive

    async def start(self):
        if not self._isAlive:
            await self.sessionManager.create()
            self._isAlive = True

    def _use(self):
        return self.sessionManager.get_session()

    async def stop(self):
        await self.sessionManager.close()
        self._isAlive = False

    async def price_lookup(self, game_titles : list, game_ids : list):
        lines = []
        remaining_titles = []
        remaining_ids = []
        sql = SQLiteManager()
        for i in range(len(game_titles)):
            if sql.last_update_is_fresh(game_ids[i]):
                lines.append(sql.game_to_string(game_ids[i]))
            else:
                remaining_ids.append(game_ids[i])
                remaining_titles.append(game_titles[i])
        if len(remaining_titles) > 0:
            lines.append(await self.itad_price_lookup(remaining_ids, remaining_titles))
        if lines:
            return "\n".join(lines)
        return "I couldn't find any price, maybe your wishlist is empty or the games you're looking for aren't available"

    async def itad_price_lookup(self, game_ids : list, game_titles : list) -> str:

        sql = SQLiteManager()
        if not self.alive(): await self.start()

        try:
            async with self._use().post(
                self.itad.get_price_lookup_url(),
                headers=self.itad.headers,
                params=self.itad.get_price_lookup_params(),
                json=game_ids
            ) as response:
                if response.status != 200:
                    err = BadStatusException("Seems like I couldn't join the API -> ", response.status)
                    raise err
                data = await response.json()
                if not data:
                    return f"Sorry... I couldn't find any price for {game_titles[0]}"

            title_by_id = dict(zip(game_ids, game_titles)) #Convert to a dictionary to compensate for API jumbling
            lines = []
            for entry in data:
                sql.refresh_game(str(title_by_id.get(entry['id'])),entry, 'itad')
                lines.append(sql.game_to_string(entry['id']))
            if len(lines) != 0:
                return "\n".join(lines)
            return ""

        except BadStatusException as err:
            return f"Psst... Something went wrong : {err}"
        except IndexError:
            return "Psst... It seems I can't find the price of what you're looking for"

    async def simple_lookup(self, game_title : str):
        lookup = SQLiteManager().get_game_query_data(game_title)
        if lookup is not None:
            return await self.price_lookup([lookup[0]],[lookup[1]])
        return await self.itad_simple_lookup(game_title)

    async def fetch_game_data(self, game_title: str) -> list:
        if not self.alive(): await self.start()
        async with self._use().get(
                self.itad.get_game_lookup_url(),
                headers=self.itad.headers,
                params=self.itad.get_game_lookup_params(game_title)
        ) as response:
            if response.status != 200:
                raise BadStatusException("Seems like I couldn't join the API -> ", response.status)
            return await response.json()

    async def itad_simple_lookup(self, game_title: str) -> str:
        await self.start()
        try:
            data = await self.fetch_game_data(game_title)
            game_id = [data[0]["id"]]
            game_itad_title = [data[0]["title"]]
            return await self.price_lookup(game_itad_title, game_id)
        except BadStatusException as err:
            return f"Psst... Something went wrong : {err}"
        except IndexError:
            return "Psst... It seems I can't find the price of what you're looking for"
