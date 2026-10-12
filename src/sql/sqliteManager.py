"""@file sqliteManager.py
@brief SQLiteManager class
@author DBZash
@date 2026-10-12
@version 0.2.0
"""

import os
import sqlite3
from datetime import datetime
import sql.utility as u
from dotenv import load_dotenv
from exception.toomanyrequests import TooManyRequestsException
from exception.unknownprovider import UnknownProviderException

load_dotenv()
realpath = os.getenv("DB_PATH")
if realpath is None:
    raise ValueError("DB_PATH environment variable not found")
path = realpath

class SQLiteManager:
    """SQLiteManager class, handles writing to and reading from the database
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.conn = sqlite3.connect(path)
            self.cursor = self.conn.cursor()
            self.execute("""PRAGMA foreign_keys = ON""")
            self._initialized = True

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def read(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def read_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def delete_user(self, user_id):
        self.execute("""DELETE FROM users WHERE user_id = ?""", (user_id,))

    def update_user(self, user_id, username):
        user_data = self.read("""SELECT * FROM users WHERE user_id = ?""", (user_id,))
        date = datetime.now()

        if user_data is None: # --> Insert New User
            self.execute("""INSERT INTO users VALUES (?, ?, ?, ?)""", (user_id, username, date, 1))

        elif u.delta_over_a_target(date, datetime.fromisoformat(user_data[2]), u.HOUR): # --> Update Existing User AND reset ddos flags
           self.execute("""UPDATE users SET ddos_flags_at = 1, last_usage_at = ? WHERE user_id = ?""", (date, user_id))

        elif user_data[3] < 60 : # --> Update Existing User AND Increment ddos flags
            self.execute("""UPDATE users SET ddos_flags_at = ddos_flags_at + 1, last_usage_at = ? WHERE user_id = ?""", (date, user_id))
        else:
            raise TooManyRequestsException(username)

    def delete_user_wishlist(self, user_id):
        self.execute("""DELETE FROM wishlists WHERE user_id = ?""", (user_id,))

    def consult_user_wishlist(self, user_id):
        return self.read("""SELECT * FROM wishlists WHERE user_id = ?""", (user_id,))

    def get_wishlist_id_from_user(self, user_id):
        return self.read("""SELECT wishlist_id FROM wishlists WHERE user_id = ?""", (user_id,))

    def create_wishlist(self, user_id):
        wishlist_data = self.consult_user_wishlist(user_id)
        if wishlist_data is not None:
            self.delete_user_wishlist(user_id)
        self.execute("""INSERT INTO wishlists (user_id) VALUES (?)""", (user_id,))


    def delete_game(self, game_id):
        self.execute("""DELETE FROM games WHERE game_id = ?""", (game_id,))

    def consult_game(self, game_id):
        return self.read("""SELECT * FROM games WHERE game_id = ?""", (game_id,))

    def last_update_is_fresh(self, game_id):
        data = self.consult_game(game_id)
        if data is None:
            return False
        return u.delta_under_a_target(datetime.now(), datetime.fromisoformat(data[2]), u.FRESH_GAME)

    def insert_game(self, game_id, game_title, url, price, cut, shop, voucher=None):
        date = datetime.now()
        if voucher:
            self.execute("""INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (game_id, game_title, date, url, price, cut, voucher, shop, price, shop, date))
        else:
            self.execute("""INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?)""", (game_id, game_title, date, url, price, cut, shop, price, shop, date))

    def update_game(self, game_id, url, price, cut, shop, voucher=None):
        date = datetime.now()
        past_data = self.read("""SELECT lowest_known_price FROM games WHERE game_id = ?""", (game_id,))
        query = ["""UPDATE games SET last_update_date = ?, last_update_url = ?, last_update_price = ?, last_update_cut = ?, last_update_shop = ?"""]
        args = [date, url, price, cut, shop]
        if voucher:
            query.append(""", last_update_voucher = ?"""); args.append(voucher)
        else:
            query.append(""", last_update_voucher = NULL""")
        if past_data[0] > price:
            query.append(""", lowest_known_price = ?, lkp_shop = ?, lkp_date = ?"""); args.extend([price, shop, date])
        query.append(""" WHERE game_id = ?"""); args.append(game_id)
        self.execute("".join(query), args)

    def refresh_game(self, game_title : str, deal_data, provider : str = 'itad'):
        if not deal_data:
            return
        match provider:
            case 'itad':
                game_id = deal_data['id']
                if self.last_update_is_fresh(game_id):
                    return
                sub_data = deal_data['deals']
                url = sub_data[0]['url']
                price = sub_data[0]['price']['amount']
                cut = sub_data[0]['cut']
                shop = sub_data[0]['shop']['name']
                voucher = sub_data[0]['voucher']
                if self.consult_game(game_id) is None:
                    self.insert_game(game_id, game_title, url, price, cut, shop, voucher)
                else:
                    self.update_game(game_id, url, price, cut, shop, voucher)
            case _:
                raise UnknownProviderException

    def game_to_string(self, game_id, form='fast'):
        data = self.consult_game(game_id)

        title = data[1]
        url = data[3]
        price = data[4]
        cut = data[5]
        voucher = data[6]
        shop = data[7]
        low = data[8]

        line = [
            f"[{title}]({url}) is currently **€{price}** "
            f"({cut}% off) at {shop}"
        ]

        if voucher is not None:
            line.append(f"with voucher: *{voucher}*")

        if form == 'full' and low < price:
            lkp_shop = data[9]
            lkp_date = data[10]
            line.append(
                f"FYI, the lowest price I'm aware of is "
                f"**€{low}** at {lkp_shop} ({lkp_date})"
            )

        return " ".join(line)

    def create_wishlist_item(self, game_id, wishlist_id, alert_rule_type, last_notified_price, last_notified_at, last_updated_at, threshold=None):
        if threshold is not None:
            self.execute("""INSERT INTO wishlist_items VALUES (?,?,?,?,?,?,?)""", (game_id, wishlist_id, alert_rule_type, threshold, last_notified_price, last_notified_at, last_updated_at))
        else:
            self.execute("""INSERT INTO wishlist_items VALUES (?,?,?,NULL,?,?,?)""", (game_id, wishlist_id, alert_rule_type, last_notified_price, last_notified_at, last_updated_at))

    def delete_wishlist_item(self, game_id, wishlist_id):
        self.execute("""DELETE FROM wishlist_items WHERE wishlist_id = ? AND game_id = ?""", (wishlist_id, game_id))

    def consult_wishlist_item(self, wishlist_id, game_id):
        return self.read("""SELECT * FROM wishlist_items WHERE wishlist_id = ? AND game_id = ?""", (wishlist_id, game_id))

    def consult_all_wishlist_items(self, wishlist_id):
        return self.read_all("""SELECT * FROM wishlist_items WHERE wishlist_id = ?""", (wishlist_id,))
