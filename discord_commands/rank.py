import datetime

import discord

from apex_api import get_apex_rank
from discord_client import client
from enums.apex_roles import APEX_ROLES
from tzinfo import tzinfo


@client.command()
async def rank(ctx, user_name=None):
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
