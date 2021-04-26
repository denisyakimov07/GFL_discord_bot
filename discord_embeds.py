import datetime

import discord

timezone_offset = 8.0  # Pacific Standard Time (UTC−08:00)
tzinfo = datetime.timezone(datetime.timedelta(hours=timezone_offset))


def embeds_for_verify_user(new_user: discord.Member, member: discord.Member):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0x8aff03),
                                         description=f"\n✅ User verified. <@!{new_user.id}>",
                                         timestamp=datetime.datetime.now(tzinfo))
    embed.set_author(name=f"{new_user}", icon_url=f"{new_user.avatar_url}")
    embed.set_footer(text=f"{member}", icon_url=f"{member.avatar_url}")
    return embed


def join_embed(member: discord.Member, after: discord.VoiceState):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0xff2f),
                                         timestamp=datetime.datetime.now(tzinfo),
                                         description=f"<@!{member.id}> has arrived to {after.channel.name}!")
    embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
    return embed


def left_embed(member: discord.Member):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0xff001f),
                                         timestamp=datetime.datetime.now(tzinfo),
                                         description=f"<@!{member.id}> User disconnect!")
    embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
    return embed


def switch_embed_embed(member: discord.Member, after: discord.VoiceState):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0xffea00),
                                         timestamp=datetime.datetime.now(tzinfo),
                                         description=f"<@!{member.id}> User switched channel to {after.channel.name}!")
    embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
    return embed


def start_stream_embed(member: discord.Member, after: discord.VoiceState):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0xff2f),
                                         timestamp=datetime.datetime.now(tzinfo),
                                         description=f"<@!{member.id}> | start stream in {after.channel.name}!")
    embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
    return embed


def stop_stream_embed(member: discord.Member, before: discord.VoiceState):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0xff001f),
                                         timestamp=datetime.datetime.now(tzinfo),
                                         description=f"<@!{member.id}> | stop stream in {before.channel.name}!")
    embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
    return embed


# could be does not working (member.mention)
def on_member_join_to_server_embed(member: discord.Member):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0x89ff00),
                                         timestamp=datetime.datetime.now(tzinfo),
                                         description=f"<@!{member.id}> has joined the server!")
    embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
    return embed


def left_server_embed(member: discord.Member):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0xff001f),
                                         timestamp=datetime.datetime.now(tzinfo),
                                         description=f"<@!{member.id}> has left the server!")
    embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
    return embed


def new_user_to_verify_embed(member: discord.Member):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0x89ff00),
                                         timestamp=datetime.datetime.now(tzinfo),
                                         description=f"<@!{member.id}> has joined the server!")
    embed.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
    embed.set_footer(text=f"{member.id}")
    return embed


def user_add_role_embed(member: discord.Member, role):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0x89ff00),
                                         timestamp=datetime.datetime.now(tzinfo),
                                         description=f"<@!{member.id}> add role - {role}!")
    embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
    return embed


def user_remove_role_embed(member: discord.Member, role):
    embed: discord.Embed = discord.Embed(colour=discord.Colour(0xff001f),
                                         timestamp=datetime.datetime.now(tzinfo),
                                         description=f"<@!{member.id}> remove role - {role}!")
    embed.set_footer(text="|", icon_url=f"{member.avatar_url}")
    return embed
