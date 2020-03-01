from discord.ext import commands, tasks
import discord
from reddit_bot import authorize, get_modqueue_length
from clear_autmod_from_modqueue import clear_queue
from mod_leaderboard import get_leaderboard_string
import os

bot = commands.Bot(command_prefix='q!')
reddit = authorize()

@bot.command()
async def test(ctx):
    print('test command')
    await ctx.send('pass')

@bot.command()
async def clear_bad_reports(ctx):
    print('clean queue command')
    await ctx.send('Clearing reports against moderators and automod from queue.')
    num_reports_cleared = clear_queue(reddit)
    await ctx.send('Finished! I cleared {} reports.'.format(num_reports_cleared))

@bot.command()
async def length(ctx):
    print('q_length command')
    length = await get_modqueue_length(reddit)
    await ctx.send('The r/coronavirus modqueue currently has {} items pending.\nhttps://www.reddit.com/r/mod/about/modqueue?subreddit=Coronavirus'.format(length))

@bot.command()
async def leaderboard(ctx, num_hours=24, top_k=5):
    if top_k > 5:
        top_k = 5
    if num_hours > 24:
        num_hours = 24
    print('leaderboard command with num_hours={} top_k={}'.format(num_hours, top_k))
    await ctx.send('Fetching data, please wait.')
    lb_string = get_leaderboard_string(reddit, num_hours=num_hours)
    print(lb_string)
    await ctx.send(lb_string)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@tasks.loop(minutes=30.0)
async def queue_length():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.name == 'rcoronavirus':
                modqueue_length = await get_modqueue_length(reddit)
                print('length: {}'.format(modqueue_length))
                if modqueue_length > 50:
                    print('modqueue length is {}, sending message'.format(modqueue_length))
                    #await channel.send('Oh no, there are {} items in the modqueue! https://www.reddit.com/r/mod/about/modqueue?subreddit=Coronavirus'.format(modqueue_length))



queue_length.start()

bot.run(os.getenv('DISCORD'), bot=True)