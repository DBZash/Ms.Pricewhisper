"""
@file main.py
@author DBZash
@brief Main file
"""
import discord

#Reaching for secrets
import os
from dotenv import load_dotenv
load_dotenv()

class MissPricewhisper(discord.Client):
    """
    @author DBZash
    @brief Main class
    """
    async def on_ready(self):
        """
        @author DBZash
        @brief Signal the bot is up and running
        """
        print(f'Psss... I am {self.user}, live and ready!')

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
    intents = discord.Intents.default()
    intents.message_content = True
    client = MissPricewhisper(intents=intents)

    #Obviously not sharing the actual token value, lol
    bot_token = os.getenv("BOT_TOKEN")
    if bot_token is None:
        raise Exception("BOT_TOKEN not defined")
    client.run(bot_token)

setup()