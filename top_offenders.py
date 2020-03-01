from reddit_bot import authorize
import datetime
from config import ACTIONS_PER_HOUR, LOG_MAX


KEEP_ACTIONS = {'removecomment', 'spamcomment', 'banuser', 'removelink', 'spamlink'}

def get_offender_profile(reddit, offender, num_hours=24):
    current_limit = ACTIONS_PER_HOUR*num_hours
    reached, offenses, banned = get_offender_profile_limit(reddit, offender, num_hours, current_limit)
    while reached is False and current_limit < LOG_MAX:
        current_limit = current_limit*2
        reached, offenses, banned = get_offender_profile_limit(reddit, offender, num_hours, current_limit)
    return offenses, banned


def get_offender_profile_limit(reddit, offender, num_hours, limit):
    offenses_idx = set([])
    banned = False
    reached = False
    for log in reddit.subreddit('coronavirus').mod.log(limit=limit):
        created = datetime.datetime.fromtimestamp(log.created_utc)
        if datetime.datetime.now() - datetime.timedelta(hours=num_hours) > created:
            print('REACHED with limit={}'.format(limit))
            reached = True
            break
        action = log.action
        log_offender = log.target_author
        if action not in KEEP_ACTIONS or log_offender.lower() != offender.lower() or log.mod.name == 'AutoModerator':
            continue
        if action == 'banuser':
            banned = True
        else:
            target_link = log.target_permalink
            offenses_idx.add('https://reddit.com{}'.format(target_link))

    return reached, offenses_idx, any(reddit.subreddit('coronavirus').banned(redditor=offender))


def get_offender_profile_string(reddit, offender, num_hours=24):
    offenses, banned = get_offender_profile(reddit, offender, num_hours=num_hours)
    banned_string = ''
    if banned:
        banned_string = '(User is currently banned)'
    p_string = 'Contributions from {} removed in the past {} hours {}\n'.format(offender, num_hours, banned_string)
    counter = 0
    for offense in offenses:
        counter += 1
        p_string += '\t{}\n'.format(offense)
        if len(p_string) > 500:
            p_string += '... {} more'.format(len(offenses) - counter)
            break
    return p_string


def get_top_offenders(reddit, num_hours=24):
    current_limit = ACTIONS_PER_HOUR*num_hours
    reached, offenders_idx, banned_idx = get_top_offenders_limit(reddit, num_hours, current_limit)
    while reached is False and current_limit < LOG_MAX:
        current_limit = current_limit*2
        reached, offenders_idx, banned_idx = get_top_offenders_limit(reddit, num_hours, current_limit)
    return offenders_idx, banned_idx


def get_top_offenders_limit(reddit, num_hours=24, limit=100):
    offenders_idx = {}
    banned_idx = {}
    reached = False
    for log in reddit.subreddit('coronavirus').mod.log(limit=limit):
        created = datetime.datetime.fromtimestamp(log.created_utc)
        if datetime.datetime.now() - datetime.timedelta(hours=num_hours) > created:
            print('REACHED with limit={}'.format(limit))
            reached = True
            break
        action = log.action
        offender = log.target_author
        if action not in KEEP_ACTIONS or log.mod.name == 'AutoModerator' or offender == '[deleted]' \
                or offender == 'AutoModerator':
            continue
        if action == 'banuser':
            if offender not in banned_idx:
                banned_idx[offender] = log.details
        else:
            target_link = log.target_permalink
            if offender not in offenders_idx:
                offenders_idx[offender] = set([])
            offenders_idx[offender].add(target_link)

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
        if any(reddit.subreddit('coronavirus').banned(redditor=offender)):
            ban_string = '\tCurrently banned\n'
        lb_string += '#{} {} ({}) \n\tRemoved or spammed contributions: {}\n{}'.format(counter, offender, profile, len(v), ban_string)
    return lb_string


if __name__ == "__main__":
    reddit = authorize()
    print(get_offenders_string(reddit, num_hours=12))