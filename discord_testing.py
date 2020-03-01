from discord.ext import commands, tasks
import discord
from reddit_bot import authorize, get_modqueue_length
from clear_autmod_from_modqueue import clear_queue
from mod_leaderboard import get_leaderboard_string
from top_offenders import get_offenders_string, get_offender_profile_string
import os

bot = commands.Bot(command_prefix='q!')
reddit = authorize()


@bot.command(help='clears modqueue reports against autmod and mods')
@commands.has_role('/r/Coronavirus')
async def clear_bad_reports(ctx):
    print('clean queue command')
    await ctx.send('Clearing reports against moderators and automod from queue.')
    num_reports_cleared = clear_queue(reddit)
    await ctx.send('Finished! I cleared {} reports.'.format(num_reports_cleared))


@bot.command(help='shows modqueue length')
@commands.has_role('/r/Coronavirus')
async def length(ctx):
    print('q_length command')
    length = await get_modqueue_length(reddit)
    await ctx.send('The r/coronavirus modqueue currently has {} items pending.\nhttps://www.reddit.com/r/mod/about/modqueue?subreddit=Coronavirus'.format(length))


@bot.command(help='shows mod action leaderboard from past <hours> hours', usage='<hours>', brief='shows mod action leaderboard')
@commands.has_role('/r/Coronavirus')
async def leaderboard(ctx, num_hours=2, top_k=5):
    if top_k > 5:
        top_k = 5
    if num_hours > 24:
        num_hours = 24
    print('leaderboard command with num_hours={} top_k={}'.format(num_hours, top_k))
    await ctx.send('Fetching data, please wait.')
    lb_string = get_leaderboard_string(reddit, num_hours=num_hours, top_k=top_k)
    print(lb_string)
    await ctx.send(lb_string)


@bot.command(help='shows leaderboard of removed user submissions from past <hours> hours', usage='<hours>', brief='shows repeat offender leaderboard')
@commands.has_role('/r/Coronavirus')
async def offenders(ctx, num_hours=2, top_k=5):
    if top_k > 5:
        top_k = 5
    if num_hours > 24:
        num_hours = 24
    print('offenders command with num_hours={} top_k={}'.format(num_hours, top_k))
    await ctx.send('Fetching data, please wait.')
    o_string = get_offenders_string(reddit, num_hours=num_hours, top_k=top_k)
    print(o_string)
    await ctx.send(o_string)


@bot.command(help='shows removed submissions from <user> from past <hours> hours', usage='<user> <hours>', brief='shows recent removals for user')
@commands.has_role('/r/Coronavirus')
async def recent(ctx, offender='', num_hours=2):
    if num_hours > 24:
        num_hours = 24
    print('recent command with offender={} num_hours={}'.format(offender, num_hours))
    if offender == '':
        await ctx.send('Please specify a user.')
    else:
        await ctx.send('Fetching data, please wait.')
        p_string = get_offender_profile_string(reddit, offender, num_hours=num_hours)
        print(p_string)
        await ctx.send(p_string)


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