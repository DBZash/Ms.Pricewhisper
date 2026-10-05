"""
@file botCommands.py
@brief Handling of bot commands
@author DBZash
"""

import discord

def init_commands(client, guild, query_manager):
    @client.tree.command(name="hey", description="Say Hi to Ms. Pricewhisper", guild=guild)
    async def hey(interaction: discord.Interaction):
        await interaction.response.send_message("I'm here!")

    @client.tree.command(name="check", description="Ask Ms.Pricewhisper to check the price of a game", guild=guild)
    async def check(interaction: discord.Interaction, game: str):
        answer = await query_manager.itad_simple_lookup(game)
        await interaction.response.send_message(answer)

    @client.tree.command(name="watch", description="Ask Ms.Pricewhisper to watch a game for you", guild=guild)
    async def watch(interaction: discord.Interaction, game: str):
        await interaction.response.send_message("Coming soon!")

    @client.tree.command(name="unwatch", description="Ask Ms.Pricewhisper to stop watching a game for you", guild=guild)
    async def unwatch(interaction: discord.Interaction, game: str):
        await interaction.response.send_message("Coming soon!")

    @client.tree.command(name="whisper", description="Ask Ms.Pricewhisper to tell you about the games on your watchlist meeting your criterions", guild=guild)
    async def whisper(interaction: discord.Interaction):
        await interaction.response.send_message("Coming soon!")

    @client.tree.command(name="whisperall", description="Ask Ms.Pricewhisper to give you a full report on your watchlist", guild=guild)
    async def report(interaction: discord.Interaction):
        #Test Exemple
        game_ids = [
            "018d954c-7887-714c-8eb8-808a642fcf0f",
            "018d937f-590c-728b-ac35-38bcff85f086",
            "018d937f-64ac-7047-aed9-f1a7e64996d5",
        ]

        game_titles = [
            "The Messenger",
            "Elden Ring",
            "Octopath Traveler II",
        ]

        await query_manager.start()
        answer = await query_manager.itad_price_lookup(game_ids, game_titles)
        await interaction.response.send_message(answer)
        await query_manager.stop()

    @client.tree.command(name="clear", description="Ask Ms.Pricewhisper to clear your watchlist", guild=guild)
    async def clear(interaction: discord.Interaction):
        await interaction.response.send_message("Coming soon!")