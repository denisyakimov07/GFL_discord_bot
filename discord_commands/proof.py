import logging

import discord

from discord.ext import commands

from api import model_api_service
from discord_client import client
from discord_embeds import user_need_to_reg_on_site_massage_embed, submitted_proof_embed, add_attachment_massage_embed, \
    registered_user_embed
from discord_server_settings_service import discord_server_settings_service
from esport_api import get_user_by_discord_member
from models import SpecialChannelEnum, GameEventProof, GameEvent

log = logging.getLogger('Discord Bot')


@client.command()
async def proof(ctx: discord.ext.commands.Context):
    server_settings = discord_server_settings_service.get_settings_by_guild_id(ctx.guild.id)
    channel_id = server_settings.get_special_channel(SpecialChannelEnum.current_event)
    if int(channel_id) != ctx.channel.id:
        return

    # TODO: For Yanis: Check if url is present in message (search for url regex pattern on google)
    # Check if URL has response

    if len(ctx.message.attachments) == 0:
        await ctx.message.delete()
        await ctx.send(embed=add_attachment_massage_embed(ctx.message.author))
        return

    user = get_user_by_discord_member(ctx.message.author)
    if user is None:
        await ctx.message.author.send(embed=user_need_to_reg_on_site_massage_embed())
        await ctx.message.delete()
        await ctx.send(embed=registered_user_embed(ctx.message.author))
        return
    else:
        first_event = model_api_service.find_one(GameEvent)
        if first_event is None:
            log.warning(f'<@!{ctx.message.author.id}> No event was found')
            return

        model_api_service.create_one(
            GameEventProof.construct(user=user.id, url=ctx.message.attachments[0].url, event=first_event.id,
                                     message=ctx.message.content)
        )
        await ctx.send(embed=submitted_proof_embed(member=ctx.message.author, att_url=ctx.message.attachments[0].url))
