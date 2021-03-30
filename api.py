from flask import Flask, request
from waitress import serve

from environment import getEnv
import threading

app = Flask(__name__)


@app.route('/discordserversettings/updateById', methods=['POST'])
def discord_server_settings_update_by_id_webhook(guild_id: str):
    data = request.json
    print(data)
    return {'success': True}


def start_server():
    print(f'Listening on port {getEnv().PORT}')
    serve(app, host='0.0.0.0', port=getEnv().PORT)


api_server_thread = threading.Thread(target=start_server, args=())
api_server_thread.start()
