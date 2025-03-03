import datetime
import os
from typing import Optional
import asyncio

import discord
from discord.ext.commands import when_mentioned_or, CommandNotFound, has_permissions, NoPrivateMessage, Bot, \
    ExpectedClosingQuoteError, MissingRole, MissingAnyRole, MissingRequiredArgument

from react_decorators import *
from voting import voteDB

# Prod
TOKEN = '' 
intents = discord.Intents.default()
intents.reactions = True
intents.members = True

if not os.path.exists("data/temp"):
    os.makedirs("data/temp")


def get_prefix(bot, message: discord.Message):
    prefix = voteDB.getPrefix(message.guild.id if message.guild else -1)
    return when_mentioned_or(prefix)(bot, message)


bot = Bot(command_prefix=get_prefix, intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord')
    await resume_posting()


async def resume_posting():
    # TODO
    pass


# Prefix get/set command
@has_permissions(administrator=True)
@bot.command(name='prefix', help='Changes prefix on the server')
async def prefix(ctx, prefix: Optional[str]):
    if prefix is None:
        prefix = voteDB.getPrefix(ctx.guild.id)
        await ctx.send(f"Current prefix is `{prefix}`")
    else:
        voteDB.setPrefix(ctx.guild.id, prefix)
        await ctx.send(f"Prefix changed to `{prefix}`")


# VC
@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel:
        role = discord.utils.get(member.guild.roles, name="talking")
        await member.add_roles(role)
    elif before.channel and not after.channel:
        role = discord.utils.get(member.guild.roles, name="talking")
        await member.remove_roles(role)


@bot.event
async def on_error(ctx, err, *args, **kwargs):
    if err == "on_command_error":
        await args[0].send("Something went wrong")
    raise


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        pass
    elif isinstance(error, NoPrivateMessage):
        await ctx.send("Cannot run this command in DMs")
    elif isinstance(error, (MissingRole, MissingAnyRole)):
        await ctx.send("You are not allowed to do that!")
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send("You are missing a required parameter! (Most likely vote id)")
    elif isinstance(error, ExpectedClosingQuoteError):
        await ctx.send(f"Mismatching quotes, {str(error)}")
    elif hasattr(error, "original"):
        raise error.original
    else: raise error


# Load poll functionality
bot.load_extension("voting.vote_commands")

bot.run(TOKEN)
