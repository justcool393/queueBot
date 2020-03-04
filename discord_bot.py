from discord.ext import commands, tasks
from reddit_bot import authorize, get_modqueue_length
from clear_autmod_from_modqueue import clear_queue
from mod_leaderboard import get_leaderboard_string
from top_offenders import get_offenders_string, get_offender_profile_string
from comment_reports import get_comment_report_data
from config import TOXICITY_THRESHOLD
import os


class QueuebotCog(commands.Cog):
    def __init__(self, bot, reddit):
        self.bot = bot
        self.reddit = reddit
        self.submission_analysis = {}

        # start timed events
        self.queue_length.start()
        #self.analyze_queue.start()


    def cog_unload(self):
        self.queue_length.cancel()
        #self.analyze_queue.cancel()


    @commands.command(help='clears modqueue reports against autmod and mods')
    @commands.has_role('/r/Coronavirus')
    async def clear_bad_reports(self, ctx):
        print('clean queue command')
        await ctx.send('Clearing reports against moderators and automod from queue.')
        num_reports_cleared = clear_queue(self.reddit)
        await ctx.send('Finished! I cleared {} reports.'.format(num_reports_cleared))


    @commands.command(help='shows modqueue length')
    @commands.has_role('/r/Coronavirus')
    async def length(self, ctx):
        print('q_length command')
        length = await get_modqueue_length(self.reddit)
        await ctx.send('The r/coronavirus modqueue currently has {} items pending.\nhttps://www.reddit.com/r/mod/about/modqueue?subreddit=Coronavirus'.format(length))


    @commands.command(help='shows mod action leaderboard from past <hours> hours', usage='<hours>', brief='shows mod action leaderboard')
    @commands.has_role('/r/Coronavirus')
    async def leaderboard(self, ctx, num_hours=1, top_k=5):
        if num_hours > 24:
            num_hours = 24
        print('leaderboard command with num_hours={} top_k={}'.format(num_hours, top_k))
        await ctx.send('Fetching data, please wait.')
        lb_string = get_leaderboard_string(self.reddit, num_hours=num_hours, top_k=top_k)
        print(lb_string)
        await ctx.send(lb_string)


    @commands.command(help='shows leaderboard of removed user submissions from past <hours> hours', usage='<hours>', brief='shows repeat offender leaderboard')
    @commands.has_role('/r/Coronavirus')
    async def offenders(self, ctx, num_hours=1, top_k=5):
        if top_k > 5:
            top_k = 5
        if num_hours > 24:
            num_hours = 24
        print('offenders command with num_hours={} top_k={}'.format(num_hours, top_k))
        await ctx.send('Fetching data, please wait.')
        o_string = get_offenders_string(self.reddit, num_hours=num_hours, top_k=top_k)
        print(o_string)
        await ctx.send(o_string)


    @commands.command(help='shows removed submissions from <user> from past <hours> hours', usage='<user> <hours>', brief='shows recent removals for user')
    @commands.has_role('/r/Coronavirus')
    async def recent(self, ctx, offender='', num_hours=1):
        if num_hours > 24:
            num_hours = 24
        print('recent command with offender={} num_hours={}'.format(offender, num_hours))
        if offender == '':
            await ctx.send('Please specify a user.')
        else:
            await ctx.send('Fetching data, please wait.')
            p_string = get_offender_profile_string(self.reddit, offender, num_hours=num_hours)
            print(p_string)
            await ctx.send(p_string)


    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('------')


    @tasks.loop(minutes=30.0)
    async def queue_length(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if channel.name == 'rcoronavirus':
                    modqueue_length = await get_modqueue_length(self.reddit)
                    print('length: {}'.format(modqueue_length))
                    if modqueue_length > 50:
                        print('modqueue length is {}, sending message'.format(modqueue_length))
                        await channel.send('Oh no, there are {} items in the modqueue! https://www.reddit.com/r/mod/about/modqueue?subreddit=Coronavirus'.format(modqueue_length))


    @tasks.loop(minutes=2)
    async def analyze_queue(self):
        print('analyzing queue...')
        num_comments_idx, reports_idx = get_comment_report_data(self.reddit)
        print('got queue analysis results')
        for sub_id, comment_count in num_comments_idx.items():
            if sub_id not in self.submission_analysis:
                self.submission_analysis[sub_id] = {}
                self.submission_analysis[sub_id]['num_comments'] = 0
                self.submission_analysis[sub_id]['reported_comments'] = set([])
                self.submission_analysis[sub_id]['reported_to_mods'] = False
            self.submission_analysis[sub_id]['num_comments'] = max(comment_count,
                                                                   self.submission_analysis[sub_id]['num_comments'])
        for sub_id, reports in reports_idx.items():
            for comment_id in reports:
                self.submission_analysis[sub_id]['reported_comments'].add(comment_id)
        for sub_id, submission_meta in self.submission_analysis.items():
            political_toxicity_score = float(len(submission_meta['reported_comments'])) / submission_meta['num_comments']
            print('political_toxicity_score for submission {} is {}'.format(sub_id, political_toxicity_score))
            if political_toxicity_score > TOXICITY_THRESHOLD and \
                    self.submission_analysis[sub_id]['reported_to_mods'] is False and \
                    len(self.submission_analysis[sub_id]['reported_comments']) > 3:
                toxic_submission = self.reddit.submission(id=sub_id)
                self.submission_analysis[sub_id]['reported_to_mods'] = True
                if toxic_submission.locked or toxic_submission.removed:
                    continue
                print('submission at {} is potentially a political wasteland'.format(toxic_submission.shortlink))
                await self.bot.wait_until_ready()
                for guild in self.bot.guilds:
                    for channel in guild.channels:
                        if channel.name == 'rcoronavirus':
                            await channel.send(
                                'The submission at {} is potentially a political wasteland (score={}), '
                                'consider locking comments'.format(toxic_submission.shortlink, political_toxicity_score))


bot = commands.Bot(command_prefix='q!')
reddit_auth = authorize()
bot.add_cog(QueuebotCog(bot, reddit_auth))
bot.run(os.getenv('DISCORD'), bot=True)