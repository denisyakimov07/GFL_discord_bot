from typing import Union

import discord

from discord_server_settings_service import discord_server_settings_service
from models import SpecialChannelEnum


def get_channel_by_special_channel(
        guild: discord.Guild,
        special_channel: SpecialChannelEnum
) -> Union[discord.TextChannel, discord.VoiceChannel, None]:
    for_guild_err = f'guild id={guild.id} name={guild.name}'

    server_settings = discord_server_settings_service.server_settings[str(guild.id)]
    if server_settings is None:
        print(f'Found no server settings for {for_guild_err}')
        return None
    channel_id = server_settings.get_special_channel(special_channel)
    if channel_id is None:
        print(f'Found no {special_channel} Special Channel for {for_guild_err}')
        return None
    channel = guild.get_channel(int(channel_id))
    if channel is None:
        print(
            f'Incorrect {special_channel} Special Channel for {for_guild_err}.'
            f'channel_id={channel_id} may not exist anymore')
    return channel
