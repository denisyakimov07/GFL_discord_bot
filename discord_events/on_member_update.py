import discord
import discord_embeds

from discord_client import client
from discord_helper_utils import get_channel_by_special_channel
from models import SpecialChannelEnum


@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    role_log_channel = get_channel_by_special_channel(before.guild, SpecialChannelEnum.audit_log_roles)
    if role_log_channel is None:
        # TODO: Maybe warn the user that the special channel isn't set?
        return

    if before.roles != after.roles:
        roles_before = [role.name for role in before.roles]
        roles_after = [role.name for role in after.roles]
        if len(roles_before) < len(roles_after):
            role = list(set(roles_before) ^ set(roles_after))[0]
            await role_log_channel.send(embed=discord_embeds.user_add_role_embed(after, role))
        else:
            role = list(set(roles_before) ^ set(roles_after))[0]
            await role_log_channel.send(embed=discord_embeds.user_remove_role_embed(after, role))
