import discord

import discord_embeds
from discord_client import client
from discord_helper_utils import try_to_verify_member
from discord_server_settings_service import discord_server_settings_service
from models import SpecialChannelEnum


@client.command()
async def verify(ctx: discord.ext.commands.Context, user_name=None):
    server_settings = discord_server_settings_service.server_settings[str(ctx.guild.id)]
    verify_channel_id = server_settings.get_special_channel(SpecialChannelEnum.verify)
    if verify_channel_id is None:
        # TODO: Maybe warn user that the special channel isn't set?
        return

    if str(ctx.channel.id) == verify_channel_id:
        if not server_settings.can_member_verify(ctx.message.author):
            return await ctx.send('No permission to verify users')

        if len(ctx.message.mentions) == 0:
            return await ctx.send("You didn't mention anyone. Try !verify @{MEMBER}")

        member_to_verify_id = ctx.message.mentions[0].id
        member_to_verify = await ctx.guild.fetch_member(member_to_verify_id)
        if member_to_verify is None:
            return await ctx.send('Could not find that user')

        error_msg_or_success = await try_to_verify_member(ctx.channel.id, ctx.message.author, member_to_verify)
        if error_msg_or_success is True:
            await ctx.send(embed=discord_embeds.embeds_for_verify_user(member_to_verify, ctx.message.author))
        elif isinstance(error_msg_or_success, str):
            await ctx.send(error_msg_or_success)
