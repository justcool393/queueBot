from reddit_bot import authorize, get_modqueue
from praw.models import Comment, Submission

def get_comment_report_data(reddit):
    queue = list(get_modqueue(reddit))
    num_comments_idx = {}
    reports_idx = {}
    for qi in queue:
        if type(qi) == Comment:
            for ur in qi.user_reports:
                if ur[0] is not None and ur[0].lower().find('political') != -1:
                    sub = qi.submission
                    if sub.locked:
                        continue
                    sub_id = sub.id
                    print('got submission {}'.format(sub_id))
                    if sub_id not in num_comments_idx:
                        print('fetching comment number for {}'.format(sub_id))
                        num_comments = sub.num_comments
                        num_comments_idx[sub_id] = num_comments
                    if sub_id not in reports_idx:
                        reports_idx[sub_id] = set([])
                    reports_idx[sub_id].add(qi.id)
                    break
    return num_comments_idx, reports_idx


if __name__ == "__main__":
    reddit = authorize()
    get_comment_report_data(reddit)