from reddit_bot import authorize, get_modqueue
from praw.models import Comment, Submission
from config import TOXICITY_THRESHOLD

def get_comment_report_data(reddit):
    queue = list(get_modqueue(reddit))
    num_comments_idx = {}
    reports_idx = {}
    for qi in queue:
        if type(qi) == Comment:
            for ur in qi.user_reports:
                if ur[0] is not None and ur[0].lower().find('political') != -1:
                    sub = qi.submission
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

def analyze_queue(reddit):
    submission_analysis = {}
    print('analyzing queue...')
    num_comments_idx, reports_idx = get_comment_report_data(reddit)
    print('got queue analysis results')
    for sub_id, comment_count in num_comments_idx.items():
        if sub_id not in submission_analysis:
            submission_analysis[sub_id] = {}
            submission_analysis[sub_id]['num_comments'] = 0
            submission_analysis[sub_id]['reported_comments'] = set([])
            submission_analysis[sub_id]['reported_to_mods'] = False
        submission_analysis[sub_id]['num_comments'] = max(comment_count,
                                                               submission_analysis[sub_id]['num_comments'])
    for sub_id, reports in reports_idx.items():
        for comment_id in reports:
            submission_analysis[sub_id]['reported_comments'].add(comment_id)
    for sub_id, submission_meta in submission_analysis.items():
        political_toxicity_score = float(len(submission_meta['reported_comments'])) / submission_meta['num_comments']
        print('political_toxicity_score for submission {} is {}'.format(sub_id, political_toxicity_score))
        if political_toxicity_score > TOXICITY_THRESHOLD and submission_analysis[sub_id]['reported_to_mods'] is False:
            toxic_submission = reddit.submission(id=sub_id)
            if toxic_submission.locked:
                print("it's already locked")
            else:
                print('submission at {} is potentially a political wasteland'.format(toxic_submission.shortlink))

if __name__ == "__main__":
    reddit = authorize()
    analyze_queue(reddit)