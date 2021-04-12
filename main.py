import datetime
import ast
import threading

import discord
from discord.ext import commands

from http_server import start_server_thread, app
from apex_api import get_apex_rank
from discord_embeds import embeds_for_verify_user, join_embed, left_embed, switch_embed_embed, start_stream_embed, \
    stop_stream_embed, on_member_join_to_server_embed, new_user_to_verify_embed, left_server_embed, user_add_role_embed, \
    user_remove_role_embed
from discord_helper_utils import get_channel_by_special_channel, try_to_verify_member
from discord_server_settings_service import discord_server_settings_service
from environment import get_env
from esport_api import add_discord_time_log_by_member
from models import SpecialChannelEnum

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

APEX_ROLES = ['Bronze 1', 'Bronze 2', 'Bronze 3', 'Bronze 4', 'Silver 1', 'Silver 2', 'Silver 3', 'Silver 4', "Gold 1",
              "Gold 2", "Gold 3", "Gold 4"]

BOT_COMAND_channels = ["bot_command", "основной"]
BOT_COMAND_channels_ID = ["788693067757781023", "816203477801762836"]

timezone_offset = 8.0  # Pacific Standard Time (UTC−08:00)
tzinfo = datetime.timezone(datetime.timedelta(hours=timezone_offset))


@client.event
async def on_ready():
    print('ready-v0.04.3')


@client.event
async def on_guild_join(guild: discord.Guild):
    discord_server_settings_service.refresh_by_guild(guild)


"""auditlog-join-log"""


@client.event
async def on_member_remove(member):
    channel = get_channel_by_special_channel(member.guild, SpecialChannelEnum.audit_log_join)
    if channel is not None:
        await channel.send(embed=left_server_embed(member))


"""Server verify"""


@client.event
async def on_member_join(member: discord.Member):
    server_log_channel = get_channel_by_special_channel(member.guild, SpecialChannelEnum.audit_log_join)
    if server_log_channel is not None:
        await server_log_channel.send(embed=on_member_join_to_server_embed(member))

    verify_channel = get_channel_by_special_channel(member.guild, SpecialChannelEnum.verify)
    if verify_channel is not None:
        message = await verify_channel.send(embed=new_user_to_verify_embed(member))
        await message.add_reaction("✅")


"""Server role manager"""

# Verification new users

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
            await verify_channel.send(embed=embeds_for_verify_user(member_to_verify, payload.member))
        elif isinstance(error_msg_or_success, str):
            await verify_channel.send(error_msg_or_success)

    elif payload.message_id == roles_assignment_setup['massage_id']:
        try:
            if payload.emoji.name in roles_assignment_setup["emoji_to_role"]:
                member_add_role = payload.member
                role = discord.utils.get(member_add_role.guild.roles,
                                         id=roles_assignment_setup["emoji_to_role"][payload.emoji.name])
                await member_add_role.add_roles(role)
                print(f"Role was added {member_add_role} - {role}")
        except Exception as ex:
            print(f"Role was not added - {ex}")


@client.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == roles_assignment_setup['massage_id']:
        if payload.emoji.name in roles_assignment_setup["emoji_to_role"]:
            guild = client.get_guild(payload.guild_id)
            member_remove_role = await guild.fetch_member(payload.user_id)
            role = discord.utils.get(guild.roles,
                                     id=roles_assignment_setup["emoji_to_role"][payload.emoji.name])
            await member_remove_role.remove_roles(role)
            print(f"Role was removed {member_remove_role} - {role}")


@client.command()
@commands.has_permissions(manage_channels=True)
async def clear(ctx: discord.ext.commands.Context, amount=0):
    await ctx.channel.purge(limit=amount + 1)


"""Log system"""


@client.event
async def on_voice_state_update(member, before, after):
    server_settings = discord_server_settings_service.server_settings[str(member.guild.id)]
    audit_log_event_channel = get_channel_by_special_channel(member.guild, SpecialChannelEnum.audit_log_event)

    if server_settings is not None:
        """auditlog-voice"""
        if not before.channel:
            await audit_log_event_channel.send(embed=join_embed(member, after))
            add_discord_time_log_by_member(member, True)

        if before.channel and not after.channel:
            await audit_log_event_channel.send(embed=left_embed(member))

            """API"""
            add_discord_time_log_by_member(member, False)

        if before.channel and after.channel and before.channel != after.channel:
            await audit_log_event_channel.send(embed=switch_embed_embed(member, after))

            """auditlog-event"""
        if not before.self_stream and after.self_stream:
            await audit_log_event_channel.send(embed=start_stream_embed(member, after))

            """API"""
            add_discord_time_log_by_member(member, True)

        if before.self_stream and not after.self_stream or not after.channel and after.self_stream:
            await audit_log_event_channel.send(embed=stop_stream_embed(member, before))

            """API"""
            add_discord_time_log_by_member(member, False)


@client.command()
async def rank(ctx, user_name=None):
    if str(ctx.channel.id) in BOT_COMAND_channels_ID:

        # Check status of user rank, -1 if name wasn't found
        apex_rank = get_apex_rank(user_name)  # return str role name
        if apex_rank == -1:
            await ctx.send("Wrong name dude, you have to type your Origin name or tracker.gg is broken.")
        else:
            member = ctx.message.author
            # check old rank role
            for i in member.roles:
                if str(i) in APEX_ROLES:
                    role = discord.utils.get(member.guild.roles, name=str(i))
                    await member.remove_roles(role)
            # add new role
            role = discord.utils.get(member.guild.roles, name=apex_rank)
            await member.add_roles(role)
            # sent image of your rank
            image_url = f"https://trackercdn.com/cdn/apex.tracker.gg/ranks/{apex_rank.replace(' ', '').lower()}.png"
            user_stat_url = f"https://apex.tracker.gg/apex/profile/origin/{user_name}/overview"
            embed = discord.Embed()
            embed.set_image(url=image_url)
            embed = discord.Embed(title=f"Get rank {apex_rank}.",
                                  colour=discord.Colour(0x50feb2), url=user_stat_url,
                                  timestamp=datetime.datetime.now(tzinfo))
            embed.set_thumbnail(url=image_url)
            embed.set_author(name=member.name, url="https://discordapp.com",
                             icon_url=member.avatar_url)
            embed.set_footer(text="footer private massage", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
            await ctx.send(embed=embed)


@client.command()
async def verify(ctx: discord.ext.commands.Context, user_name=None):
    server_settings = discord_server_settings_service.server_settings[str(ctx.guild.id)]
    verify_channel_id = server_settings.get_special_channel(SpecialChannelEnum.verify)
    if verify_channel_id is None:
        # TODO: Maybe warn user that the special channel isn't set?
        return

    if str(ctx.channel.id) == verify_channel_id:
        if not server_settings.can_member_verify(ctx.message.author):
            return await ctx.send('No permission to verify users')

        if len(ctx.message.mentions) == 0:
            return await ctx.send("You didn't mention anyone. Try !verify @{MEMBER}")

        member_to_verify_id = ctx.message.mentions[0].id
        member_to_verify = await ctx.guild.fetch_member(member_to_verify_id)
        if member_to_verify is None:
            return await ctx.send('Could not find that user')

        error_msg_or_success = await try_to_verify_member(ctx.channel.id, ctx.message.author, member_to_verify)
        if error_msg_or_success is True:
            await ctx.send(embed=embeds_for_verify_user(member_to_verify, ctx.message.author))
        elif isinstance(error_msg_or_success, str):
            await ctx.send(error_msg_or_success)


@client.command()
async def edit_nick(ctx):
    if ctx.author.id == 339287982320254976:
        i = 0
        role_id_list = []
        for member in ctx.guild.members:
            for role in member.roles:
                role_id_list.append(role.id)
            if 818901497244024842 in role_id_list:
                i += 1
                if member.nick is None:
                    nick_name = str(member.name).replace("]TPG[", "")
                else:
                    nick_name = str(member.nick).replace("]TPG[", "").replace("NS_", "")

                print(f"{member} - {member.nick}")
                try:
                    await member.edit(nick=f"NS_{nick_name}")
                    print(f"{member} - {member.nick}---{nick_name}")
                    print(role_id_list)
                    role_id_list = []
                except Exception as ex:
                    print(f"can't change {member} - {ex}")
                    role_id_list = []
        print(i)


# @client.command(name='twitch')
# async def link_twitch(twitch_user_id):
#

@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    server_settings = discord_server_settings_service.server_settings[str(after.guild.id)]
    guild = client.get_guild(int(server_settings.guild_id))
    channel_id = server_settings.get_special_channel(SpecialChannelEnum.audit_log_roles)
    if channel_id is None:
        # TODO: Maybe warn the user that the special channel isn't set?
        return

    role_log_channel = guild.get_channel(int(channel_id))
    if before.roles != after.roles:
        roles_before = [role.name for role in before.roles]
        roles_after = [role.name for role in after.roles]
        if len(roles_before) < len(roles_after):
            role = list(set(roles_before) ^ set(roles_after))[0]
            await role_log_channel.send(embed=user_add_role_embed(after, role))
        else:
            role = list(set(roles_before) ^ set(roles_after))[0]
            await role_log_channel.send(embed=user_remove_role_embed(after, role))


@client.command()
async def to_embed(ctx: discord.ext.commands.Context):
    new_embed = ctx.message.content.replace("!to_embed ", "")
    if new_embed is not None:
        try:
            new_embed = discord.Embed.from_dict(ast.literal_eval(new_embed))
            await ctx.send(embed=new_embed)
            await ctx.message.delete()
        except Exception as ex:
            print(ex)


def start_bot():
    client.run(get_env().DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    api_server_thread = threading.Thread(target=start_bot, args=())

start_server_thread()
