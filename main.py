import discord
from discord.ext import commands

from discord.utils import get
import datetime

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker, query

import config
from models import DiscordUser, MediaPost, OnlineTimeLog, OnlineStreamTimeLog
from apex_api import get_apex_rank
from welcome_message import WELCOME_MESSAGE

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

APEX_ROLES = ['Bronze 1', 'Bronze 2', 'Bronze 3', 'Bronze 4', 'Silver 1', 'Silver 2', 'Silver 3', 'Silver 4', "Gold 1",
              "Gold 2", "Gold 3", "Gold 4"]

BOT_COMAND_channels = ["bot_command", "основной"]
BOT_COMAND_channels_ID = ["788693067757781023", "816203477801762836"]

engine_config = f'{config.DB_DATABASE_TYPE_1}://{config.DB_USER_1}:{config.DB_PASSWORD_1}@{config.DB_HOST_1}:{config.DB_PORT_1}/{config.DB_DATABASE_1}'
engine = create_engine(engine_config, echo=False)
Session = sessionmaker(bind=engine)

timezone_offset = 8.0  # Pacific Standard Time (UTC−08:00)
tzinfo = datetime.timezone(datetime.timedelta(hours=timezone_offset))


@client.event
async def on_ready():
    print('ready-v0.03.8')


"""auditlog-join-log"""


@client.event
async def on_member_remove(member):
    if member.guild.id == GUILD:
        guild = client.get_guild(GUILD)
        channel = guild.get_channel(SERVER_LOG)
        left_server_embed = discord.Embed(colour=discord.Colour(0xff001f),
                                          timestamp=datetime.datetime.now(tzinfo),
                                          description=f"{member} has left the server!")
        left_server_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
        await channel.send(embed=left_server_embed)


"""Server verify"""
VERIFICATION_CHANNEL_ID = [709285744794927125, 819347673575456769]  # Discord TPG (verify-a-friend)


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
                                              description="```\n✅ User verified.```",
                                              timestamp=datetime.datetime.now(tzinfo))
                success_embed.set_author(name=f"{new_user}", icon_url=f"{new_user.avatar_url}")
                success_embed.set_footer(text=f"{member}", icon_url=f"{member.avatar_url}")
                await channel.send(embed=success_embed)


"""Log system"""
GUILD = 696277112600133633
CHANNELS_LOG = 818756453778063380  # auditlog-voice
SERVER_LOG = 818756528176627743  # auditlog-join-log
STREAM_LOG = 819783521907638344  # auditlog-event
ROLES_LOG = 818756406496067604  # auditlog-roles


@client.event
async def on_voice_state_update(member, before, after):
    guild = client.get_guild(GUILD)
    voice_channel = guild.get_channel(CHANNELS_LOG)
    stream_channel = guild.get_channel(STREAM_LOG)

    if member.guild.id == GUILD:

        """auditlog-voice"""
        if not before.channel:
            join_embed = discord.Embed(colour=discord.Colour(0xff2f),
                                       timestamp=datetime.datetime.now(tzinfo),
                                       description=f"{member} has arrived to {after.channel.name}!")
            join_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
            await voice_channel.send(embed=join_embed)

            """ADD user to DB"""
            checkuser = DiscordUser(member_name=str(member),
                                    member_id=int(member.id),
                                    member_nickname=str(member.nick),
                                    avatar_url=member.avatar_url)
            session = Session()
            discord_user_create(checkuser, session)

            """ADD time record DB"""
            session2 = Session()
            time_log = OnlineTimeLog(member_id=member.id, status=True)
            add_time_log(time_log, session2)



        if before.channel and not after.channel:
            left_embed = discord.Embed(colour=discord.Colour(0xff001f),
                                       timestamp=datetime.datetime.now(tzinfo),
                                       description=f"{member} User disconnect!")
            left_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
            await voice_channel.send(embed=left_embed)

            """ADD time record DB"""
            session = Session()
            time_log = OnlineTimeLog(member_id=member.id, status=False)
            add_time_log(time_log, session)

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
            session = Session()
            time_log = OnlineStreamTimeLog(member_id=member.id, status=True)
            add_time_log(time_log, session)

        if before.self_stream and not after.self_stream or not after.channel and after.self_stream:
            switched_embed = discord.Embed(colour=discord.Colour(0xff001f),
                                           timestamp=datetime.datetime.now(tzinfo),
                                           description=f"{member} | stop stream in {before.channel.name}!")
            switched_embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
            await stream_channel.send(embed=switched_embed)
            """ADD stream time record DB"""
            session = Session()
            time_log = OnlineStreamTimeLog(member_id=member.id, status=False)
            add_time_log(time_log, session)


@client.command()
async def roles(ctx):
    roles_list_name = []
    if str(ctx.channel.id) in BOT_COMAND_channels_ID:
        for role in ctx.guild.roles:
            roles_list_name.append(str(role.name))
        await ctx.send(roles_list_name)


@client.command()
async def users(ctx, user_status=None):
    if str(ctx.channel.id) in BOT_COMAND_channels_ID:
        users_list_name = []
        if user_status is None:
            for guild in client.guilds:
                print(f"{guild} - {guild.id}")
                for member in guild.members:
                    users_list_name.append(
                        {"name": member.name, "discriminator": member.discriminator, "id": member.id})
            print(users_list_name)
            # await ctx.send(users_list_name)
        elif user_status == "online":
            print(discord.Guild.name)


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
async def server_info(ctx):
    if str(ctx.channel.id) in BOT_COMAND_channels_ID:
        print(ctx.args)
        print(ctx.channel.id)
        name = str(ctx.guild.name)
        description = str(ctx.guild.description)
        total_online_members = sum(
            member.status == discord.Status.online and not member.bot for member in ctx.guild.members)
        total_offline_members = sum(
            member.status == discord.Status.offline and not member.bot for member in ctx.guild.members)

        owner = str(ctx.guild.owner)
        id = str(ctx.guild.id)
        region = str(ctx.guild.region)
        memberCount = str(ctx.guild.member_count)
        icon = str(ctx.guild.icon_url)
        embed = discord.Embed(
            title=name + " Server Information",
            description=description,
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Owner", value=owner, inline=True)
        embed.add_field(name="Server ID", value=id, inline=True)
        embed.add_field(name="Region", value=region, inline=True)
        embed.add_field(name="Member Count", value=memberCount, inline=True)
        embed.add_field(name="online_members", value=total_online_members, inline=True)
        embed.add_field(name="offline_members", value=total_offline_members, inline=True)
        await ctx.send(embed=embed)


#
# @client.event
# async def on_raw_reaction_add(payload):
#     if str(payload.channel_id) in BOT_COMAND_channels_ID:
#         member = payload.member
#         message_id = payload.message_id
#         user_id = payload.user_id
#         channel_id = payload.channel_id
#         msg = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
#         author = msg.author
#         channel = client.get_channel(channel_id)
#         message = await channel.fetch_message(payload.message_id)
#         reaction = get(message.reactions)
#         if str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "✅":
#             data_log = {"member_added_reaction": {"member_name": str(member),
#                                                   "author_nick": str(member.nick),
#                                                   "id": str(user_id)},
#                         "message_data": {
#                             "message_id": str(message_id),
#                             "message_author": str(msg.author),
#                             "author_id": str(author.id),
#                             "author_nick": str(author.nick),
#                             "reaction_count": str(reaction.count),
#                             "message_data": str(msg.content),
#                         }
#                         }
#
#             message_author = DiscordUser(member_name=str(member),
#                                          member_id=int(user_id),
#                                          member_nickname=str(member.nick))
#
#             admin_user = DiscordUser(member_name=str(author),
#                                      member_id=int(author.id),
#                                      member_nickname=str(author.nick))
#
#             session = Session()
#             discord_user_create(message_author, session)
#             discord_user_create(admin_user, session)
#
#             # message_author_for_post = session.query(DiscordUser).filter_by(member_id=message_author.member_id).first()
#             # admin_user_for_post = session.query(DiscordUser).filter_by(member_id=admin_user.member_id).first()
#
#             medea_post = MediaPost(message_data=msg.content,
#                                    message_author_id=int(author.id),
#                                    admin_user_id=int(user_id),
#                                    discord_message_id=message_id)
#             print(f"{member.avatar_url}")
#             try:
#                 session.add(medea_post)
#                 session.commit()
#                 print(f"{MediaPost}--CREATE")
#
#                 embed = discord.Embed(title=f"Message id - {message_id}",
#                                       colour=discord.Colour(0x18617), url="https://discordapp.com",
#                                       description=f" ```\n{msg.content.replace('!submit', '')}```",
#                                       timestamp=datetime.datetime.utcfromtimestamp(1614909210))
#
#                 embed.set_author(name=f"{author}", icon_url=f"{author.avatar_url}")
#                 embed.set_footer(text=f"Approved by {member}", icon_url=f"{member.avatar_url}")
#                 await channel.send(embed=embed)
#                 await message.delete()
#
#             except:
#                 print(f"{MediaPost}--ERROR")
#                 session.rollback()
#                 raise
#             finally:
#                 session.close()
#             try:
#                 await msg.clear_reaction("❗")
#             except:
#                 pass
#         elif str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "❌":
#             await message.add_reaction("⭕")
#         elif str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "⭕":
#             await message.delete()
#         elif str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "❗":
#             await message.add_reaction("✅")


@client.command()
async def delete_msg(ctx, msg_id):
    if ctx.author.id == "339287982320254976":
        session = Session()
        if msg_id != "all":
            try:
                session.query(MediaPost).filter_by(id=msg_id).delete()
                # session.query(MediaPost).filter_by(discord_message_id=msg_id).delete()
                session.commit()

            except:
                print(f"{msg_id}--ERROR")
                raise
            finally:
                session.close()
        elif msg_id == "all":
            messages = session.query(DiscordUser).all()
            for i in messages:
                session.query(DiscordUser).filter_by(id=i.id).delete()

            print(messages)
        session.commit()
        session.close()


@client.event
async def on_raw_reaction_remove(payload):
    if str(payload.channel_id) in BOT_COMAND_channels_ID:
        msg = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        channel_id = payload.channel_id
        channel = client.get_channel(channel_id)
        message = await channel.fetch_message(payload.message_id)
        for reaction in message.reactions:
            if reaction.emoji == '✅':
                reaction_count = reaction.count
        if str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "❌":
            await msg.clear_reaction("⭕")
        elif str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "❗":
            await msg.clear_reaction("✅")
        elif str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "✅" and reaction_count <= 1:
            await msg.clear_reaction("✅")
            await msg.add_reaction("❗")


@client.command()
async def submit(ctx):
    if str(ctx.channel.id) in BOT_COMAND_channels_ID:
        await ctx.message.add_reaction("❗")
        await ctx.message.add_reaction("❌")


def discord_user_create(checkuser, session):
    user_stat = session.query(exists().where(DiscordUser.member_id == checkuser.member_id)).scalar()
    if not user_stat:
        session.add(checkuser)
        try:
            session.commit()
        except:
            print(f"{user_stat}--ERROR")
            session.rollback()
            raise
        finally:
            session.close()


def add_time_log(record, session):
        session.add(record)
        try:
            session.commit()
        except:
            print(f"{record}--ERROR")
            session.rollback()
            raise
        finally:
            session.close()


if __name__ == '__main__':
    client.run(config.TOKEN)
