import logging
from discord_commands import *
from discord_events import *

from discord_client import client
from environment import get_env

log = logging.getLogger('DiscordBot')


def start_discord_bot():
    log.info('Starting Discord Bot')
    client.run(get_env().DISCORD_BOT_TOKEN)
