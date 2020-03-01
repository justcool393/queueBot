import discord
from discord.ext import tasks
import os
from reddit_bot import authorize, get_modqueue_length

client = discord.Client()
reddit = authorize()


@tasks.loop(minutes=30.0)
async def slow_count():
    await client.wait_until_ready()
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == 'rcoronavirus':
                print('rc')
                modqueue_length = await get_modqueue_length(reddit)
                print('length: {}'.format(modqueue_length))
                if modqueue_length > 50:
                    print('modqueue length is {}, sending message'.format(modqueue_length))
                    await channel.send('Oh no, there are {} items in the modqueue! '
                                       'https://www.reddit.com/r/mod/about/modqueue?subreddit=Coronavirus'.format(modqueue_length))


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

slow_count.start()
client.run(os.getenv('DISCORD'))
