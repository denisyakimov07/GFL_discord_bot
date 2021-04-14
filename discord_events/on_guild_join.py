import discord

from discord_client import client
from discord_server_settings_service import discord_server_settings_service


@client.event
async def on_guild_join(guild: discord.Guild):
    discord_server_settings_service.refresh_by_guild(guild)
