import logging
import time
import requests

from environment import get_env

log = logging.getLogger('Access Token')


def get_new_access_token():
    body = {
        "client_id": get_env().API_CLIENT_ID,
        "client_secret": get_env().API_CLIENT_SECRET,
        "scope": "discord webhooks",
        "grant_type": "client_credentials"
    }
    try:
        resp = requests.post(f'{get_env().API_BASE_URL}/oauth/token', json=body)
        new_access_token = resp.json()['accessToken']
        if resp.status_code == 200:
            log.info("New token was created")
            return f"Bearer {new_access_token}"
        else:
            log.fatal(f"Failed to create new token{resp.status_code}{resp.json()}")
    except Exception as ex:
        log.fatal(f"Token (resp) was not create {ex}")


class AccessToken:
    TOKEN_TTL = 60 * 60 - 60
    token_gen_time: float

    def __init__(self):
        self.token = get_new_access_token()
        self.token_gen_time = time.time()

    def refresh_token(self):
        self.token = get_new_access_token()
        self.token_gen_time = time.time()  # When token was made
        log.info(f"Generate new token token")

    def get_token(self):
        if time.time() > self.token_gen_time + self.TOKEN_TTL:
            # token can be expired.
            self.refresh_token()
            log.info(f"Token expire")
        log.debug(f"Return token")
        return self.token
