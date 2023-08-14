from mastodon import Mastodon
import os
from config import client_secret, access_token, hashtag_to_boost, api_base_url, app_name


mast = Mastodon(
    app_name,
    client_secret = client_secret,
    access_token = access_token,
    api_base_url = api_base_url
)

def hashtags(toot):
    htgs = []
    for ht in toot['tags']:
        htgs.append(ht['name'])
    return set(htgs)



with open('reblog-history.log', 'r') as history:
    reblog_history = history.readlines()

reblog_history = [l.strip() for l in reblog_history]

for account in mast.account_following(mast.me(), limit=200):
    uname = account['username']
    uid = str(account['id'])
    uid_fn = f'{uid}.log'
    if os.path.isfile(uid_fn):
        with open(uid_fn, 'r') as uid_f:
            #user already known, fetch since last boosted post
            user_last_boosted_toot_id = uid_f.read().strip()
            statuses = mast.account_statuses(account['id'], tagged=hashtag_to_boost, since_id=user_last_boosted_toot_id, limit = 10)
    else:
        #fetch only the most recent matching toot of this user
        statuses = mast.account_statuses(account['id'], tagged=hashtag_to_boost, limit = 1)

    print(f'Fetching toots for {uname} (Id: {uid})')

    for toot in statuses:
        toot_id = str(toot['id'])
        if toot['reblogged'] or toot_id in reblog_history:
            continue
        with open(f'{uid}.log', 'w') as user_last_log:
            user_last_log.write(toot_id)
        with open(uid_fn, 'w') as uid_f:
            uid_f.write(toot_id)

        toot_url = toot['url']
        print(f'Found new toot to reblog: {toot_url}')
        mast.status_reblog(toot_id, visibility='public')
        with open('reblog-history.log', 'a') as history:
            history.write(toot_url + '\n')

