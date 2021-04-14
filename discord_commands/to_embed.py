import ast
import logging
import discord

from discord_client import client

log = logging.getLogger('DiscordBot')


@client.command()
async def to_embed(ctx: discord.ext.commands.Context):
    new_embed = ctx.message.content.replace("!to_embed ", "")
    if new_embed is not None:
        try:
            new_embed = discord.Embed.from_dict(ast.literal_eval(new_embed))
            await ctx.send(embed=new_embed)
            await ctx.message.delete()
        except Exception as ex:
            log.error(ex)
