from typing import Dict, Union

import discord

from esport_api import get_all_discord_server_settings, \
    get_discord_server_settings, \
    get_or_create_discord_server_settings
from models import DiscordServerSettings


class __DiscordServerSettingsService():
    server_settings: Dict[str, DiscordServerSettings]

    def __init__(self):
        self.server_settings = {}
        all_server_settings = get_all_discord_server_settings()
        for server_settings in all_server_settings.data:
            print('Adding server settings', server_settings)
            self.server_settings[server_settings.guild_id] = server_settings

    def refresh_by_guild(self, guild: discord.Guild):
        """
        Gets or create the DiscordServerSettings for the specified discord.Guild
        """
        server_settings = get_or_create_discord_server_settings(guild)
        self.server_settings[server_settings.guild_id] = server_settings

    def refresh_by_discord_server_settings_id(self, discord_server_settings_id: str):
        """
        Similar to refresh_by_guild, but is more efficient because we already have the discord_server_settings_id
        """
        server_settings = get_discord_server_settings(discord_server_settings_id)
        self.server_settings[server_settings.guild_id] = server_settings

    def has_guild(self, guild_id: Union[str, int]):
        return str(guild_id) in self.server_settings


discord_server_settings_service = __DiscordServerSettingsService()
