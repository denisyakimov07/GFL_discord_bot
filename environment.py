from dotenv import load_dotenv
import os

load_dotenv(verbose=True)


class _Environment:
    DISCORD_BOT_TOKEN: str
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    DISCORD_PUBLIC_KEY: str
    DISCORD_BASE_URL: str
    APEX_KEY: str
    API_CLIENT_ID: str
    API_CLIENT_SECRET: str
    PORT: int
    API_BASE_URL: str

    def __init__(self):
        self.DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        self.DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
        self.DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
        self.DISCORD_PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')
        self.DISCORD_BASE_URL = os.getenv('DISCORD_BASE_URL')

        self.APEX_KEY = os.getenv('APEX_KEY')

        self.API_BASE_URL = os.getenv('API_BASE_URL')
        self.API_CLIENT_ID = os.getenv('API_CLIENT_ID')
        self.API_CLIENT_SECRET = os.getenv('API_CLIENT_SECRET')
        self.PORT = int(os.getenv('PORT') or 8082)

    def __str__(self):
        return f'DISCORD_BOT_TOKEN={self.DISCORD_BOT_TOKEN}\nDISCORD_CLIENT_ID={self.DISCORD_CLIENT_ID}'


__environment = _Environment()


def get_env():
    return __environment
