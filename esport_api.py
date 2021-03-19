import requests
import config
import json
import time





acc_token = AccessToken()
# 401
HEADER = {"Authorization": f"Bearer {acc_token.token}",
          "Content-Type": "application/json"
          }
BASE_URL = "https://gamersforlife.herokuapp.com/api/model/"
GET_NEW_TOKEN_URL = "oauth/token"
DiscordUser = "DiscordUser"


def get_user_by_id_from_api(new_user):
    params = {"q":
                  json.dumps({"memberId": f"{new_user['memberId']}"})
              }
    check_user = requests.get(f'{BASE_URL}DiscordUser', headers=HEADER, params=params)
    if check_user.status_code == 401:
        check_user = requests.get(f'{BASE_URL}DiscordUser', headers=HEADER, params=params)
    if len(check_user.json()["data"]) == 0:
        return False
    else:
        return True


def create_discord_user_api(new_user):
    user_status = get_user_by_id_from_api(new_user)
    print(acc_token.token)
    if not user_status:
        resp = requests.post(f'{BASE_URL}DiscordUser', headers=HEADER, json=new_user)
        if resp.status_code == 200:
            print(resp.json())
        else:
            print(resp.status_code)
            print(resp.json())
    else:
        pass


def get_new_access_token():
    body = {"client_id": config.ESPORT_ID,
            "client_secret": config.ESPORT_SECRET_KEY_API,
            "scope": "discord",
            "grant_type": "client_credentials"
            }
    try:
        resp = requests.post(f'https://gamersforlife.herokuapp.com/oauth/token', json=body)
        access_token = resp.json()['accessToken']
        if resp.status_code == 200:
            print("New token was create")
            print(resp.json())
            return f"Bearer  {access_token}"
        else:
            print(f"Failed to create new token{resp.status_code}{resp.json()}")
    except:
        print(f"resp was not create")


new_user = {"memberName": "Yanis07 (Denis)#1771",
            "memberId": "339287982320254976",
            "avatarUrl": "https://cdn.discordapp.com/avatars/339287982320254976/0642007edaec7940b9f6ffd398a20962.webp?size=1024"
            }

create_discord_user_api(new_user)


def delete_user():
    check_user = requests.delete(f'{BASE_URL}DiscordUser/{"6053cb7f1a633f001cf7c2d9"}', headers=HEADER)
    print(check_user)
    print(check_user.json())
