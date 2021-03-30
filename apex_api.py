import os

import requests
from dotenv import load_dotenv
load_dotenv()

APEX_KEY = os.getenv("APEX_KEY")

APEX_URL = f"https://public-api.tracker.gg/v2/apex/standard/profile/"


def get_apex_rank(name):
    platform = "origin"
    try:
        request = requests.get(f"{APEX_URL.lower()}{platform.lower()}/{name.lower()}",
                               headers={"TRN-Api-Key": APEX_KEY})
        rang = request.json()
        print(rang)
        return str(rang['data']["segments"][0]["stats"]['rankScore']["metadata"]['rankName'])
    except:
        return -1  # "Wrong name dude, you have to type your Origin name or tracker.gg is broken."



