import ast


import discord
from discord.ext import commands

import datetime

from discord_embeds import embeds_for_verify_user, join_embed, left_embed, switch_embed_embed, start_stream_embed, \
    stop_stream_embed, on_member_join_to_server_embed, new_user_to_verify_embed, left_server_embed, user_add_role_embed, \
    user_remove_role_embed
from discord_server_settings_service import discord_server_settings_service
from environment import get_env
from esport_api import create_discord_user_api, add_discord_time_log, add_discord_stream_time_log, \
    get_or_create_discord_server_settings, check_webhook_subscriptions, verified_by_member
from apex_api import get_apex_rank
from models import DiscordServerSettings
import api

api.start_server_thread()

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
    if member.guild.id == GUILD:
        guild = client.get_guild(GUILD)
        channel = guild.get_channel(SERVER_LOG)
        await channel.send(embed=left_server_embed(member))


"""Server verify"""
VERIFICATION_CHANNEL_ID = [709285744794927125, 819347673575456769]  # Discord TPG (verify-a-friend) 709285744794927125


@client.event
async def on_member_join(member):
    if member.guild.id == GUILD:
        new_user = {"memberName": f"{member}",
                    "memberId": f"{member.id}",
                    "avatarUrl": f"{member.avatar_url}"
                    }
        guild = client.get_guild(GUILD)
        channel = guild.get_channel(SERVER_LOG)
        verify_channel = guild.get_channel(709285744794927125)
        """ADD user to API DB"""
        create_discord_user_api(new_user)
        await channel.send(embed=on_member_join_to_server_embed(member))
        msg = await verify_channel.send(embed=new_user_to_verify_embed(member))
        await msg.add_reaction("✅")


"""Server role manager"""

# Verification new users
ROLE_ALLOWED_TO_VERIFY_ID = [
    818901497244024842,  # Member
    722195472411787455,  # Coach
    703688573978804224,  # Staff
    709595149419675689,  # Director
    812537908736819280,  # Admin
    696277516020875324  # Owner
]
BOT_ID = 786029312788791346
VERIFY_ROLE_ID = 703686185968599111

settings = {"ROLE_ALLOWED_TO_VERIFY_ID": [818901497244024842, 722195472411787455, ],
            "BOT_ID": 696277516020875324,
            "VERIFY_ROLE_ID": 703686185968599111
            }

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
async def on_raw_reaction_add(payload):
    if payload.channel_id in VERIFICATION_CHANNEL_ID and str(payload.emoji.name) == "✅" and int(
            payload.user_id) != BOT_ID:
        msg = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if msg.author.id == BOT_ID:
            new_user_id = msg.embeds[0].title
            member = payload.member
            user_roles_list = [role.id for role in member.roles]
            intersection_roles = set(user_roles_list) & set(ROLE_ALLOWED_TO_VERIFY_ID)
            if len(intersection_roles) > 0:
                guild = client.get_guild(GUILD)
                new_user = await guild.fetch_member(int(new_user_id))
                role = discord.utils.get(member.guild.roles, id=VERIFY_ROLE_ID)
                await new_user.add_roles(role)
                await msg.delete()
                channel_id = payload.channel_id
                channel = client.get_channel(channel_id)
                await channel.send(embed=embeds_for_verify_user(new_user, member))

                """API"""
                new_user = {"memberId": f"{new_user.id}"}
                admin_member = {"memberId": f"{member.id}"}
                verified_by_member(new_user, admin_member)

    if payload.message_id == roles_assignment_setup['massage_id']:
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
async def clear(ctx, amount=0):
    if ctx.author.id == 339287982320254976:
        await ctx.channel.purge(limit=amount + 1)


"""Log system"""
GUILD = 696277112600133633
CHANNELS_LOG = 818756453778063380  # auditlog-voice
SERVER_LOG = 818756528176627743  # auditlog-join-log
STREAM_LOG = 819783521907638344  # auditlog-event
ROLES_LOG = 818756406496067604  # auditlog-roles
MESSAGE_LOG = 818756504245108757  # auditlog-messages


@client.event
async def on_voice_state_update(member, before, after):
    guild = client.get_guild(GUILD)
    voice_channel = guild.get_channel(CHANNELS_LOG)
    stream_channel = guild.get_channel(STREAM_LOG)

    if member.guild.id == GUILD:
        new_user = {"memberName": f"{member}",
                    "memberId": f"{member.id}",
                    "avatarUrl": f"{member.avatar_url}"
                    }

        """auditlog-voice"""
        if not before.channel:
            await voice_channel.send(embed=join_embed(member, after))

            """ADD user to API DB"""
            create_discord_user_api(new_user)
            add_discord_time_log(new_user, status=True)

        if before.channel and not after.channel:
            await voice_channel.send(embed=left_embed(member))

            """API"""
            add_discord_time_log(new_user, status=False)

        if before.channel and after.channel and before.channel != after.channel:
            await voice_channel.send(embed=switch_embed_embed(member, after))

            """auditlog-event"""
        if not before.self_stream and after.self_stream:
            await stream_channel.send(embed=start_stream_embed(member, after))

            """API"""
            add_discord_stream_time_log(new_user, status=True)

        if before.self_stream and not after.self_stream or not after.channel and after.self_stream:
            await stream_channel.send(embed=stop_stream_embed(member, before))

            """API"""
            add_discord_stream_time_log(new_user, status=False)


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
async def verify(ctx, user_name=None):
    if int(ctx.channel.id) in VERIFICATION_CHANNEL_ID:
        author = ctx.message.author
        user_roles_list = [role.id for role in author.roles]
        intersection_roles = set(user_roles_list) & set(ROLE_ALLOWED_TO_VERIFY_ID)
        member = None
        if len(intersection_roles) > 0:
            try:
                member = discord.utils.get(client.get_all_members(), name=user_name.split("#")[0],
                                           discriminator=user_name.split("#")[1])
            except Exception as ex:
                print(ex)
                await ctx.send("Can't fine User")
            if len(member.roles) == 1:
                role = discord.utils.get(member.guild.roles, id=VERIFY_ROLE_ID)
                await member.add_roles(role)
                await ctx.send(embed=embeds_for_verify_user(member, author))

                """API"""
                new_user = {"memberId": f"{member.id}"}
                admin_member = {"memberId": f"{member.id}"}
                verified_by_member(new_user, admin_member)
            else:
                await ctx.send('User already verified')
        else:
            await ctx.send('No permission to verify users')


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
    guild = client.get_guild(GUILD)
    role_log_channel = guild.get_channel(ROLES_LOG)
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
    new_embed = ctx.message.content.replace("!to_embed ", "").replace(" ", "")
    if new_embed is not None:
        try:
            new_embed = discord.Embed.from_dict(ast.literal_eval(new_embed))
            await ctx.send(embed=new_embed)
            await ctx.message.delete()
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    client.run(get_env().DISCORD_BOT_TOKEN)
