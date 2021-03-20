import requests
import config
import json
import time



def get_new_access_token():
    body = {"client_id": config.ESPORT_ID,
            "client_secret": config.ESPORT_SECRET_KEY_API,
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
            print(token)
            # token can be expired.
            self.refresh_token()
        return self.token


access_token = AccessToken()
token = access_token.get_token()


# 401
HEADER = {"Authorization": f"{token}",
          "Content-Type": "application/json"
          }
BASE_URL = "https://gamersforlife.herokuapp.com/api/model/"
GET_NEW_TOKEN_URL = "oauth/token"
DiscordUser = "DiscordUser"


def get_user_by_id_from_api(new_user):
    params = {"q":
                  json.dumps({"memberId": f"{new_user['memberId']}"})
              }
    try:
        check_user = requests.get(f'{BASE_URL}DiscordUser', headers=HEADER, params=params)
        print(check_user.json())
        if len(check_user.json()["data"]) == 0:
            print(f"User was no found {new_user}.")
            return False
        else:
            print(f"User was found {new_user}.")
            return True
    except:
        print(f"Cant check user")


def create_discord_user_api(new_user):
    user_status = get_user_by_id_from_api(new_user)
    print(token)
    if not user_status:
        resp = requests.post(f'{BASE_URL}DiscordUser', headers=HEADER, json=new_user)
        if resp.status_code == 200:
            print(resp.json())
        else:
            print(f"User was create {resp.status_code} {resp.json()}.")
    else:
        pass



def delete_user():
    check_user = requests.delete(f'{BASE_URL}DiscordUser/{"6053cb7f1a633f001cf7c2d9"}', headers=HEADER)
    print(check_user)
    print(check_user.json())
