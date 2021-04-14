import logging
import discord
import discord_embeds

from discord_client import client
from discord_helper_utils import get_channel_by_special_channel, try_to_verify_member
from models import SpecialChannelEnum

log = logging.getLogger('DiscordBot')

roles_assignment_setup = {"massage_id": 828861933280428043,
                          "emoji_to_role": {"Apex": 818814719854116914,
                                            "WorldofWarcraft": 824845946684571719,
                                            "CallofDuty": 824846357214396477,
                                            "Fortnite": 824852084691566613,
                                            "LeagueofLegends": 824846490350256199,
                                            "Overwatch": 824845796196352033,
                                            "Valorant": 824845603687104512,
                                            "HuntShowdown": 824846176154943499,
                                            "Minecraft": 818824441903185950,
                                            "EscapeFromTarkov": 824846668406456351,
                                            }}


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    guild = client.get_guild(payload.guild_id)
    verify_channel = get_channel_by_special_channel(guild, SpecialChannelEnum.verify)

    if payload.channel_id == verify_channel.id and str(payload.emoji.name) == '✅' and client.user.id != payload.user_id:
        message = await verify_channel.fetch_message(payload.message_id)
        member_to_verify: discord.Member = await guild.fetch_member(int(message.embeds[0].title))
        error_msg_or_success = await try_to_verify_member(payload.channel_id, payload.member, member_to_verify)
        if error_msg_or_success is True:
            await message.delete()
            await verify_channel.send(embed=discord_embeds.embeds_for_verify_user(member_to_verify, payload.member))
        elif isinstance(error_msg_or_success, str):
            await verify_channel.send(error_msg_or_success)

    elif payload.message_id == roles_assignment_setup['massage_id']:
        try:
            if payload.emoji.name in roles_assignment_setup["emoji_to_role"]:
                member_add_role = payload.member
                role = discord.utils.get(member_add_role.guild.roles,
                                         id=roles_assignment_setup["emoji_to_role"][payload.emoji.name])
                await member_add_role.add_roles(role)
                log.debug(f"Role was added {member_add_role} - {role}")
        except Exception as ex:
            log.error(f"Role was not added - {ex}")
