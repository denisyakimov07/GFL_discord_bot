import datetime
import logging
from typing import Union

import discord
import requests
import json

from api import model_api_service
from environment import get_env
from models import DiscordServerSettings, Pagination, DiscordUser, WebhookSubscription, DiscordOnlineStreamTimeLog, \
    User, GameEventProof

cached_get_user_api_id_by_discord_id = {}

log = logging.getLogger('API')


def get_user_status_by_id_from_api(new_user):
    params = {"q": json.dumps({"memberId": f"{new_user['memberId']}"})}

    try:
        check_user = requests.get(f'{get_env().API_BASE_URL}/api/model/DiscordUser',
                                  headers=model_api_service.get_headers(),
                                  params=params)
        if len(check_user.json()["data"]) == 0:
            log.info(f"User was no found {new_user}.")
            return False
        else:
            log.info(f"User was found {new_user}.")
            return True
    except Exception as ex:
        log.error(f"Cant check user {ex}")


def check_webhook_subscriptions():
    """
    Checks to see if a webhook subscription exists and creates it if it does not
    """
    webhook_url = f'{get_env().BASE_URL}/discordserversettings'
    url = f'{get_env().API_BASE_URL}/api/webhooks'
    jsonBody = {
        'url': webhook_url,
        'leaseSeconds': 864000,  # 10 days in seconds
        'topic': 'discordserversettings',
        'secret': 'monkeybars',
        'mode': 'subscribe',
    }
    request = requests.post(url, json=jsonBody, headers=model_api_service.get_headers())

    if request.status_code == 200:
        subscription = WebhookSubscription.parse_raw(request.text)
        log.info('Confirmed webhook subscription', subscription)
    else:
        log.error(f'Failed to confirm webhook subscription: {request.text}')


def get_user_by_discord_user_id(discord_user_id: str) -> Union[None, User]:
    return model_api_service.find_one(User, {'discordUser': discord_user_id})


def get_user_by_discord_member(member: discord.Member) -> Union[None, User]:
    discord_user = get_create_discord_user_by_member(member)
    return get_user_by_discord_user_id(discord_user.id)


def get_all_discord_server_settings() -> Pagination[DiscordServerSettings]:
    return model_api_service.find_many(DiscordServerSettings, populate=['verificationRoles'])


def get_discord_server_settings(discord_server_settings_id: str) -> DiscordServerSettings:
    return model_api_service.find_by_id(DiscordServerSettings, discord_server_settings_id,
                                        populate=['verificationRoles'])


def get_or_create_discord_server_settings(guild: discord.Guild) -> DiscordServerSettings:
    pagination = model_api_service.find_many(DiscordServerSettings, query={'guildId': str(guild.id)})

    if pagination.total_count == 0:
        new_body = DiscordServerSettings.construct(guild_id=str(guild.id), name=guild.name)
        return model_api_service.create_one(new_body)
    else:
        return pagination.data[0]


def get_create_discord_user_by_member(member: discord.Member) -> DiscordUser:
    discord_user = model_api_service.find_one(DiscordUser, {'memberId': str(member.id)})
    if discord_user is None:
        model = DiscordUser.construct(
            member_id=str(member.id),
            member_name=member.display_name,
            avatar_url=f'{member.avatar_url.BASE}{member.avatar_url._url}'
        )
        discord_user = model_api_service.create_one(model)
    return discord_user


def create_discord_user_api(new_user):
    user_status = get_user_api_id_by_discord_id(new_user)
    if not user_status:
        resp = requests.post(f'{get_env().API_BASE_URL}/api/model/DiscordUser', headers=model_api_service.get_headers(),
                             json=new_user)
        if resp.status_code == 200:
            log.info(f"New user was create {new_user}.")
        else:
            log.error(f"New user was not create {resp.status_code} {resp.json()}.")
    else:
        log.error(f"User already exist {new_user}")


def new_user_time_log(user_time_log, status):
    time_log = {
        "discordUser": f"{get_user_api_id_by_discord_id(user_time_log)}",
        "memberId": f"{user_time_log['memberId']}",
        "status": status,
    }
    return time_log


def add_discord_time_log_by_member(member: discord.Member, status: bool):
    model_api_service.create_one(DiscordOnlineStreamTimeLog.construct(
        member_id=str(member.id),
        status=status,
    ))


def add_discord_time_log(user_add_time_log, status):
    if get_user_api_id_by_discord_id(user_add_time_log) is not None:
        resp = requests.post(f'{get_env().API_BASE_URL}/api/model/DiscordOnlineTimeLog',
                             headers=model_api_service.get_headers(),
                             json=new_user_time_log(user_add_time_log, status))
        log.info(f"DiscordOnlineTimeLog {resp.status_code} {resp.json()}.")
    else:
        log.error(f"Time log was not added - {user_add_time_log} - is None")


def add_discord_stream_time_log(user_stream_log, status):
    if get_user_api_id_by_discord_id(user_stream_log) is not None:
        resp = requests.post(f'{get_env().API_BASE_URL}/api/model/DiscordOnlineStreamTimeLog',
                             headers=model_api_service.get_headers(),
                             json=new_user_time_log(user_stream_log, status))
        log.info(f"DiscordOnlineStreamTimeLog {resp.status_code} {resp.json()}.")
    else:
        log.error(f"Stream log was not added - {user_stream_log} - is None")


def get_user_api_id_by_discord_id(user_discord):
    if str(user_discord['memberId']) in cached_get_user_api_id_by_discord_id:
        log.info(
            f"User_api_id get from cache {user_discord['memberId']} = {cached_get_user_api_id_by_discord_id[user_discord['memberId']]}")
        return cached_get_user_api_id_by_discord_id[user_discord['memberId']]
    else:
        params = {"q": json.dumps({"memberId": f"{user_discord['memberId']}"})}
        try:
            check_user = requests.get(f'{get_env().API_BASE_URL}/api/model/DiscordUser',
                                      headers=model_api_service.get_headers(),
                                      params=params)
            if len(check_user.json()["data"]) > 0:
                user_id = check_user.json()["data"][0]["id"]
                log.info(f"User found discord id - {user_discord['memberId']}, api_id - {user_id}")
                cached_get_user_api_id_by_discord_id[str(user_discord['memberId'])] = str(user_id)
                return user_id
            else:
                log.error(f"User is not found discord id - {user_discord['memberId']}")
        except Exception as ex:
            log.error(f"Bad request, discord id - {user_discord['memberId']}, Exception {ex}.")
            return


def verify_member(from_member: discord.Member, to_member: discord.Member):
    from_user = get_create_discord_user_by_member(from_member)
    to_user = get_create_discord_user_by_member(to_member)
    model_api_service.update_by_id(DiscordUser, to_user.id, {
        'verifiedBy': from_user.id,
    })


def get_total_verifications_in_last_24_hours(user_discord_id: Union[str, int]):
    if isinstance(user_discord_id, str):
        user_discord_id = str(user_discord_id)

    member = {'memberId': user_discord_id}
    right_now = datetime.datetime.utcnow()
    a_day_ago = right_now - datetime.timedelta(hours=24)
    params = {"q": json.dumps({f"{'verifiedBy'}": f"{get_user_api_id_by_discord_id(member)}",
                               f"{'updatedAt'}": {'$gte': f'{a_day_ago.isoformat()}'}})}
    count = requests.get(f'{get_env().API_BASE_URL}/api/model/DiscordUser',
                         headers=model_api_service.get_headers(),
                         params=params)
    pagination: Pagination[DiscordUser] = Pagination[DiscordUser].parse_raw(count.text)
    return pagination.total_count


def create_proof_by_message(msg: discord.Message):
    model_api_service.create_one(GameEventProof.construct())
