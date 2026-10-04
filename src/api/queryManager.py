"""
@file: queryManager.py
@brief: Query Manager Class
@author:DBZash
@date 2026-10-04
@version 0.1.2
"""

from api.itad import IsThereAnyDeal
from api.sessionManager import SessionManager
from exception.badstatus import BadStatus


class QueryManager:

    def __init__(self):
        self.sessionManager = SessionManager()

    async def start(self):
        await self.sessionManager.create()

    def use(self):
        return self.sessionManager.get_session()

    async def stop(self):
        await self.sessionManager.close()

    def touch(self):
        return self

    async def itad_price_lookup(self, game_ids : list, game_titles : list) -> str:

        itad = IsThereAnyDeal()

        try:
            async with self.use().post(
                itad.get_price_lookup_url(),
                headers=itad.headers,
                params=itad.get_price_lookup_params(),
                json=game_ids
            ) as response:
                if response.status != 200:
                    err = BadStatus("On dirait que je n'ai pas réussi à joindre l'API -> ", response.status)
                    raise err
                data = await response.json()
                if not data:
                    return f"Sorry... I couldn't find any price for {game_titles[0]}"

            title_by_id = dict(zip(game_ids, game_titles)) #Convert to a dictionnary to compensate for API jumbling
            lines = []
            for entry in data:
                value = entry["deals"][0]["price"]["amount"]
                lines.append(f"{title_by_id.get(entry['id'])} is currently €{value:.2f}")
            return "\n".join(lines)

        except BadStatus as err:
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
                    err = BadStatus("On dirait que je n'ai pas réussi à joindre l'API -> ", response.status)
                    raise err
                data = await response.json()

            game_id= [data[0]["id"]]
            game_itad_title = [data[0]["title"]]
            return await self.itad_price_lookup(game_id, game_itad_title)

        except BadStatus as err:
            return f"Psst... Quelque chose s'est mal passé : {err}"
        except IndexError:
            return "Psst... On dirait que je ne suis pas en mesure de trouver le jeu que tu me demandes"
        finally:
            await self.stop()