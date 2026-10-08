"""
@file sqliteManager.py
@brief SQLiteManager class
@author DBZash
@date 2026-10-08
@version 0.1.0
"""
import os
import sqlite3
import datetime
from dotenv import load_dotenv

load_dotenv()
realpath = os.getenv("DB_PATH")
if realpath is None:
    raise ValueError("DB_PATH environment variable not found")
path = realpath

class SQLiteManager:
    """SQLiteManager class, handles writing to and reading from the database
    """

    def __init__(self):

        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.execute("""PRAGMA foreign_keys = ON""")

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

    def insert_user(self, user_id, username, last_usage):
        self.execute("""INSERT INTO users VALUES (?, ?, ?, ?)""", (user_id, username, last_usage, 1))

    def update_user(self, last_usage, user_id):
        self.execute("""UPDATE users SET ddos_flags_at = ddos_flags_at + 1, last_usage_at = ? WHERE user_id = ?""", (last_usage, user_id))

    def delete_user(self, user_id):
        self.execute("""DELETE FROM users WHERE user_id = ?""", (user_id,))

    def consult_user(self, user_id):
        return self.read("""SELECT * FROM users WHERE user_id = ?""", (user_id,))

    def create_wishlist(self,wishlist_id, user_id):
        self.execute("""INSERT INTO wishlists VALUES (?, ?)""", (wishlist_id, user_id))

    def delete_wishlist(self, wishlist_id):
        self.execute("""DELETE FROM wishlists WHERE wishlist_id = ?""", (wishlist_id,))

    def delete_wishlist_user(self, user_id):
        self.execute("""DELETE FROM wishlists WHERE user_id = ?""", (user_id,))

    def consult_wishlist(self, wishlist_id):
        return self.read("""SELECT * FROM wishlists WHERE wishlist_id = ?""", (wishlist_id,))

    def get_wishlist_id_from_user(self, user_id):
        return self.read("""SELECT wishlist_id FROM wishlists WHERE user_id = ?""", (user_id,))

    def insert_game(self, game_id, game_title, url, price, cut, shop, voucher=None):
        date = datetime.datetime.now()
        if voucher:
            self.execute("""INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (game_id, game_title, date, url, price, cut, voucher, shop, price, shop, date))
        else:
            self.execute("""INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?)""", (game_id, game_title, date, url, price, cut, shop, price, shop, date))

    def consult_game(self, game_id):
        return self.read("""SELECT * FROM games WHERE game_id = ?""", (game_id,))

    def consult_game_lkp(self, game_id):
        return self.read("""SELECT lowest_known_price FROM games WHERE game_id = ?""", (game_id,))

    def update_game(self, game_id, url, price, cut, shop, voucher=None):
        date = datetime.datetime.now()
        past_data = self.consult_game_lkp(game_id)
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

    def delete_game(self, game_id):
        self.execute("""DELETE FROM games WHERE game_id = ?""", (game_id,))

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