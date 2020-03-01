from reddit_bot import get_modqueue, authorize



def clear_queue(reddit):
    modset = set([k.name for k in reddit.subreddit('coronavirus').moderator()])
    queue = get_modqueue(reddit)
    approve_count = 0
    for qi in queue:
        if qi.author.name in modset:
            print('approving submission {} {}'.format(qi.author.name, qi.submission.id))
            qi.mod.approve()
            approve_count += 1
    print('finished clearing queue')
    return approve_count


if __name__ == "__main__":
    reddit = authorize()
    clear_queue(reddit)