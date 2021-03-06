import logging
import threading

from flask import Flask, request
from waitress import serve

from discord_server_settings_service import discord_server_settings_service
from environment import get_env

from esport_api import check_webhook_subscriptions
from models import DiscordServerSettings

app = Flask(__name__)

check_webhook_subscriptions()

log = logging.getLogger('HttpServer')


@app.route('/discordserversettings', methods=['POST'])
def discord_server_settings_update_by_id_webhook():
    discord_server_settings = DiscordServerSettings.parse_raw(request.data)

    discord_server_settings_service.refresh_by_discord_server_settings_id(discord_server_settings.id)
    log.info('[WebhooksCallback] Updating DiscordServerSettings', discord_server_settings.name)

    return {'success': True}


def start_server():
    log.info(f'Listening on port {get_env().PORT}')
    serve(app, host='0.0.0.0', port=get_env().PORT)


def start_server_thread():
    log.info('Starting server thread')
    api_server_thread = threading.Thread(target=start_server, args=())
    api_server_thread.start()
