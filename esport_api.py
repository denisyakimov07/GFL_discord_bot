import os

import requests

import json
import time

from dotenv import load_dotenv

load_dotenv()

ESPORT_ID = os.getenv("ESPORT_ID")
ESPORT_SECRET_KEY_API = os.getenv("ESPORT_SECRET_KEY_API")
BASE_URL = "https://gamersforlife.herokuapp.com/api/model/"
GET_NEW_TOKEN_URL = "oauth/token"
DiscordUser = "DiscordUser"
cached_get_user_api_id_by_discord_id = {}

def get_new_access_token():
    body = {"client_id": ESPORT_ID,
            "client_secret": ESPORT_SECRET_KEY_API,
            "scope": "discord",
            "grant_type": "client_credentials"
            }
    try:
        resp = requests.post(f'https://gamersforlife.herokuapp.com/oauth/token', json=body)
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


def create_discord_user_api(new_user):
    header = {"Authorization": f"{access_token.get_token()}"}
    user_status = get_user_api_id_by_discord_id(new_user)
    if not user_status:
        resp = requests.post(f'{BASE_URL}DiscordUser', headers=header, json=new_user)
        if resp.status_code == 200:
            print(f"New user was create {new_user}.")
        else:
            print(f"New user was not create {resp.status_code} {resp.json()}.")
    else:
        print(f"User already exist {new_user}")


def add_discord_time_log(user, status):
    header = {"Authorization": f"{access_token.get_token()}"}
    user_api_id = get_user_api_id_by_discord_id(user)
    new_user_time_log = {
        "discordUser": f"{user_api_id}",
        "memberId": f"{user['memberId']}",
        "status": status,
    }
    if user_api_id is not None:
        resp = requests.post(f'{BASE_URL}DiscordOnlineTimeLog', headers=header, json=new_user_time_log)
        print(f"DiscordOnlineTimeLog {resp.status_code} {resp.json()}.")
    else:
        print(f"Time log was not added - {user} - is None")


def add_discord_stream_time_log(user, status):
    header = {"Authorization": f"{access_token.get_token()}"}
    user_api_id = get_user_api_id_by_discord_id(user)
    new_user_time_log = {
        "discordUser": f"{user_api_id}",
        "memberId": f"{user['memberId']}",
        "status": status,
    }
    if user_api_id is not None:
        resp = requests.post(f'{BASE_URL}DiscordOnlineStreamTimeLog', headers=header, json=new_user_time_log)
        print(f"DiscordOnlineStreamTimeLog {resp.status_code} {resp.json()}.")
    else:
        print(f"Stream log was not added - {user} - is None")


def get_user_api_id_by_discord_id(user):

    print (user['memberId'])
    print (cached_get_user_api_id_by_discord_id)

    if str(user['memberId']) in cached_get_user_api_id_by_discord_id:
        print(f"User_api_id get from cache {user['memberId']} = {cached_get_user_api_id_by_discord_id[user['memberId']]}")
        return cached_get_user_api_id_by_discord_id[user['memberId']]
    else:
        header = {"Authorization": f"{access_token.get_token()}"}
        params = {"q":
                      json.dumps({"memberId": f"{user['memberId']}"})
                  }
        try:
            check_user = requests.get(f'{BASE_URL}DiscordUser', headers=header, params=params)
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
