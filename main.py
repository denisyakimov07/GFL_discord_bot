import threading

from discord_bot import start_discord_bot
from http_server import start_server_thread, app

if __name__ == '__main__':
    discord_bot_thread = threading.Thread(target=start_discord_bot, args=())
    discord_bot_thread.start()
    start_server_thread()
