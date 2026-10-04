"""
@file msPriceWhisper.py
@brief MissPriceWhisper class and initialization
@author DBZash
@date 2026-10-04
@version 0.1.0
"""

import os
from discord.ext import commands
from dotenv import load_dotenv
from api.queryManager import QueryManager
from bot.botCommands import *

load_dotenv()
guild_id = os.getenv("SERVER_ID")
if guild_id is None:
    raise Exception("SERVER_ID not defined")
guild = discord.Object(id=guild_id)

class MissPriceWhisper(commands.Bot):
    """
    Class responsible for interacting with the bot
    """

    async def sync(self):
        try:
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands')
        except Exception as err:
            print(f"failed to sync command: {err}")

    async def on_ready(self):
        """@brief In terminal, signal the bot is up and running
        """
        await self.sync()
        print(f'Pssst... I am {self.user}, live and ready!')

    async def on_message(self, message):
        """@brief in terminal, show messages read by the bot on the server
        :param message The message read
        @author DBZash
        """
        if message.author == self.user:
            return
        print(f'Message from {message.author} : {message.content}')

def run():
    intents = discord.Intents.default()
    intents.message_content = True

    client = MissPriceWhisper(command_prefix='!', intents=intents)
    bot_token = os.getenv("BOT_TOKEN")
    if bot_token is None:
        raise Exception("BOT_TOKEN not defined")

    init_commands(client, guild, query_manager=QueryManager())
    client.run(bot_token)