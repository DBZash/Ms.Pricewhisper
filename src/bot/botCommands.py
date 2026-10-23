"""@file botCommands.py
@brief Handling of bot commands
@author DBZash
@date 2026-10-23
@version 0.3.0
"""

import discord
from api.queryManager import QueryManager
from exception.badstatus import BadStatusException
from exception.invalidparam import InvalidParamException
from exception.toomanyrequests import TooManyRequestsException
from sql.sqliteManager import SQLiteManager


def init_commands(client, guild, query_manager : QueryManager):

    sql_manager = SQLiteManager()

    async def _safe_execute(interaction: discord.Interaction, action_func):
        """Encapsulates common error handling and query_manager cleanup."""
        try:
            sql_manager.update_user(interaction.user.id, interaction.user.name)
            await action_func()
        except TooManyRequestsException as e:
            await interaction.response.send_message(e.prompt())
        except InvalidParamException as e:
            await interaction.response.send_message(e.prompt())
        except ValueError as e:
            await interaction.response.send_message(str(e))
        except BadStatusException as err:
            await interaction.response.send_message(f"Psst... Something bad happened : {err}")
        except IndexError:
            await interaction.response.send_message("Psst... Seems like I can't find this game")
        finally:
            if query_manager.alive():
                print ("Welp... That was awkward")
                await query_manager.stop()

    async def _resolve_game_and_wishlist(interaction: discord.Interaction, game: str):
        """Handles user update and resolves game_id and wishlist_id.
        :param interaction: discord.Interaction
        :param game: name of the game"""
        game_id, wishlist_id = sql_manager.resolve_wishlist_item_pkey(game_title=game, user_id=interaction.user.id)

        if game_id is None:
            api_data = await query_manager.fetch_game_data(game)
            game_id = api_data[0]["id"]
            game_title = api_data[0]["title"]
            await query_manager.price_lookup(game_ids=[game_id], game_titles=[game_title])

        return game_id, wishlist_id


    @client.tree.command(name="hey", description="Say Hi to Ms. Pricewhisper", guild=guild)
    async def hey(interaction: discord.Interaction):
        async def action():
            await interaction.response.send_message("I'm here!")
        await _safe_execute(interaction, action)

    @client.tree.command(name="check", description="Ask Ms.Pricewhisper to check the price of a game", guild=guild)
    async def check(interaction: discord.Interaction, game: str):
        async def action():
            await interaction.response.send_message(await query_manager.simple_lookup(game))
        await _safe_execute(interaction, action)

    @client.tree.command(name="watch", description="Ask Ms.Pricewhisper to watch a game for you", guild=guild)
    async def watch(interaction: discord.Interaction, game: str, rule_type: str, threshold: int | None = None):
        async def action():
            game_id, wishlist_id = await _resolve_game_and_wishlist(interaction, game)
            sql_manager.create_wishlist_item(game_id=game_id, wishlist_id=wishlist_id, alert_rule_type=rule_type, threshold=threshold)
            await interaction.response.send_message("Okay, I'll keep an eye out for you!")
        await _safe_execute(interaction, action)

    @client.tree.command(name="unwatch", description="Ask Ms.Pricewhisper to stop watching a game for you", guild=guild)
    async def unwatch(interaction: discord.Interaction, game: str):
        async def action():
            game_id, wishlist_id = await _resolve_game_and_wishlist(interaction, game)
            sql_manager.delete_wishlist_item(game_id=game_id, wishlist_id=wishlist_id)
            await interaction.response.send_message("Got it, I won't monitor this game for you anymore")
        await _safe_execute(interaction, action)

    @client.tree.command(name="whisper", description="Ask Ms.Pricewhisper to tell you about the games on your watchlist meeting your criteria", guild=guild)
    async def whisper(interaction: discord.Interaction):
        async def action():
            usr_id = interaction.user.id
            game_ids, game_titles = sql_manager.resolve_wishlist_items_identifiers(usr_id=usr_id)
            await query_manager.price_lookup(game_titles, game_ids)
            await interaction.response.send_message(await sql_manager.filtering_by_rule(user_id=usr_id))
        await _safe_execute(interaction, action)

    @client.tree.command(name="whisperall", description="Ask Ms.Pricewhisper to give you a full report on your watchlist", guild=guild)
    async def whisperall(interaction: discord.Interaction):
        async def action():
            game_ids, game_titles = sql_manager.resolve_wishlist_items_identifiers(usr_id=interaction.user.id)
            await interaction.response.send_message(await query_manager.price_lookup(game_titles, game_ids))
        await _safe_execute(interaction, action)

    @client.tree.command(name="clear", description="Ask Ms.Pricewhisper to clear your watchlist", guild=guild)
    async def clear(interaction: discord.Interaction):
        async def action():
            sql_manager.create_wishlist(interaction.user.id)
            await interaction.response.send_message("Psst... Your watchlist has been cleared. Tell me if you need to add **Anything** back")
        await _safe_execute(interaction, action)
