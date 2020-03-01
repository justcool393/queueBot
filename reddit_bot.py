import praw
import os


def authorize():
    reddit = praw.Reddit(client_id='rFeHPl-tHNwzeQ',
                         client_secret=os.environ['REDDITS'],
                         password=os.environ['REDDITP'],
                         user_agent='testscript by /u/barber5',
                         username='barber5')
    return reddit


def get_modqueue(reddit):
    print('getting modqueue')
    return reddit.subreddit('coronavirus').mod.modqueue(limit=None)


async def get_modqueue_length(reddit=None):
    print('mc time')
    if reddit is None:
        print('authing')
        reddit = authorize()

    modqueue = get_modqueue(reddit)
    print('got it')
    length = sum(1 for _ in modqueue)
    print('length is {}'.format(length))
    return length

if __name__ == "__main__":
    print(get_modqueue_length())
