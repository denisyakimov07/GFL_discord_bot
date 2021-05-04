import logging

import discord

from discord.ext import commands

from api import model_api_service
from discord_client import client
from discord_server_settings_service import discord_server_settings_service
from environment import get_env
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
        await ctx.send('Please add a picture attachment')
        return

    user = get_user_by_discord_member(ctx.message.author)
    if user is None:
        await ctx.message.author.send(
            f'To participate in North Star\'s event, you first must register! Click this link to register via Discord: '
            f'{get_env().WEB_BASE_URL}/authredirect/discord\n\nAfter clicking the link, you will be redirected to '
            f'Discord\'s site to authenticate and redirected again to the North Star website.\n\n'
            f'After registering, please resubmit your proof using the '
            f'!proof command')
        await ctx.message.delete()
        await ctx.send('You must be a registered user to submit proof. Please check your messages for more details.')
        return
    else:
        first_event = model_api_service.find_one(GameEvent)
        if first_event is None:
            log.warning('No event was found')
            return

        model_api_service.create_one(
            GameEventProof.construct(user=user.id, url=ctx.message.attachments[0].url, event=first_event.id)
        )
        await ctx.send('Proof has been submitted for review')
