import datetime
import json
import discord
from discord.ext import commands
import random
import string

with open('secrets.json', 'r') as secrets_file:
    TOKEN = json.load(secrets_file)['DISCORD_TOKEN']
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
# images for the embedded message
PFP_URLS = {
    'ironclad': 'https://racketrenegade.com/wp-content/uploads/2020/06/1521914530_slay-the-spire-1.jpg',
    'silent': 'https://res.cloudinary.com/lmn/image/upload/e_sharpen:100/f_auto,fl_lossy,q_auto/v1/gameskinnyc/s/i/l/'
              'silentportrait-6a431.jpg',
    'defect': 'https://cdn.pastemagazine.com/www/articles/slay%20the%20spire%20defect%20main.jpg',
    'watcher': 'https://www.dexerto.com/wp-content/uploads/2019/11/akali-cosplay.jpg'
}


# returns today's date as a string in the format used as the top-level keys in scores.json
def update_date(fmt='%m-%d-%Y'):
    today_dt = datetime.datetime.today().date()
    return today_dt.strftime(fmt)


# open the file, update a player's scores, and add a new leaderboard if necessary
# can also update character and modifiers
# returns dict of all score data
def update_score(date: str, player_id: int, player_score: int, *args) -> dict:
    player_id = str(player_id)  # str for keys in json

    with open('scores.json', 'r') as f:
        all_scores = json.load(f)

    # try to update existing player entry and update winner
    if date in all_scores.keys():
        all_scores[date]['scores'].update({player_id: player_score})
        all_scores[date]['winner'] = sorted(all_scores[date]['scores'],
                                            key=all_scores[date]['scores'].get,
                                            reverse=True)[0]

    # else construct a new leaderboard
    else:
        all_scores[date] = {
            'character': 'unknown',
            'modifiers': ['unknown'],
            'winner': player_id,
            'scores': {
                player_id: player_score
            }
        }

    # update character and modifiers if applicable
    if len(args):  # first arg is character
        all_scores[date]['character'] = args[0].lower()
    if len(args) > 1:  # second is a list of modifiers as a string
        all_scores[date]['modifiers'] = args[1].lower().split(' ')

    with open('scores.json', 'w') as f:
        json.dump(all_scores, f, indent=4)

    return all_scores


# add score to daily run, print current winner
@bot.command()
async def score(ctx, player_score, *args):
    player_score = int(player_score)
    scores = update_score(update_date(), ctx.author.id, player_score, *args)
    current_winner = await bot.fetch_user(int(scores[update_date()]['winner']))
    await ctx.send(f'Updated leaderboard.\nCurrent leader: `{current_winner.name}`')


@bot.command()
async def leaderboard(ctx, day='today'):
    if day == 'today':
        day = update_date()
    with open('scores.json', 'r') as f:
        try:
            scoreboard = json.load(f)[day]
        except KeyError:
            await ctx.send('No scoreboard for today!')
            return

    # SORTING
    # sort the player id's according to score
    scores = sorted(scoreboard['scores'], key=scoreboard['scores'].get, reverse=True)
    winner = await bot.fetch_user(int(scores[0]))

    # EMBED CONSTRUCTION
    # create and embedded leaderboard
    pasta = discord.Embed(
        title=f'Daily Challenge, {day}',
        description=f'*{" ".join(scoreboard["modifiers"])} __{scoreboard["character"]}__*',
        color=discord.Color.blurple()
    )
    # add the users to embed
    for i, player_id in enumerate(scores):
        user = await bot.fetch_user(int(player_id))
        pasta.add_field(name=f'{i+1}. {user.name}:', value=f'`{scoreboard["scores"][player_id]}`', inline=False)
    # add the character image
    if scoreboard["character"] in PFP_URLS:
        pasta.set_image(url=PFP_URLS[scoreboard['character']])
    # add winner thumbnail
    pasta.set_thumbnail(url=winner.avatar_url)
    # send the message
    await ctx.send(embed=pasta)


@bot.command()
async def stats(ctx):
    with open('scores.json', 'r') as f:
        scores = json.load(f)
    pid = str(ctx.author.id)
    pts, n, wins = 0, 0, 0

    # STAT COLLECTION
    # tally up the stats
    for day in scores:
        if pid in scores[day]['scores']:
            n += 1
            pts += scores[day]['scores'][pid]
        if scores[day]['winner'] == pid:
            wins += 1

    # EMBED CONSTRUCTION
    # make the embed
    pasta = discord.Embed(title=f'Stats for __{ctx.author.name}__', description=f'*as of {update_date()}*')
    pasta.set_thumbnail(url=ctx.author.avatar_url)
    pasta.add_field(name='Challenges Done', value=f'`{n}`', inline=False)
    pasta.add_field(name='Total Points', value=f'`{pts}`', inline=False)
    pasta.add_field(name='Average Points', value=f'`{round(pts/n)}`', inline=False)
    pasta.add_field(name='Total Wins', value=f'`{wins}`', inline=False)
    # send the message
    await ctx.send(embed=pasta)


def run():
    bot.run(TOKEN)


if __name__ == '__main__':
    run()
