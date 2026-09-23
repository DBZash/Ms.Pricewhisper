"""
@file main.py
@author DBZash
@brief Main file
"""
import discord
from discord.ext import commands

#Reaching for secrets
import os
from dotenv import load_dotenv
load_dotenv()

guild_id = os.getenv("SERVER_ID")
if guild_id is None:
    raise Exception("SERVER_ID not defined")
guild = discord.Object(id=guild_id)

class MissPricewhisper(commands.Bot):
    """
    @author DBZash
    @brief Main class
    """
    async def sync(self):
        try:
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands')
        except Exception as err:
            print(f"failed to sync command: {err}")

    async def on_ready(self):
        """
        @author DBZash
        @brief Signal the bot is up and running
        """
        await self.sync()
        print(f'Pssst... I am {self.user}, live and ready!')

    async def on_message(self, message):
        """
        @author DBZash
        @brief log, in terminal of messages read by the bot on the server
        :param message: Message read
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

    #run
    client.run(bot_token)

setup()