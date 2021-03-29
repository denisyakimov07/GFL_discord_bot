import os

import discord
import requests

import json
import time

from dotenv import load_dotenv
from typing import List

load_dotenv()

ESPORT_ID = os.getenv("API_CLIENT_ID")
ESPORT_SECRET_KEY_API = os.getenv("API_CLIENT_SECRET")
API_BASE_URL = os.getenv('API_BASE_URL')


def get_new_access_token():
    body = {"client_id": ESPORT_ID,
            "client_secret": ESPORT_SECRET_KEY_API,
            "scope": "discord",
            "grant_type": "client_credentials"
            }

    print(body)
    try:
        resp = requests.post(f'{API_BASE_URL}/oauth/token', json=body)
        print(resp.json())
        access_token = resp.json()['accessToken']
        if resp.status_code == 200:
            print("New token was create")
            print(resp.json())
            return f"Bearer {access_token}"
        else:
            print(f"Failed to create new token{resp.status_code}{resp.json()}")
    except:
        print(f"resp was not create")


class AccessToken:
    TOKEN_TTL = 60 * 60 - 60

    def __init__(self):
        self.token = get_new_access_token()
        self.token_gen_time = time.time()

    def refresh_token(self):
        self.token = get_new_access_token()
        self.token_gen_time = time.time()  # When token was made

    def get_token(self):
        if time.time() > self.token_gen_time + self.TOKEN_TTL:
            print(f"time {time.time()} - {self.token_gen_time + self.TOKEN_TTL}")
            print(self.token)
            # token can be expired.
            self.refresh_token()
        print(self.token)
        print(f"time {time.time()} - {self.token_gen_time + self.TOKEN_TTL}")
        return self.token


access_token = AccessToken()

BASE_URL = "https://gamersforlife.herokuapp.com/api/model/"
GET_NEW_TOKEN_URL = "oauth/token"
DiscordUser = "DiscordUser"


def get_user_status_by_id_from_api(new_user):
    header = {"Authorization": f"{access_token.get_token()}"}
    params = {"q":
                  json.dumps({"memberId": f"{new_user['memberId']}"})
              }
    try:
        check_user = requests.get(f'{os.getenv("API_BASE_URL")}/api/model/DiscordUser', headers=header, params=params)
        if len(check_user.json()["data"]) == 0:
            print(f"User was no found {new_user}.")
            return False
        else:
            print(f"User was found {new_user}.")
            return True
    except:
        print(f"Cant check user")


# Checks to see if a webhook subscription exists and creates it if it does not
def check_webhook_subscriptions():
    headers = {"Authorization": f"{access_token.get_token()}"}
    url = f'{os.getenv("API_BASE_URL")}/api/model/WebhookSubscription'
    webhook_url = f'{os.getenv("BASE_URL")}/discordserversettings/updateById'
    params = {'q': json.dumps({'client': os.getenv('API_CLIENT_ID'), 'url': webhook_url})}
    get_request = requests.get(url, headers=headers, params=params)
    response_body = get_request.json()
    if response_body['totalCount'] == 0:
        # Create webhook
        body = {'client': os.getenv('API_CLIENT_ID'), 'url': webhook_url, 'modelOperations': ['updateById'],
                'modelName': 'DiscordServerSettings'}
        try:
            requests.post(url, json=body, headers=headers)
        except:
            print('Failed to create webhook')


def get_or_create_discord_server_settings(guilds: list) -> dict:
    server_models_dict = {}

    guild_ids = list(map(lambda x: str(x.id), guilds))
    params = {
        'q': json.dumps({'guildId': {'$in': guild_ids}}),
        'populate': json.dumps(['roles', 'verificationRoles'])
    }

    headers = {"Authorization": f"{access_token.get_token()}"}

    url = f'{os.getenv("API_BASE_URL")}/api/model/DiscordServerSettings'
    get_request = requests.get(url, headers=headers, params=params)
    body = get_request.json()

    # Discord Server Settings that already exist
    found_guild_ids: list = list(map(lambda x: x['guildId'], body['data']))

    # Body models to create in API
    create_many_body: list = []

    for guild in guilds:
        guild_id_str = str(guild.id)
        if guild_id_str not in found_guild_ids:
            print(f'Need to create DiscordServerSettings for guild {guild.id} ({guild.name})')

            create_many_body.append({
                'name': guild.name,
                'guildId': guild_id_str,
            })
        else:
            discord_server_settings = [x for x in body['data'] if x['guildId'] == guild_id_str][0]
            server_models_dict[discord_server_settings['guildId']] = discord_server_settings

    if len(create_many_body) > 0:
        post_request = requests.post(url, json=create_many_body, headers=headers)
        body = post_request.json()
        for guild_model in body:
            server_models_dict[guild_model['guildId']] = guild_model

    add_roles_to_server_settings(guilds, server_models_dict)
    return server_models_dict


def add_roles_to_server_settings(guilds: List[discord.Guild], server_models_dict: dict):
    headers = {"Authorization": f"{access_token.get_token()}"}

    create_many_body = []

    for guild in guilds:
        server_settings = server_models_dict[str(guild.id)]

        roles_dict = {}

        for role in guild.roles:
            roles_in_api = server_settings['roles'] or []
            existing_role = next(iter(filter(lambda x: x['roleId'] == str(role.id), roles_in_api)), None)
            if existing_role is None:
                create_many_body.append({
                    'guildId': server_settings['guildId'],
                    'roleId': str(role.id),
                    'name': role.name
                })

    if len(create_many_body) > 0:
        url = f'{os.getenv("API_BASE_URL")}/api/model/DiscordRole'
        put_response = requests.post(url, headers=headers, json=create_many_body)
        if put_response.status_code != 200:
            print(f'Failed to create DiscordRole role\'s: {put_response.json()}')


def create_discord_user_api(new_user):
    header = {"Authorization": f"{access_token.get_token()}"}
    user_status = get_user_status_by_id_from_api(new_user)
    if not user_status:
        resp = requests.post(f'{BASE_URL}DiscordUser', headers=header, json=new_user)
        if resp.status_code == 200:
            print(f"User was create {new_user}.")
        else:
            print(f"User was not create {resp.status_code} {resp.json()}.")
    else:
        print(f"User already exist {new_user}")


def delete_user(user_id):
    header = {"Authorization": f"{access_token.get_token()}"}
    check_user = requests.delete(f'{BASE_URL}DiscordUser/{user_id}', headers=header)
    print(check_user)
    print(check_user.json())


def add_discord_time_log(user_time_log, status):
    header = {"Authorization": f"{access_token.get_token()}"}
    params = {"q":
                  json.dumps({"memberId": f"{user_time_log['memberId']}"})
              }
    check_user = requests.get(f'{BASE_URL}DiscordUser', headers=header, params=params)
    user_id = check_user.json()["data"][0]["id"]
    new_user_time_log = {
        "discordUser": f"{user_id}",
        "memberId": f"{user_time_log['memberId']}",
        "status": status,
    }
    resp = requests.post(f'{BASE_URL}DiscordOnlineTimeLog', headers=header, json=new_user_time_log)
    print(f"DiscordOnlineTimeLog {resp.status_code} {resp.json()}.")


def add_discord_stream_time_log(user_time_log, status):
    header = {"Authorization": f"{access_token.get_token()}"}
    params = {"q":
                  json.dumps({"memberId": f"{user_time_log['memberId']}"})
              }
    check_user = requests.get(f'{BASE_URL}DiscordUser', headers=header, params=params)
    user_id = check_user.json()["data"][0]["id"]
    new_user_time_log = {
        "discordUser": f"{user_id}",
        "memberId": f"{user_time_log['memberId']}",
        "status": status,
    }
    resp = requests.post(f'{BASE_URL}DiscordOnlineStreamTimeLog', headers=header, json=new_user_time_log)
    print(f"DiscordOnlineTimeLog {resp.status_code} {resp.json()}.")


def get_user_api_id_by_discord_id(user):
    header = {"Authorization": f"{access_token.get_token()}"}
    params = {"q":
                  json.dumps({"memberId": f"{user['memberId']}"})
              }
    pass
