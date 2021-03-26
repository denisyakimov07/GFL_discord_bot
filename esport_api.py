import os

import requests

import json
import time

from dotenv import load_dotenv
load_dotenv()

ESPORT_ID = os.getenv("ESPORT_ID")
ESPORT_SECRET_KEY_API = os.getenv("ESPORT_SECRET_KEY_API")


def get_new_access_token():
    body = {"client_id": ESPORT_ID,
            "client_secret": ESPORT_SECRET_KEY_API,
            "scope": "discord",
            "grant_type": "client_credentials"
            }
    try:
        resp = requests.post(f'https://gamersforlife.herokuapp.com/oauth/token', json=body)
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
            print(token)
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
        check_user = requests.get(f'{BASE_URL}DiscordUser', headers=header, params=params)
        if len(check_user.json()["data"]) == 0:
            print(f"User was no found {new_user}.")
            return False
        else:
            print(f"User was found {new_user}.")
            return True
    except:
        print(f"Cant check user")


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