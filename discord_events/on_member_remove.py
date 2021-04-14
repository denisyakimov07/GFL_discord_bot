import discord_embeds

from discord_client import client
from discord_helper_utils import get_channel_by_special_channel
from models import SpecialChannelEnum


@client.event
async def on_member_remove(member):
    channel = get_channel_by_special_channel(member.guild, SpecialChannelEnum.audit_log_join)
    if channel is not None:
        await channel.send(embed=discord_embeds.left_server_embed(member))
