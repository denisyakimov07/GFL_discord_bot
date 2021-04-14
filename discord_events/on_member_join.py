import discord
import discord_embeds

from discord_client import client
from discord_helper_utils import get_channel_by_special_channel
from models import SpecialChannelEnum


@client.event
async def on_member_join(member: discord.Member):
    server_log_channel = get_channel_by_special_channel(member.guild, SpecialChannelEnum.audit_log_join)
    if server_log_channel is not None:
        await server_log_channel.send(embed=discord_embeds.on_member_join_to_server_embed(member))

    verify_channel = get_channel_by_special_channel(member.guild, SpecialChannelEnum.verify)
    if verify_channel is not None:
        message = await verify_channel.send(embed=discord_embeds.new_user_to_verify_embed(member))
        await message.add_reaction("✅")
