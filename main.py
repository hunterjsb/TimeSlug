import discord
from discord.ext import commands
import random
import string

TOKEN = 'ODg1MjI5NTE2NzYxNDczMDk1.YTkAOw.qKsrtN9LEYj_O6nkEHRKXIsY6M4'
bot = commands.Bot(command_prefix='$')


def generate_url(length: int) -> str:
    an_str = ''.join(random.choices(string.ascii_letters + string.digits, k=length)).lower()
    url = 'https://prnt.sc/' + an_str
    return url


@bot.command()
async def prntsc(ctx, n=1, length=6):
    for i in range(n):
        url = generate_url(length)
        await ctx.send(url)


def run():
    bot.run(TOKEN)


if __name__ == '__main__':
    run()
