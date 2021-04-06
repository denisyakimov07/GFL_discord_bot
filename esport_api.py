import datetime

import discord
import requests

import json
import time

from typing import List, Dict

from pydantic.tools import parse_obj_as

from environment import get_env
from models import DiscordServerSettings, Pagination, DiscordRole, DiscordUser, WebhookSubscription

cached_get_user_api_id_by_discord_id = {}


def get_new_access_token():
    body = {"client_id": get_env().API_CLIENT_ID,
            "client_secret": get_env().API_CLIENT_SECRET,
            "scope": "discord webhooks",
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


def check_webhook_subscriptions():
    """
    Checks to see if a webhook subscription exists and creates it if it does not
    """
    headers = {"Authorization": f"{access_token.get_token()}"}
    webhook_url = f'{get_env().BASE_URL}/discordserversettings'
    url = f'{get_env().API_BASE_URL}/api/webhooks'
    jsonBody = {
        'url': webhook_url,
        'leaseSeconds': 864000, # 10 days in seconds
        'topic': 'discordserversettings',
        'secret': 'monkeybars',
        'mode': 'subscribe',
    }
    request = requests.post(url, json=jsonBody, headers=headers)

    if request.status_code == 200:
        subscription = WebhookSubscription.parse_raw(request.text)
        print('Confirmed subscription', subscription)
    else:
        print(f'Failed to confirm webhook subscription: {request.text}')


def get_all_discord_server_settings() -> Pagination[DiscordServerSettings]:
    params = {
        'populate': json.dumps(['roles', 'verificationRoles'])
    }
    headers = {"Authorization": f"{access_token.get_token()}"}
    url = f'{get_env().API_BASE_URL}/api/model/DiscordServerSettings'
    get_request = requests.get(url, headers=headers, params=params)
    pagination: Pagination[DiscordServerSettings] = Pagination[DiscordServerSettings].parse_raw(get_request.text)
    return pagination


def get_discord_server_settings(discord_server_settings_id: str) -> DiscordServerSettings:
    params = {
        'populate': json.dumps(['roles', 'verificationRoles'])
    }

    headers = {"Authorization": f"{access_token.get_token()}"}
    url = f'{get_env().API_BASE_URL}/api/model/DiscordServerSettings/{discord_server_settings_id}'
    get_request = requests.get(url, headers=headers, params=params)
    server_settings: DiscordServerSettings = DiscordServerSettings.parse_raw(get_request.text)
    return server_settings


def get_or_create_discord_server_settings(guild: discord.Guild) -> DiscordServerSettings:
    populate = json.dumps(['roles', 'verificationRoles'])

    params = {
        'q': json.dumps({'guildId': str(guild.id)}),
        'populate': populate
    }
    headers = {"Authorization": f"{access_token.get_token()}"}

    url = f'{get_env().API_BASE_URL}/api/model/DiscordServerSettings'
    get_request = requests.get(url, headers=headers, params=params)
    pagination: Pagination[DiscordServerSettings] = Pagination[DiscordServerSettings].parse_raw(get_request.text)

    server_settings: DiscordServerSettings

    if pagination.total_count == 0:
        new_body = DiscordServerSettings()
        new_body.guild_id = str(guild.id)
        new_body.name = guild.name
        request = requests.post(url, new_body, headers=headers, params={'populate': populate})
        server_settings = DiscordServerSettings.parse_raw(request.text)

    return server_settings


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


def new_user_time_log(user_time_log, status):
    time_log = {
        "discordUser": f"{get_user_api_id_by_discord_id(user_time_log)}",
        "memberId": f"{user_time_log['memberId']}",
        "status": status,
    }
    return time_log


def add_discord_time_log(user_add_time_log, status):
    if get_user_api_id_by_discord_id(user_add_time_log) is not None:
        resp = requests.post(f'{get_env().API_BASE_URL}/api/model/DiscordOnlineTimeLog',
                             headers=get_header(),
                             json=new_user_time_log(user_add_time_log, status))
        print(f"DiscordOnlineTimeLog {resp.status_code} {resp.json()}.")
    else:
        print(f"Time log was not added - {user_add_time_log} - is None")


def add_discord_stream_time_log(user_stream_log, status):
    if get_user_api_id_by_discord_id(user_stream_log) is not None:
        resp = requests.post(f'{get_env().API_BASE_URL}/api/model/DiscordOnlineStreamTimeLog', headers=get_header(),
                             json=new_user_time_log(user_stream_log, status))
        print(f"DiscordOnlineStreamTimeLog {resp.status_code} {resp.json()}.")
    else:
        print(f"Stream log was not added - {user_stream_log} - is None")


def get_user_api_id_by_discord_id(user_discord):
    if str(user_discord['memberId']) in cached_get_user_api_id_by_discord_id:
        print(
            f"User_api_id get from cache {user_discord['memberId']} = {cached_get_user_api_id_by_discord_id[user_discord['memberId']]}")
        return cached_get_user_api_id_by_discord_id[user_discord['memberId']]
    else:
        params = {"q": json.dumps({"memberId": f"{user_discord['memberId']}"})}
        try:
            check_user = requests.get(f'{get_env().API_BASE_URL}/api/model/DiscordUser',
                                      headers=get_header(),
                                      params=params)
            if len(check_user.json()["data"]) > 0:
                user_id = check_user.json()["data"][0]["id"]
                print(f"User found discord id - {user_discord['memberId']}, api_id - {user_id}")
                cached_get_user_api_id_by_discord_id[str(user_discord['memberId'])] = str(user_id)
                return user_id
            else:
                print(f"User is not found discord id - {user_discord['memberId']}")
        except Exception as ex:
            print(f"Bad request, discord id - {user_discord['memberId']}, Exception {ex}.")
            return


def verified_by_member(new_user, admin_user):
    try:
        user_verified_by = {"verifiedBy": f"{get_user_api_id_by_discord_id(admin_user)}"}
        resp = requests.put(f'{get_env().API_BASE_URL}/api/model/DiscordUser/{get_user_api_id_by_discord_id(new_user)}',
                            headers=get_header(),
                            json=user_verified_by)
        print(f"User get verified {new_user} by {admin_user}---{resp}")
    except Exception as ex:
        print(ex)


def get_total_verifications_in_last_24_hours(user_discord_id):
    member = {'memberId': user_discord_id}
    right_now = datetime.datetime.utcnow()
    a_day_ago = right_now - datetime.timedelta(hours=24)
    params = {"q": json.dumps({f"{'verifiedBy'}": f"{get_user_api_id_by_discord_id(member)}",
                               f"{'updatedAt'}": {'$gte': f'{a_day_ago.isoformat()}'}})}
    count = requests.get(f'{get_env().API_BASE_URL}/api/model/DiscordUser',
                         headers=get_header(),
                         params=params)
    pagination: Pagination[DiscordUser] = Pagination[DiscordUser].parse_raw(count.text)
    return pagination.total_count
