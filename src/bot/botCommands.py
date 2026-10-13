"""@file botCommands.py
@brief Handling of bot commands
@author DBZash
@date 2026-10-14
@version 0.2.0
"""

import discord

from api.queryManager import QueryManager
from exception.badstatus import BadStatusException
from exception.invalidparam import InvalidParamException
from exception.toomanyrequests import TooManyRequestsException
from sql.sqliteManager import SQLiteManager


def init_commands(client, guild, query_manager : QueryManager):
    sql_manager = SQLiteManager()
    @client.tree.command(name="hey", description="Say Hi to Ms. Pricewhisper", guild=guild)
    async def hey(interaction: discord.Interaction):
        try:
            sql_manager.update_user(interaction.user.id, interaction.user.name)
            await interaction.response.send_message("I'm here!")
        except TooManyRequestsException as e:
            await interaction.response.send_message(e.prompt())

    @client.tree.command(name="check", description="Ask Ms.Pricewhisper to check the price of a game", guild=guild)
    async def check(interaction: discord.Interaction, game: str):
        answer = await query_manager.simple_lookup(game)
        await interaction.response.send_message(answer)

    @client.tree.command(name="watch", description="Ask Ms.Pricewhisper to watch a game for you", guild=guild)
    async def watch(interaction: discord.Interaction, game: str, rule_type : str, threshold : int | None = None):
        try:
            sql_manager.update_user(interaction.user.id, interaction.user.name)
            sql_data = sql_manager.find_item_pair_in_db(user_id=interaction.user.id, game_title=game)
            game_id = sql_data[0]
            wishlist_id = sql_data[1]

            if game_id is None:
                try:
                    api_data = await query_manager.fetch_game_data(game)
                    game_id = api_data[0]["id"]
                    game_title = api_data[0]["title"]
                    await query_manager.price_lookup(game_ids=[game_id], game_titles=[game_title])
                except BadStatusException as err:
                    await interaction.response.send_message(f"Psst... Something bad happened : {err}")
                except IndexError:
                    await interaction.response.send_message("Psst... Seems like I can't find this game")

            sql_manager.create_wishlist_item(game_id=game_id, wishlist_id=wishlist_id, alert_rule_type=rule_type, threshold=threshold)
            await interaction.response.send_message(f"Okay, I'll keep an eye out for you!")
        except TooManyRequestsException as e:
            await interaction.response.send_message(e.prompt())
        except InvalidParamException as e:
            await interaction.response.send_message(e.prompt())
        finally:
            if query_manager.alive(): await query_manager.stop()

    @client.tree.command(name="unwatch", description="Ask Ms.Pricewhisper to stop watching a game for you", guild=guild)
    async def unwatch(interaction: discord.Interaction, game: str):
        await interaction.response.send_message("Coming soon!")

    @client.tree.command(name="whisper", description="Ask Ms.Pricewhisper to tell you about the games on your watchlist meeting your criterions", guild=guild)
    async def whisper(interaction: discord.Interaction):
        await interaction.response.send_message("Coming soon!")

    @client.tree.command(name="whisperall", description="Ask Ms.Pricewhisper to give you a full report on your watchlist", guild=guild)
    async def whisperall(interaction: discord.Interaction):
        data = sql_manager.consult_all_items_from_wishlist(sql_manager.get_wishlist_id_from_user(interaction.user.id)[0])
        game_ids = []
        game_titles = []
        for item in data:
            game_ids.append(item[0])
            game_titles.append(item[1])

        answer = await query_manager.price_lookup(game_titles, game_ids)
        await interaction.response.send_message(answer)

    @client.tree.command(name="clear", description="Ask Ms.Pricewhisper to clear your watchlist", guild=guild)
    async def clear(interaction: discord.Interaction):
        try:
            sql_manager.update_user(interaction.user.id, interaction.user.name)
            sql_manager.create_wishlist(interaction.user.id)
            await interaction.response.send_message("Psst... Your watchlist has been cleared. Tell me if you need to add **Anything** back")
        except TooManyRequestsException:
            await interaction.response.send_message("Haven't we talked enough for now?")