"""@file sqliteManager.py
@brief SQLiteManager class
@author DBZash
@date 2026-10-23
@version 0.4.0
"""

import os
import sqlite3
from datetime import datetime
import sql.sqliteUtility as Util
from dotenv import load_dotenv
from exception.invalidparam import InvalidParamException
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
            self._execute("""PRAGMA foreign_keys = ON""")
            self._initialized = True

    def _execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def _read(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def _read_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def delete_user(self, user_id):
        self._execute("""DELETE FROM users WHERE user_id = ?""", (user_id,))

    def update_user(self, user_id, username):
        user_data = self._read("""SELECT * FROM users WHERE user_id = ?""", (user_id,))
        date = datetime.now()

        if user_data is None: # --> Insert New User
            self._execute("""INSERT INTO users VALUES (?, ?, ?, ?)""", (user_id, username, date, 1))

        elif Util.delta_over_a_target(date, datetime.fromisoformat(user_data[2]), Util.HOUR): # --> Update Existing User AND reset ddos flags
           self._execute("""UPDATE users SET ddos_flags_at = 1, last_usage_at = ? WHERE user_id = ?""", (date, user_id))

        elif user_data[3] < 60 : # --> Update Existing User AND Increment ddos flags
            self._execute("""UPDATE users SET ddos_flags_at = ddos_flags_at + 1, last_usage_at = ? WHERE user_id = ?""", (date, user_id))
        else:
            raise TooManyRequestsException(username)

    def delete_user_wishlist(self, user_id):
        self._execute("""DELETE FROM wishlists WHERE user_id = ?""", (user_id,))

    def consult_user_wishlist(self, user_id):
        return self._read("""SELECT * FROM wishlists WHERE user_id = ?""", (user_id,))

    def get_wishlist_id_from_user(self, user_id):
        ans = self._read("""SELECT wishlist_id FROM wishlists WHERE user_id = ?""", (user_id,))
        if ans:
            return ans
        raise ValueError("It seems like you don't have a wishlist the following options are available friend: \n"
                         "- try **/clear** to generate an empty one\n"
                         "- try **/watch** to generate one with a specific game\n")

    def create_wishlist(self, user_id):
        wishlist_data = self.consult_user_wishlist(user_id)
        if wishlist_data is not None:
            self.delete_user_wishlist(user_id)
        self._execute("""INSERT INTO wishlists (user_id) VALUES (?)""", (user_id,))

    def delete_game(self, game_id):
        self._execute("""DELETE FROM games WHERE game_id = ?""", (game_id,))

    def consult_game(self, game_id):
        return self._read("""SELECT * FROM games WHERE game_id = ?""", (game_id,))

    def get_game_query_data(self, title) -> tuple | None:
        """Function to fetch the data needed for a game query
        :param title: Title of the game
        :return: A tuple containing, in order, the game_title and game_id as known by the database,
        if not found then return None
        """
        reformated_titles = Util.title_formatting(title)
        for formated_title in reformated_titles:
            query_data = self._read("""SELECT game_title, game_id FROM games WHERE game_title = ?""", (formated_title,))
            if query_data is not None:
                return query_data
        return None

    def last_update_is_fresh(self, game_id):
        data = self.consult_game(game_id)
        if data is None:
            return False
        return Util.delta_under_a_target(datetime.now(), datetime.fromisoformat(data[2]), Util.FRESH_GAME)

    def insert_game(self, game_id, game_title, url, price, cut, shop, voucher=None):
        date = datetime.now()
        if voucher:
            self._execute("""INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (game_id, game_title, date, url, price, cut, voucher, shop, price, shop, date))
        else:
            self._execute("""INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?)""", (game_id, game_title, date, url, price, cut, shop, price, shop, date))

    def update_game(self, game_id, url, price, cut, shop, voucher=None):
        date = datetime.now()
        past_data = self._read("""SELECT lowest_known_price FROM games WHERE game_id = ?""", (game_id,))
        query = ["""UPDATE games SET last_update_date = ?, last_update_url = ?, last_update_price = ?, last_update_cut = ?, last_update_shop = ?"""]
        args = [date, url, price, cut, shop]
        if voucher:
            query.append(""", last_update_voucher = ?"""); args.append(voucher)
        else:
            query.append(""", last_update_voucher = NULL""")
        if past_data[0] > price:
            query.append(""", lowest_known_price = ?, lkp_shop = ?, lkp_date = ?"""); args.extend([price, shop, date])
        query.append(""" WHERE game_id = ?"""); args.append(game_id)
        self._execute("".join(query), args)

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

        title = data[1]; url = data[3]; price = data[4] ;cut = data[5]
        voucher = data[6]; shop = data[7]; low = data[8]

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

    def create_wishlist_item(self, game_id, wishlist_id : int, alert_rule_type: str, threshold : int | None =None):
        if alert_rule_type not in ('below', 'lowest', 'cut'):
            raise InvalidParamException(alert_rule_type, ('below', 'lowest', 'cut'))

        elif alert_rule_type in ('below', 'cut') and type(threshold) is not int :
            raise InvalidParamException(threshold, "Integer")

        if alert_rule_type == 'lowest' and threshold is not None:
            threshold = None

        elif type(threshold) is int and threshold > 100:
            threshold = 100

        elif type(threshold) is int and threshold < 0:
            threshold = 0

        if alert_rule_type == 'lowest':
            alert_rule_type = 'observed_low'

        elif alert_rule_type == 'cut':
            alert_rule_type = 'minimum_cut'
        try:
            if threshold is not None:
                self._execute("""INSERT INTO wishlist_items (game_id, wishlist_id, alert_rule_type, threshold, last_updated_at) VALUES (?,?,?,?,?)""",
                              (game_id, wishlist_id, alert_rule_type, threshold, datetime.now()))
            else:
                self._execute("""INSERT INTO wishlist_items (game_id, wishlist_id, alert_rule_type, last_updated_at) VALUES (?,?,?,?)""",
                              (game_id, wishlist_id, alert_rule_type, datetime.now()))
        except sqlite3.IntegrityError: # <-- During runtime, reached if the item already exists even though the rest was verified, then we simply try to update the rule
            self.update_wishlist_item_rule(game_id, wishlist_id, alert_rule_type, threshold)

    async def filtering_by_rule(self, user_id):
        lines = []
        data = self.consult_all_wishlist_items(self.get_wishlist_id_from_user(user_id=user_id)[0])
        for game in data:
            game_id = game[0]
            if Util.meet_rule_condition(game_data=game):
                lines.append(self.game_to_string(game_id=game_id, form='full'))
        if lines:
            return "\n".join(lines)
        return "Huh-Oh, it seems like nothing matches your rules yet"

    def update_wishlist_item_rule(self, game_id, wishlist_id, alert_rule_type, threshold=None):
        if threshold is not None:
            self._execute("""UPDATE wishlist_items SET alert_rule_type = ?, threshold = ?, last_updated_at = ? WHERE game_id = ? AND wishlist_id = ?""",
                          (alert_rule_type, threshold, datetime.now(), game_id, wishlist_id))
        else:
            self._execute("""UPDATE wishlist_items SET alert_rule_type = ?, threshold = NULL, last_updated_at = ? WHERE game_id = ? AND wishlist_id = ?""",
                          (alert_rule_type, datetime.now(), game_id, wishlist_id))

    def notified_item_flag(self, game_id, wishlist_id, last_notified_price, last_notified_at):
        self._execute("""UPDATE wishlist_items SET last_notified_price = ?, last_notified_at = ?, last_updated_at = ? WHERE game_id = ? AND wishlist_id = ?""",
                      (last_notified_price, last_notified_at, datetime.now(), game_id, wishlist_id))

    def delete_wishlist_item(self, game_id, wishlist_id):
        if self._read("""SELECT COUNT(game_id) FROM wishlist_items WHERE wishlist_id = ? AND game_id = ?""", (wishlist_id, game_id))[0] > 0:
            self._execute("""DELETE FROM wishlist_items WHERE wishlist_id = ? AND game_id = ?""", (wishlist_id, game_id))
        else:
            raise ValueError("Psst... This item isn't part of your wishlist, so I couldn't delete it from it\n"
                             "The good news is that it's technically already out of scope :wink:")

    def consult_wishlist_item(self, game_id, wishlist_id):
        return self._read("""SELECT * FROM wishlist_items WHERE wishlist_id = ? AND game_id = ?""", (wishlist_id, game_id))

    def consult_all_wishlist_items(self, wishlist_id):
        return self._read_all("""SELECT games.game_id, game_title, last_update_price, alert_rule_type, threshold, lowest_known_price, last_update_cut FROM games INNER JOIN wishlist_items ON games.game_id = wishlist_items.game_id WHERE wishlist_items.wishlist_id = ?""",
                              (wishlist_id,))

    def resolve_wishlist_item_pkey(self, game_title, user_id):
        game_data = self.get_game_query_data(game_title)
        wishlist_data = self.consult_user_wishlist(user_id)
        if wishlist_data is None:
            self.create_wishlist(user_id)
            wishlist_data = self.consult_user_wishlist(user_id)
        wishlist_id = wishlist_data[0]
        if game_data is not None:
            game_id = game_data[1]
        else:
            game_id = None
        return game_id, wishlist_id

    def resolve_wishlist_items_identifiers(self, usr_id):
        data = self.consult_all_wishlist_items(self.get_wishlist_id_from_user(usr_id)[0])
        if not data:
            raise ValueError("It seems like your wishlist is empty, consider adding a game to it.")

        game_ids = []; game_titles = []
        for item in data:
            game_ids.append(item[0])
            game_titles.append(item[1])

        return game_ids, game_titles
