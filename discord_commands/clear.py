import discord

from discord.ext import commands

from discord_client import client


@client.command()
@commands.has_permissions(manage_channels=True)
async def clear(ctx: discord.ext.commands.Context, amount=0):
    await ctx.channel.purge(limit=amount + 1)
