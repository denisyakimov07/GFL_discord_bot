import logging
import discord

from discord_client import client
from discord_events.on_raw_reaction_add import roles_assignment_setup

log = logging.getLogger('DiscordBot')


@client.event
async def on_raw_reaction_remove(payload):
    if payload.message_id in roles_assignment_setup['massage_id']:
        if payload.emoji.name in roles_assignment_setup["emoji_to_role"]:
            guild = client.get_guild(payload.guild_id)
            member_remove_role = await guild.fetch_member(payload.user_id)
            role = discord.utils.get(guild.roles,
                                     id=roles_assignment_setup["emoji_to_role"][payload.emoji.name])
            await member_remove_role.remove_roles(role)
            log.info(f"Role was removed {member_remove_role} - {role}")
