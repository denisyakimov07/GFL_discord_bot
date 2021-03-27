import discord
from discord.ext import commands

import datetime
import os

from db_functions import add_record_log, discord_user_create
from esport_api import create_discord_user_api, add_discord_time_log, add_discord_stream_time_log
from models import DiscordUser, OnlineTimeLog, OnlineStreamTimeLog, UserVerifiedLog
from apex_api import get_apex_rank

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

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
    print('ready-v0.04.0')


"""auditlog-join-log"""


@client.event
async def on_member_remove(member):
    if member.guild.id == GUILD:
        guild = client.get_guild(GUILD)
        channel = guild.get_channel(SERVER_LOG)
        left_server_embed = discord.Embed(colour=discord.Colour(0xff001f),
                                          timestamp=datetime.datetime.now(tzinfo),
                                          description=f"{member.mention} has left the server!")
        left_server_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
        await channel.send(embed=left_server_embed)


"""Server verify"""
VERIFICATION_CHANNEL_ID = [709285744794927125, 819347673575456769]  # Discord TPG (verify-a-friend) 709285744794927125


@client.event
async def on_member_join(member):
    if member.guild.id == GUILD:
        guild = client.get_guild(GUILD)
        channel = guild.get_channel(SERVER_LOG)
        verify_channel = guild.get_channel(709285744794927125)

        join_to_server_embed = discord.Embed(colour=discord.Colour(0x89ff00),
                                             timestamp=datetime.datetime.now(tzinfo),
                                             description=f"{member} has joined the server!")
        join_to_server_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
        await channel.send(embed=join_to_server_embed)

        verify_embed = discord.Embed(colour=discord.Colour(0x89ff00),
                                     title=member.id,
                                     timestamp=datetime.datetime.now(tzinfo),
                                     description=f"{member} has joined the server!")
        verify_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
        msg = await verify_channel.send(embed=verify_embed)
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
                success_embed = discord.Embed(colour=discord.Colour(0x8aff02),
                                              description=f"\n✅ User verified. {new_user.mention}",
                                              timestamp=datetime.datetime.now(tzinfo))
                success_embed.set_author(name=f"{new_user}", icon_url=f"{new_user.avatar_url}")
                success_embed.set_footer(text=f"{member}", icon_url=f"{member.avatar_url}")
                await channel.send(embed=success_embed)
                role_add_log = UserVerifiedLog(member_id=new_user_id, admin_id=member.id)
                add_record_log(role_add_log)


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
            join_embed = discord.Embed(colour=discord.Colour(0xff2f),
                                       timestamp=datetime.datetime.now(tzinfo),
                                       description=f"{member} has arrived to {after.channel.name}!")
            join_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
            await voice_channel.send(embed=join_embed)

            """ADD user to DB"""
            check_user = DiscordUser(member_name=str(member),
                                     member_id=str(member.id),
                                     member_nickname=str(member.nick),
                                     avatar_url=member.avatar_url)

            discord_user_create(check_user)

            """ADD user to API DB"""
            create_discord_user_api(new_user)

            """ADD time record DB"""

            time_log = OnlineTimeLog(member_id=member.id, status=True)
            add_record_log(time_log)
            """API"""
            add_discord_time_log(new_user, status=True)

        if before.channel and not after.channel:
            left_embed = discord.Embed(colour=discord.Colour(0xff001f),
                                       timestamp=datetime.datetime.now(tzinfo),
                                       description=f"{member} User disconnect!")
            left_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
            await voice_channel.send(embed=left_embed)

            """ADD time record DB"""

            time_log = OnlineTimeLog(member_id=member.id, status=False)
            add_record_log(time_log)

            """API"""
            add_discord_time_log(new_user, status=False)

        if before.channel and after.channel and before.channel != after.channel:
            switched_embed = discord.Embed(colour=discord.Colour(0xffea00),
                                           timestamp=datetime.datetime.now(tzinfo),
                                           description=f"{member} User switched channel to {after.channel.name}!")
            switched_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
            await voice_channel.send(embed=switched_embed)

            """auditlog-event"""
        if not before.self_stream and after.self_stream:
            switched_embed = discord.Embed(colour=discord.Colour(0xff2f),
                                           timestamp=datetime.datetime.now(tzinfo),
                                           description=f"{member} | start stream in {after.channel.name}!")
            switched_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
            await stream_channel.send(embed=switched_embed)

            """ADD stream time record DB"""

            time_log = OnlineStreamTimeLog(member_id=member.id, status=True)
            add_record_log(time_log)

            """API"""
            add_discord_stream_time_log(new_user, status=True)

        if before.self_stream and not after.self_stream or not after.channel and after.self_stream:
            switched_embed = discord.Embed(colour=discord.Colour(0xff001f),
                                           timestamp=datetime.datetime.now(tzinfo),
                                           description=f"{member} | stop stream in {before.channel.name}!")
            switched_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
            await stream_channel.send(embed=switched_embed)

            """ADD stream time record DB"""

            time_log = OnlineStreamTimeLog(member_id=member.id, status=False)
            add_record_log(time_log)

            """API"""
            add_discord_stream_time_log(new_user, status=False)


@client.command()
async def rank(ctx, user_name=None):
    if str(ctx.channel.id) in BOT_COMAND_channels_ID:

        # Check status of user rank, -1 if name wasn't found
        rank = get_apex_rank(user_name)  # return str role name
        if rank == -1:
            await ctx.send("Wrong name dude, you have to type your Origin name or tracker.gg is broken.")
        else:
            member = ctx.message.author
            # check old rank role
            for i in member.roles:
                if str(i) in APEX_ROLES:
                    role = discord.utils.get(member.guild.roles, name=str(i))
                    await member.remove_roles(role)
            # add new role
            role = discord.utils.get(member.guild.roles, name=rank)
            await member.add_roles(role)
            # sent image of your rank
            image_url = f"https://trackercdn.com/cdn/apex.tracker.gg/ranks/{rank.replace(' ', '').lower()}.png"
            user_stat_url = f"https://apex.tracker.gg/apex/profile/origin/{user_name}/overview"
            embed = discord.Embed()
            embed.set_image(url=image_url)
            embed = discord.Embed(title=f"Get rank {rank}.",
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
        if len(intersection_roles) > 0:
            try:
                member = discord.utils.get(client.get_all_members(), name=user_name.split("#")[0],
                                           discriminator=user_name.split("#")[1])
            except:
                await ctx.send("Can't fine User")
            if len(member.roles) == 1:
                role = discord.utils.get(member.guild.roles, id=VERIFY_ROLE_ID)
                await member.add_roles(role)
                success_embed = discord.Embed(colour=discord.Colour(0x8aff02),
                                              description=f"\n✅ User verified. {member.mention}",
                                              timestamp=datetime.datetime.now(tzinfo))
                success_embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
                success_embed.set_footer(text=f"{author}", icon_url=f"{author.avatar_url}")
                await ctx.send(embed=success_embed)
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
                except:
                    print(f"can't change {member}")
                    role_id_list = []
        print(i)


if __name__ == '__main__':
    client.run(TOKEN)
