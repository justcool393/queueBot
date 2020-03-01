from reddit_bot import authorize
import datetime




KEEP_ACTIONS = {'approvecomment', 'removecomment', 'spamcomment', 'banuser', 'approvelink', 'removelink', 'spamlink',
                'editflair', 'lock'}

ACTIONS_PER_HOUR = 150
LOG_MAX = 10000

def get_leaderboard(reddit, num_hours=24):
    current_limit = ACTIONS_PER_HOUR*num_hours
    reached, mods_actions_idx, approve_idx, remove_idx, lock_idx, ban_idx, flair_idx = get_leaderboard_limit(reddit, num_hours, current_limit)
    while reached is False and current_limit < LOG_MAX:
        current_limit = current_limit*2
        reached, mods_actions_idx, approve_idx, remove_idx, lock_idx, ban_idx, flair_idx = get_leaderboard_limit(reddit,
                                                                                                                 num_hours,
                                                                                                                 current_limit)
    return mods_actions_idx, approve_idx, remove_idx, lock_idx, ban_idx, flair_idx


def get_leaderboard_limit(reddit, num_hours=24, limit=100):
    mods_actions_idx = {}
    flair_idx = {}
    ban_idx = {}
    remove_idx = {}
    approve_idx = {}
    lock_idx = {}
    modset = set([])
    reached = False
    for log in reddit.subreddit('coronavirus').mod.log(limit=limit):
        mod = log.mod
        created = datetime.datetime.fromtimestamp(log.created_utc)
        action = log.action
        if action not in KEEP_ACTIONS or mod == 'AutoModerator':
            continue
        modset.add(mod)
        if datetime.datetime.now() - datetime.timedelta(hours=num_hours) > created:
            print('REACHED 24H')
            reached = True
            break
        target = log.target_permalink
        if mod not in mods_actions_idx:
            mods_actions_idx[mod] = 0
        mods_actions_idx[mod] += 1
        if action == 'banuser':
            if mod not in ban_idx:
                ban_idx[mod] = 0
            ban_idx[mod] += 1
        elif action == 'editflair':
            if mod not in flair_idx:
                flair_idx[mod] = 0
            flair_idx[mod] += 1
        elif action.find('approve') != -1:
            if mod not in approve_idx:
                approve_idx[mod] = 0
            approve_idx[mod] += 1
        elif action == 'lock':
            if mod not in lock_idx:
                lock_idx[mod] = 0
            lock_idx[mod] += 1
        else:
            if mod not in remove_idx:
                remove_idx[mod] = 0
            remove_idx[mod] += 1
    return reached, mods_actions_idx, approve_idx, remove_idx, lock_idx, ban_idx, flair_idx

def print_leaderboard(mods_actions_idx, approve_idx, remove_idx, lock_idx, ban_idx, flair_idx, top_k=5):
    counter = 0
    for mod, v in reversed(sorted(mods_actions_idx.items(), key=lambda item: item[1])):
        counter += 1
        if counter > top_k:
            break
        actions = mods_actions_idx[mod]
        approvals = 0
        if mod in approve_idx:
            approvals = approve_idx[mod]
        removals = 0
        if mod in remove_idx:
            removals = remove_idx[mod]
        locks = 0
        if mod in lock_idx:
            locks = lock_idx[mod]
        bans = 0
        if mod in ban_idx:
            bans = ban_idx[mod]
        flairs = 0
        if mod in flair_idx:
            flairs = flair_idx[mod]
        print('#{} {} \n\tactions: {} \n\tapprovals: {} removals: {} \n\tlocks: {} bans: {} flairs: {}'.format(counter, mod,
                                                                                                    actions, approvals,
                                                                                                    removals, locks, bans,
                                                                                                    flairs))

def get_leaderboard_string(reddit, num_hours=24, top_k=5):
    mods_actions_idx, approve_idx, remove_idx, lock_idx, ban_idx, flair_idx = get_leaderboard(reddit, num_hours=num_hours)
    lb_string = 'Mod action leaderboard from past {} hours\n'.format(num_hours)
    counter = 0
    for mod, v in reversed(sorted(mods_actions_idx.items(), key=lambda item: item[1])):
        counter += 1
        if counter > top_k:
            break
        actions = mods_actions_idx[mod]
        approvals = 0
        if mod in approve_idx:
            approvals = approve_idx[mod]
        removals = 0
        if mod in remove_idx:
            removals = remove_idx[mod]
        locks = 0
        if mod in lock_idx:
            locks = lock_idx[mod]
        bans = 0
        if mod in ban_idx:
            bans = ban_idx[mod]
        flairs = 0
        if mod in flair_idx:
            flairs = flair_idx[mod]
        lb_string += '#{} {} \n\tactions: {} \n\tapprovals: {} removals: {} \n\tlocks: {} bans: {} flairs: {}\n'.format(counter,
                                                                                                               mod,
                                                                                                               actions,
                                                                                                               approvals,
                                                                                                               removals,
                                                                                                               locks,
                                                                                                               bans,
                                                                                                               flairs)
    return lb_string


if __name__ == "__main__":
    reddit = authorize()
    print(get_leaderboard_string(reddit, num_hours=1.5))