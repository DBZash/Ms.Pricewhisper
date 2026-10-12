"""
@file: queryManager.py
@brief: Query Manager Class
@author:DBZash
@date 2026-10-04
@version 0.2.0
"""

from api.itad import IsThereAnyDeal
from api.sessionManager import SessionManager
from exception.badstatus import BadStatusException
from sql.sqliteManager import SQLiteManager


class QueryManager:

    def __init__(self):
        self.sessionManager = SessionManager()

    async def start(self):
        await self.sessionManager.create()

    def use(self):
        return self.sessionManager.get_session()

    async def stop(self):
        await self.sessionManager.close()

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
        return "\n".join(lines)

    async def itad_price_lookup(self, game_ids : list, game_titles : list) -> str:

        sql = SQLiteManager()
        itad = IsThereAnyDeal()

        try:
            async with self.use().post(
                itad.get_price_lookup_url(),
                headers=itad.headers,
                params=itad.get_price_lookup_params(),
                json=game_ids
            ) as response:
                if response.status != 200:
                    err = BadStatusException("On dirait que je n'ai pas réussi à joindre l'API -> ", response.status)
                    raise err
                data = await response.json()
                if not data:
                    return f"Sorry... I couldn't find any price for {game_titles[0]}"

            title_by_id = dict(zip(game_ids, game_titles)) #Convert to a dictionnary to compensate for API jumbling
            lines = []
            for entry in data:
                sql.refresh_game(str(title_by_id.get(entry['id'])),entry, 'itad')
                lines.append(sql.game_to_string(entry['id']))
            if len(lines) != 0:
                return "\n".join(lines)
            return ""

        except BadStatusException as err:
            return f"Psst... Quelque chose s'est mal passé : {err}"
        except IndexError:
            return "Psst... On dirait que je ne suis pas en mesure de trouver le prix de ce que tu me demandes"

    async def itad_simple_lookup(self, game_title) -> str:

        await self.start()
        itad = IsThereAnyDeal()

        try:
            async with self.use().get(
                itad.get_game_lookup_url(),
                headers=itad.headers,
                params=itad.get_game_lookup_params(game_title)
            ) as response:
                if response.status != 200:
                    err = BadStatusException("On dirait que je n'ai pas réussi à joindre l'API -> ", response.status)
                    raise err
                data = await response.json()

            game_id= [data[0]["id"]]
            game_itad_title = [data[0]["title"]]
            return await self.price_lookup(game_itad_title, game_id)

        except BadStatusException as err:
            return f"Psst... Quelque chose s'est mal passé : {err}"
        except IndexError:
            return "Psst... On dirait que je ne suis pas en mesure de trouver le jeu que tu me demandes"
        finally:
            await self.stop()
