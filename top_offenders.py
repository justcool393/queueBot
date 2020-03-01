from reddit_bot import authorize
import datetime




KEEP_ACTIONS = {'removecomment', 'spamcomment', 'banuser', 'removelink', 'spamlink'}



def get_top_offenders(reddit, num_hours=24):
    current_limit = 100
    reached, offenders_idx, banned_idx = get_top_offenders_limit(reddit, num_hours, current_limit)
    while reached is False and current_limit < 7000:
        current_limit = current_limit*2
        reached, offenders_idx, banned_idx = get_top_offenders_limit(reddit, num_hours, current_limit)
    return offenders_idx, banned_idx


def get_top_offenders_limit(reddit, num_hours=24, limit=100):
    offenders_idx = {}
    banned_idx = {}
    reached = False
    for log in reddit.subreddit('coronavirus').mod.log(limit=limit):
        created = datetime.datetime.fromtimestamp(log.created_utc)
        action = log.action
        offender = log.target_author
        if action not in KEEP_ACTIONS:
            continue
        if action == 'banuser':
            if offender not in banned_idx:
                banned_idx[offender] = log.details
        else:
            target_link = log.target_permalink
            if offender not in offenders_idx:
                offenders_idx[offender] = set([])
            offenders_idx[offender].add(target_link)


        if datetime.datetime.now() - datetime.timedelta(hours=num_hours) > created:
            print('REACHED 24H')
            reached = True
            break
    return reached, offenders_idx, banned_idx


def get_offenders_string(reddit, num_hours=24, top_k=10):
    offenders_idx, banned_idx = get_top_offenders(reddit, num_hours=num_hours)
    lb_string = 'Top offenders in modlog from past {} hours\n'.format(num_hours)
    counter = 0
    for offender, v in reversed(sorted(offenders_idx.items(), key=lambda item: len(item[1]))):
        counter += 1
        if counter > top_k:
            break
        profile = 'https://reddit.com/u/{}'.format(offender)
        ban_string = ''
        if offender in banned_idx:
            ban_string = 'Banned: {}\n'.format(banned_idx[offender])
        lb_string += '#{} {} ({}) \n\tRemoved or spammed contributions: {}\n'.format(counter, offender, profile, len(v), ban_string)
    return lb_string


if __name__ == "__main__":
    reddit = authorize()
    print(get_offenders_string(reddit, num_hours=5))