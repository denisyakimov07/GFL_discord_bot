import discord
import requests

import json
import time

from typing import List

from environment import get_env

cached_get_user_api_id_by_discord_id = {}


def get_new_access_token():
    body = {"client_id": get_env().API_CLIENT_ID,
            "client_secret": get_env().API_CLIENT_SECRET,
            "scope": "discord",
            "grant_type": "client_credentials"
            }
    try:
        resp = requests.post(f'{get_env().API_BASE_URL}/oauth/token', json=body)
        new_access_token = resp.json()['accessToken']
        if resp.status_code == 200:
            print("New token was create")
            return f"Bearer {new_access_token}"
        else:
            print(f"Failed to create new token{resp.status_code}{resp.json()}")
    except Exception as ex:
        print(f"Token (resp) was not create {ex}")


class AccessToken:
    TOKEN_TTL = 60 * 60 - 60

    def __init__(self):
        self.token = get_new_access_token()
        self.token_gen_time = time.time()

    def refresh_token(self):
        self.token = get_new_access_token()
        self.token_gen_time = time.time()  # When token was made
        print(f"Generate new token token - {self.token}")

    def get_token(self):
        if time.time() > self.token_gen_time + self.TOKEN_TTL:
            # token can be expired.
            self.refresh_token()
            print(f"Token expire - {self.token}")
        print(f"Return token - {self.token}")
        return self.token


access_token = AccessToken()

GET_NEW_TOKEN_URL = "oauth/token"
DiscordUser = "DiscordUser"


def get_header():
    header = {"Authorization": f"{access_token.get_token()}"}
    return header


def get_user_status_by_id_from_api(new_user):
    params = {"q": json.dumps({"memberId": f"{new_user['memberId']}"})}

    try:
        check_user = requests.get(f'{get_env().API_BASE_URL}/api/model/DiscordUser',
                                  headers=get_header(),
                                  params=params)
        if len(check_user.json()["data"]) == 0:
            print(f"User was no found {new_user}.")
            return False
        else:
            print(f"User was found {new_user}.")
            return True
    except Exception as ex:
        print(f"Cant check user {ex}")


# Checks to see if a webhook subscription exists and creates it if it does not
def check_webhook_subscriptions():
    url = f'{get_env().API_BASE_URL}/api/model/WebhookSubscription'
    webhook_url = f'{get_env().API_BASE_URL}/discordserversettings/updateById'
    params = {'q': json.dumps({'client': get_env().API_CLIENT_ID, 'url': webhook_url})}
    get_request = requests.get(url, headers=get_header(), params=params)
    response_body = get_request.json()
    if response_body['totalCount'] == 0:
        # Create webhook
        body = {'client': get_env().API_CLIENT_ID, 'url': webhook_url, 'modelOperations': ['updateById'],
                'modelName': 'DiscordServerSettings'}
        try:
            requests.post(url, json=body, headers=get_header())
        except Exception as ex:
            print(f'Failed to create webhook {ex}')


def get_or_create_discord_server_settings(guilds: list) -> dict:
    server_models_dict = {}

    guild_ids = list(map(lambda x: str(x.id), guilds))
    params = {
        'q': json.dumps({'guildId': {'$in': guild_ids}}),
        'populate': json.dumps(['roles', 'verificationRoles'])
    }

    headers = {"Authorization": f"{access_token.get_token()}"}

    url = f'{get_env().API_BASE_URL}/api/model/DiscordServerSettings'
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
            print(f'Added DiscordServerSettings for {guild_model["name"]}')

    add_roles_to_server_settings(guilds, server_models_dict)
    return server_models_dict


def add_roles_to_server_settings(guilds: List[discord.Guild], server_models_dict: dict):
    create_many_body = []

    for guild in guilds:
        server_settings = server_models_dict[str(guild.id)]

        # roles_dict = {}

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
        url = f'{get_env().API_BASE_URL}/api/model/DiscordRole'
        put_response = requests.post(url, headers=get_header(), json=create_many_body)
        if put_response.status_code != 200:
            print(f'Failed to create DiscordRole role\'s: {put_response.json()}')
        else:
            print(f'Added roles to guilds: {list(map(lambda x: x.name, guilds))}')


def create_discord_user_api(new_user):
    user_status = get_user_api_id_by_discord_id(new_user)
    if not user_status:
        resp = requests.post(f'{get_env().API_BASE_URL}/api/model/DiscordUser', headers=get_header(), json=new_user)
        if resp.status_code == 200:
            print(f"New user was create {new_user}.")
        else:
            print(f"New user was not create {resp.status_code} {resp.json()}.")
    else:
        print(f"User already exist {new_user}")


def new_user_time_log(user, status):
    time_log = {
        "discordUser": f"{get_user_api_id_by_discord_id(user)}",
        "memberId": f"{user['memberId']}",
        "status": status,
    }
    return time_log


def add_discord_time_log(user, status):
    if get_user_api_id_by_discord_id(user) is not None:
        resp = requests.post(f'{get_env().API_BASE_URL}/api/model/DiscordOnlineTimeLog',
                             headers=get_header(),
                             json=new_user_time_log(user, status))
        print(f"DiscordOnlineTimeLog {resp.status_code} {resp.json()}.")
    else:
        print(f"Time log was not added - {user} - is None")


def add_discord_stream_time_log(user, status):
    if get_user_api_id_by_discord_id(user) is not None:
        resp = requests.post(f'{get_env().API_BASE_URL}/api/model/DiscordOnlineStreamTimeLog', headers=get_header(),
                             json=new_user_time_log(user, status))
        print(f"DiscordOnlineStreamTimeLog {resp.status_code} {resp.json()}.")
    else:
        print(f"Stream log was not added - {user} - is None")


def get_user_api_id_by_discord_id(user):
    if str(user['memberId']) in cached_get_user_api_id_by_discord_id:
        print(
            f"User_api_id get from cache {user['memberId']} = {cached_get_user_api_id_by_discord_id[user['memberId']]}")
        return cached_get_user_api_id_by_discord_id[user['memberId']]
    else:
        params = {"q": json.dumps({"memberId": f"{user['memberId']}"})}
        try:
            check_user = requests.get(f'{get_env().API_BASE_URL}/api/model/DiscordUser',
                                      headers=get_header(),
                                      params=params)
            if len(check_user.json()["data"]) > 0:
                user_id = check_user.json()["data"][0]["id"]
                print(f"User found discord id - {user['memberId']}, api_id - {user_id}")
                cached_get_user_api_id_by_discord_id[str(user['memberId'])] = str(user_id)
                return user_id
            else:
                print(f"User is not found discord id - {user['memberId']}")
        except Exception as ex:
            print(f"Bad request, discord id - {user['memberId']}, Exception {ex}.")
            return


def verified_by_member(new_user_id, admin_user_id):
    user_verified_by = {"verifiedByMemberId": f"{admin_user_id}"}
    resp = requests.put(f'{get_env().API_BASE_URL}/api/model/DiscordUser/{get_user_api_id_by_discord_id(new_user_id)}',
                        headers=get_header(),
                        json=user_verified_by)
    print(resp)
