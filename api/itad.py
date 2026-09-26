"""
@file itad.py
@brief Communication with IsThereAnyDeal API
@author DBZash
@date 2026-09-26
@version 0.0.1
"""

import asyncio
import aiohttp

#Reaching for secrets
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ITAD_API_KEY")

if API_KEY is None:
    raise Exception("ITAD_API_KEY not defined")

class IstThereAnyDeal:
    def __init__(self):
        self.base_url = "https://api.isthereanydeal.com/"
        self.headers = {
            "ITAD-API-Key": API_KEY
        }

    async def search_game(self, title):
        url = self.base_url+"games/search/v1"
        params = {
            "title": title,
            "results": 5
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=self.headers,
                params=params
            ) as response:

                print("Status:", response.status)

                data = await response.json()
                print(data)

itad = IstThereAnyDeal()
asyncio.run(itad.search_game("Grand Theft Auto IV"))
