import requests
from environment import get_env

APEX_URL = f"https://public-api.tracker.gg/v2/apex/standard/profile/"


def get_apex_rank(name):
    platform = "origin"
    try:
        request = requests.get(f"{APEX_URL.lower()}{platform.lower()}/{name.lower()}",
                               headers={"TRN-Api-Key": get_env().APEX_KEY})
        rang = request.json()
        print(rang)
        return str(rang['data']["segments"][0]["stats"]['rankScore']["metadata"]['rankName'])
    except Exception as ex:
        print(ex)
        return -1  # "Wrong name dude, you have to type your Origin name or tracker.gg is broken."
