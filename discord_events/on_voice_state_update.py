import discord_embeds
from discord_client import client
from discord_helper_utils import get_channel_by_special_channel
from discord_server_settings_service import discord_server_settings_service
from esport_api import add_discord_time_log_by_member
from models import SpecialChannelEnum


@client.event
async def on_voice_state_update(member, before, after):
    server_settings = discord_server_settings_service.server_settings[str(member.guild.id)]
    audit_log_event_channel = get_channel_by_special_channel(member.guild, SpecialChannelEnum.audit_log_event)

    if server_settings is not None:
        """auditlog-voice"""
        if not before.channel:
            await audit_log_event_channel.send(embed=discord_embeds.join_embed(member, after))
            add_discord_time_log_by_member(member, True)

        if before.channel and not after.channel:
            await audit_log_event_channel.send(embed=discord_embeds.left_embed(member))

            """API"""
            add_discord_time_log_by_member(member, False)

        if before.channel and after.channel and before.channel != after.channel:
            await audit_log_event_channel.send(embed=discord_embeds.switch_embed_embed(member, after))

            """auditlog-event"""
        if not before.self_stream and after.self_stream:
            await audit_log_event_channel.send(embed=discord_embeds.start_stream_embed(member, after))

            """API"""
            add_discord_time_log_by_member(member, True)

        if before.self_stream and not after.self_stream or not after.channel and after.self_stream:
            await audit_log_event_channel.send(embed=discord_embeds.stop_stream_embed(member, before))

            """API"""
            add_discord_time_log_by_member(member, False)
