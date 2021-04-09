from typing import Union

import discord

from discord_server_settings_service import discord_server_settings_service
from esport_api import verify_member
from models import SpecialChannelEnum, SpecialRoleEnum


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


async def try_to_verify_member(
        channel_id: int,
        from_member: discord.Member,
        to_member: discord.Member
) -> Union[str, bool]:
    guild = from_member.guild
    verify_channel = get_channel_by_special_channel(guild, SpecialChannelEnum.verify)

    if verify_channel is None:
        return False

    if verify_channel.id != channel_id:
        # Verifications can only be done in the verification channel
        return f'Verifications can only be done in the {verify_channel.name} channel'

    server_settings = discord_server_settings_service.get_settings_by_guild_id(guild.id)
    # TODO: Check how many members they have verified in the last 24 hours
    if server_settings.can_member_verify(from_member) is not True:
        return 'You do not have permissions to verify members'

    verify_role_id = server_settings.get_special_role(SpecialRoleEnum.verify)
    if verify_role_id is None:
        return f'No verify role has been set in the Management Portal'

    verify_role = discord.utils.get(guild.roles, id=int(verify_role_id))
    if verify_role is None:
        print(f'SpecialRole \'verify\' is invalid. It may have been deleted. Please reset it in the Management Portal')
        return False

    verify_member(from_member, to_member)
    if verify_role in to_member.roles:
        return 'User is already verified'

    await to_member.add_roles(verify_role)
    return True
