from discord_bot import start_discord_bot_thread
from http_server import start_server_thread

if __name__ == '__main__':
    start_discord_bot_thread()
    start_server_thread()
