from reddit_bot import get_modqueue, authorize
from config import SUBREDDIT


def clear_queue(reddit):
    modset = set([k.name for k in reddit.subreddit(SUBREDDIT).moderator()])
    queue = get_modqueue(reddit)
    approve_count = 0
    for qi in queue:
        if qi.author.name in modset:
            print('approving submission {} {}'.format(qi.author.name, qi.submission.id))
            qi.mod.approve()
            approve_count += 1
    print('finished clearing queue')
    return approve_count


def approve_reposts(reddit):
    queue = get_modqueue(reddit)
    remove_count = 0
    for qi in queue:
        repost_text = 'Avoid reposting information'
        for ur in qi.user_reports:
            if ur[0] is not None and ur[0].find(repost_text) != -1:
                qi.mod.approve()
                remove_count += 1
    print('finished clearing queue')
    return remove_count


if __name__ == "__main__":
    reddit = authorize()
    approve_reposts(reddit)