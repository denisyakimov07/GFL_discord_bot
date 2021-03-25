from dotenv import load_dotenv
load_dotenv(verbose=True)
import os


class _Environment:
    DISCORD_BOT_TOKEN: str
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    DISCORD_PUBLIC_KEY: str
    API_CLIENT_ID: str
    API_CLIENT_SECRET: str
    PORT: int

    def __init__(self):
        self.DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        self.DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
        self.DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
        self.DISCORD_PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

        self.API_CLIENT_ID = os.getenv('API_CLIENT_ID')
        self.API_CLIENT_SECRET = os.getenv('API_CLIENT_SECRET')
        self.PORT = int(os.getenv('PORT') or 8082)

    def __str__(self):
        return f'DISCORD_BOT_TOKEN=${self.DISCORD_BOT_TOKEN}\nDISCORD_CLIENT_ID=${self.DISCORD_CLIENT_ID}'

__environment = _Environment()

def getEnv():
    return __environment
