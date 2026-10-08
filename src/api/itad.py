"""
@file itad.py
@brief Communication with IsThereAnyDeal API
@author DBZash
@date 2026-09-28
@version 0.1.1
"""

#Reaching for secrets
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ITAD_API_KEY")

if API_KEY is None:
    raise Exception("ITAD_API_KEY not defined")

class IsThereAnyDeal:
    base_url = "https://api.isthereanydeal.com/"
    headers = {
        "ITAD-API-Key": API_KEY
    }
    def __init__(self):
        pass

    def get_base_url(self):
        return self.base_url

    @staticmethod
    def get_price_lookup_params():
        return {
            "country": "FR",
            "deals": "false",
            "vouchers": "true",
        }

    def get_price_lookup_url(self):
        return self.base_url + "games/prices/v3"

    @staticmethod
    def get_game_lookup_params(game_title):
        return {
            "title": game_title,
            "results": 5
        }

    def get_game_lookup_url(self):
        return self.base_url + "games/search/v1"

    def get_headers(self):
        return self.headers