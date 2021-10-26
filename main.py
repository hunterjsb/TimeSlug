import datetime
import json
import discord
from discord.ext import commands
import random
import string

TOKEN = 'ODg1MjI5NTE2NzYxNDczMDk1.YTkAOw.qKsrtN9LEYj_O6nkEHRKXIsY6M4'
bot = commands.Bot(command_prefix='$')


@bot.event  # ready-up
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f'$score, $leaderboard, or try $help...'))
    print('- R E A D Y -')

# ------------- LITE-SHOT BOT ---------------


# generate random alpha-numeric lite-shot URL extension and append it
def generate_url(length: int) -> str:
    an_str = ''.join(random.choices(string.ascii_letters + string.digits, k=length)).lower()
    url = 'https://prnt.sc/' + an_str
    return url


# send the URL to the discord (hopefully it embeds)
@bot.command()
async def prntsc(ctx, n=1, length=6):
    for i in range(n):
        url = generate_url(length)
        await ctx.send(url)


#  ------------- SLAY THE SPIRE ----------------
#  oct. 25, 2021
"""
scores.json will be structured as follows:
{
    date: {
        character: str,
        perks: [str],
        winner: player_id,
        scores: {
            player_id: score,
            ...
        }
    },
    ...   
}
"""

today_dt = datetime.datetime.today().date()
today = today_dt.strftime('%m-%d-%Y')

PFP_URLS = {
    'ironclad': 'https://racketrenegade.com/wp-content/uploads/2020/06/1521914530_slay-the-spire-1.jpg',
    'silent': 'https://res.cloudinary.com/lmn/image/upload/e_sharpen:100/f_auto,fl_lossy,q_auto/v1/gameskinnyc/s/i/l/'
              'silentportrait-6a431.jpg',
    'defect': 'https://cdn.pastemagazine.com/www/articles/slay%20the%20spire%20defect%20main.jpg',
    'vigilant': 'https://www.dexerto.com/wp-content/uploads/2019/11/akali-cosplay.jpg'
}


def update_score(date: str, player_id: int, player_score: int, *args):
    player_id = str(player_id)  # str for keys in json

    with open('scores.json', 'r') as f:
        all_scores = json.load(f)

    # try to update existing player entry and update winner
    if date in all_scores.keys():
        all_scores[date]['scores'].update({player_id: player_score})
        all_scores[date]['winner'] = \
            sorted(all_scores[date]['scores'], key=all_scores[date]['scores'].get, reverse=True)[0]

    # else construct a new leaderboard
    else:
        all_scores[date] = {
            'character': 'unknown',
            'modifiers': 'unknown',
            'winner': player_id,
            'scores': {
                player_id: player_score
            }
        }

    # update character and modifiers if applicable
    if len(args):
        all_scores[date]['character'] = args[0].lower()
    if len(args) > 1:
        all_scores[date]['modifiers'] = args[1].lower().split(' ')

    with open('scores.json', 'w') as f:
        json.dump(all_scores, f, indent=4)


# add score to daily run
@bot.command()
async def score(ctx, player_score, *args):
    update_score(today, ctx.author.id, player_score, *args)
    await ctx.send('Updated leaderboard.')


@bot.command()
async def leaderboard(ctx, day=today):
    with open('scores.json', 'r') as f:
        try:
            scoreboard = json.load(f)[day]
        except KeyError:
            await ctx.send('No scoreboard for today!')
            return

    # sort the player id's according to score
    scores = sorted(scoreboard['scores'], key=scoreboard['scores'].get, reverse=True)

    # create and embedded leaderboard
    pasta = discord.Embed(
        title=f'Daily Challenge, {day}',
        description=f'*{" ".join(scoreboard["modifiers"])} __{scoreboard["character"]}__*',
        color=discord.Color.blurple()
    )
    for i, player_id in enumerate(scores):
        user = await bot.fetch_user(int(player_id))
        pasta.add_field(name=f'{i+1}. {user.name.upper()}:', value=scoreboard['scores'][player_id], inline=False)
    if scoreboard["character"] in PFP_URLS:
        pasta.set_thumbnail(url=PFP_URLS[scoreboard['character']])

    # send the message
    await ctx.send(embed=pasta)


def run():
    bot.run(TOKEN)


if __name__ == '__main__':
    run()
