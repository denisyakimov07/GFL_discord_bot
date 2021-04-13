import logging

from discord_bot import start_discord_bot
from http_server import start_server_thread

logging.getLogger().setLevel(logging.DEBUG)

if __name__ == '__main__':
    start_server_thread()
    start_discord_bot()

