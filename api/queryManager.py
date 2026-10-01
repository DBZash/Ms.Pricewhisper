"""
@file: queryManager.py
@brief: Query Manager Class
@author:DBZash
@date 2026-10-01
@version 0.1.1
"""

from api.itad import IsThereAnyDeal
from api.sessionManager import SessionManager
from exception.badstatus import BadStatus
import asyncio

class QueryManager:

    def __init__(self):
        self.sessionManager = SessionManager()

    async def itad_lookup(self, game_title):
        await self.sessionManager.create()
        itad = IsThereAnyDeal()

        #Find game block
        try:
            async with self.sessionManager.get_session().get(
                itad.get_game_lookup_url(),
                headers=itad.headers,
                params=itad.get_game_lookup_params(game_title)
            ) as response:
                if response.status != 200:
                    err = BadStatus("On dirait que je n'ai pas réussi à joindre l'API -> ", response.status)
                    raise err
                data = await response.json()
                game_id= [data[0]["id"]]
        except BadStatus as err:
            await self.sessionManager.close()
            return f"Psst... Quelque chose s'est mal passé : {err}"
        except IndexError:
            await self.sessionManager.close()
            return "Psst... On dirait que je ne suis pas en mesure de trouver le jeu que tu me demandes"


        #Find price block
        try:
            async with self.sessionManager.get_session().post(
                itad.get_price_lookup_url(),
                headers=itad.headers,
                params=itad.get_price_lookup_params(),
                json=game_id
            ) as response:
                if response.status != 200:
                    err = BadStatus("On dirait que je n'ai pas réussi à joindre l'API -> ", response.status)
                    raise err
                data = await response.json()
                value = data[0]["deals"][0]["price"]["amount"]
        except BadStatus as err:
            await self.sessionManager.close()
            return f"Psst... Quelque chose s'est mal passé : {err}"
        except IndexError:
            await self.sessionManager.close()
            return "Psst... On dirait que je ne suis pas en mesure de trouver le prix du jeu que tu me demandes"

        await self.sessionManager.close()
        return f"{game_title} is currently €{value:.2f}"