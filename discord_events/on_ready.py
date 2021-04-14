import logging

from discord_client import client

log = logging.getLogger('DiscordBot')


@client.event
async def on_ready():
    log.info(f'Logged in as {client.user.name}')
