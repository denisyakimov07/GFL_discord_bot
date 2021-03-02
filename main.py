import discord
from discord.ext import commands
import requests
from discord.utils import get
import datetime
from models import DiscordUser



from sqlalchemy import create_engine


"""name  - epiz_27963539,  pass -o8vSQ3DjMGQ, host name - sql105.epizy.com, data_name - epiz_27963539_tpgdatabace,"""
"https://discord.com/api/oauth2/authorize?client_id=786029312788791346&permissions=2014313665&scope=bot"
# Apex
APEX_KEY = "cc301c53-f007-455e-b3da-0fdd828c6523"
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


# Discord
CLIENT_ID = 786029312788791346
PUBLIC_KEY = '5abb7a5d430e5158b68b6b217f4ac1bc0e5065c0a3093ccdad53ede613869390'
TOKEN = "Nzg2MDI5MzEyNzg4NzkxMzQ2.X9Ac1w.TRZVEdtnSA4NyTh0Yyo-pXmi1a4"
CLIENT_SECRET = "nblp34-XOk8gO4vhOs4e4fxQYShoKYIi"
APEX_ROLES = ['Bronze 1', 'Bronze 2', 'Bronze 3', 'Bronze 4', 'Silver 1', 'Silver 2', 'Silver 3', 'Silver 4', "Gold 1",
              "Gold 2", "Gold 3", "Gold 4"]

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)
BOT_COMAND_channels = ["bot_command", "основной"]
BOT_COMAND_channels_ID = ["788693067757781023", "816203477801762836"]

@client.event
async def on_ready():
    print('ready-v0.01')


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
                    users_list_name.append({"name": member.name, "discriminator": member.discriminator, "id": member.id})
            print (users_list_name)
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
                                  timestamp=datetime.datetime.utcfromtimestamp(1613357441))
            embed.set_thumbnail(url=image_url)
            embed.set_author(name=member.name, url="https://discordapp.com",
                             icon_url=member.avatar_url)
            embed.set_footer(text="footer text", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
            await ctx.send(embed=embed)


@client.command()
async def server_info(ctx):
    if str(ctx.channel.id) in BOT_COMAND_channels_ID:

        print (ctx.args)
        print (ctx.channel.id)
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


@client.event
async def on_raw_reaction_add(payload):
    if str(payload.channel_id) in BOT_COMAND_channels_ID:
        member = payload.member
        message_id = payload.message_id
        user_id = payload.user_id
        channel_id = payload.channel_id
        msg = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        author = msg.author
        channel = client.get_channel(channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = get(message.reactions)
        if str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "✅":
            data_log = {"member_added_reaction": {"member_name": str(member),
                                                  "author_nick": str(member.nick),
                                                  "id": str(user_id)},
                        "message_data": {
                            "message_id": str(message_id),
                            "message_author": str(msg.author),
                            "author_id": str(author.id),
                            "author_nick": str(author.nick),
                            "reaction_count": str(reaction.count),
                            "message_data": str(msg.content),
                        }
                        }
            adduser = DiscordUser(member_name=member, member_id=user_id, member_nickname=member.nick)

            embed = discord.Embed(colour=discord.Colour(0xe083b), description=str(data_log))
            await channel.send(embed=embed)

            await msg.clear_reaction("❗")
        elif str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "❌":
            await message.add_reaction("⭕")
        elif str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "⭕":
            await message.delete()
        elif str(payload.user_id) != "786029312788791346" and str(payload.emoji.name) == "❗":
            await message.add_reaction("✅")


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


client.run(TOKEN)
