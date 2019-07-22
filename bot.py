import discord
import random

from discord import Game
from discord.ext.commands import Bot

TOKEN = 'NA'

bot = Bot(command_prefix='?')


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
             brief='[upper limit]',
             aliases=['dice'])
async def roll(ctx, limit: int):
    rnum = random.randint(1, limit)
    await ctx.send(str(rnum))


bot.run(TOKEN)