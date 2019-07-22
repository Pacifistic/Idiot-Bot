import discord
import random
import time
import sys
import traceback

from discord import Game
from discord.ext import commands
from discord import client

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

TOKEN = ''

bot = commands.Bot(command_prefix='?')


def isAFK(member: discord.VoiceState):
    if member.deaf:
        return True
    elif member.mute:
        return True
    elif member.self_mute:
        return True
    elif member.self_deaf:
        return True
    elif member.afk:
        return True
    return False


def get_time():
    localtime = time.asctime(time.localtime(time.time()))
    return localtime


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return

    ignored = (commands.CommandNotFound)

    error = getattr(error, 'original', error)

    if isinstance(error, ignored):
        return

    elif isinstance(error, commands.DisabledCommand):
        return await ctx.send(str(ctx.command) + 'has been disabled you moron')

    elif isinstance(error, commands.NoPrivateMessage):
        try:
            return await ctx.author.send(str(ctx.command) + 'cannot be used in Private Messages you idiot')
        except:
            pass

    elif isinstance(error, commands.UserInputError):
        return await ctx.send('Thats the wrong syntax you fucking idiot')

    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@bot.event
async def on_ready():
    game = discord.Game("Listening to these Idiots")
    await bot.change_presence(activity=game)
    print('logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('--------')


@bot.command(name='roll',
             description='Rolls random number up to specified limit',
             brief='roll from 1 to limit',
             aliases=['dice'])
async def roll(ctx, limit: int):
    rnum = random.randint(1, limit)
    await ctx.send(str(rnum))


@roll.error
async def roll_handler(ctx, error):
    if isinstance(error, commands.UserInputError):
        await ctx.send('It\'s supposed to be a number after ?roll you moron')


@bot.command(name='PickIdiot',
             description='picks a random idiot from the idiot tag',
             brief='picks a random idiot',
             aliases=['pickidiot', 'Pickidiot', 'pickIdiot'],
             pass_context=True)
async def pick_idiot(ctx):
    server = bot.get_guild(156092180090322944)
    role = discord.utils.get(server.roles, name='idiot')
    idiots = []
    for member in server.members:
        if role in member.roles:
            idiots.append(member)
    random_num = random.randint(0, len(idiots)-1)
    random_idiot = idiots.pop(random_num)
    await ctx.send(random_idiot.display_name)


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        print(member.display_name + ' joined '+after.channel.name)
        return
    elif after.channel is None:
        print(member.display_name + ' disconnected')
        return
    elif isAFK(after):
        print(member.display_name + ' is AFK')
        return
    else:
        print(member.display_name + ' is back')
        return


bot.run(TOKEN)