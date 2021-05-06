import logging

import discord

from typing import Union
from discord_server_settings_service import discord_server_settings_service
from esport_api import verify_member
from models import SpecialChannelEnum, SpecialRoleEnum
from discord_embeds import welcome_message_embed

log = logging.getLogger('Discord Helper Utils')


def get_channel_by_special_channel(
        guild: discord.Guild,
        special_channel: SpecialChannelEnum
) -> Union[discord.TextChannel, discord.VoiceChannel, None]:
    for_guild_err = f'guild id={guild.id} name={guild.name}'

    server_settings = discord_server_settings_service.server_settings.get(str(guild.id))
    if server_settings is None:
        log.warning(f'Found no server settings for {for_guild_err}')
        return None
    channel_id = server_settings.get_special_channel(special_channel)
    if channel_id is None:
        log.log(f'Found no {special_channel} Special Channel for {for_guild_err}')
        return None
    channel = guild.get_channel(int(channel_id))
    if channel is None:
        log.warning(
            f'Incorrect {special_channel} Special Channel for {for_guild_err}.'
            f'channel_id={channel_id} may not exist anymore')
    return channel


async def try_to_verify_member(
        channel_id: int,
        from_member: discord.Member,
        to_member: discord.Member,
        message: discord.Message
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
        return f'<@!{from_member.id}> You do not have permissions to verify members (<@!{to_member.id}>)'

    verify_role_id = server_settings.get_special_role(SpecialRoleEnum.verify)
    if verify_role_id is None:
        return f'No verify role has been set in the Management Portal'

    verify_role = discord.utils.get(guild.roles, id=int(verify_role_id))
    if verify_role is None:
        log.warning(f'SpecialRole \'verify\' is invalid. It may have been deleted.'
                    f'Please reset it in the Management Portal')
        return False

    verify_member(from_member, to_member)
    if verify_role in to_member.roles:
        await message.delete()
        return f'User <@!{to_member.id}> is already verified (<@!{from_member.id}>)'

    await to_member.add_roles(verify_role)

    return True


async def send_message_to_verified_user(member: discord.Member):
    await member.send(embed=welcome_message_embed())
