"""
@file main.py
@brief Main file
@author DBZash
@date 2026-09-26
@version 0.2.1
"""
import discord
from discord.ext import commands

#Reaching for secrets
import os
from api.queryManager import QueryManager
from dotenv import load_dotenv

load_dotenv()

guild_id = os.getenv("SERVER_ID")
if guild_id is None:
    raise Exception("SERVER_ID not defined")
guild = discord.Object(id=guild_id)

class MissPricewhisper(commands.Bot):
    """@brief Main class
    @author DBZash
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

#Intent init
def setup():
    #intent setup
    intents = discord.Intents.default()
    intents.message_content = True

    #Client setup, Obviously not sharing the actual token value, lol
    client = MissPricewhisper(command_prefix='!', intents=intents)
    bot_token = os.getenv("BOT_TOKEN")
    if bot_token is None:
        raise Exception("BOT_TOKEN not defined")

    # Commands
    @client.tree.command(name="hey", description="Say Hi to Ms. Pricewhisper", guild=guild)
    async def hey(interaction: discord.Interaction):
        await interaction.response.send_message("I'm here!")

    @client.tree.command(name="check", description="Check the price of a game", guild=guild)
    async def check(interaction: discord.Interaction, game: str):
        query_manager = QueryManager()
        answer = await query_manager.itad_lookup(game)
        await interaction.response.send_message(
            answer
        )

    #run
    client.run(bot_token)

if __name__ == "__main__":
    setup()
