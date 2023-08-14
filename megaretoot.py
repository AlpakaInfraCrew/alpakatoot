from mastodon import Mastodon
import os
from config import client_secret, access_token, hashtag_to_boost, api_base_url, app_name
import argparse
import pathlib
import sys

parser = argparse.ArgumentParser(
                    prog='MEGARETOOT',
                    description='This script boosts the toots using a given hashtag of the accounts you are following.')


parser.add_argument('-d', '--dry',
                    action='store_true', dest='dry',
                    help='Dry run, use this on the first run to ignore any toots from the past.')
parser.add_argument('-f', '--force',
                    action='store_true', dest='force',
                    help='If ran for the first time, -d is required. This can be overridden with -f.')
args = parser.parse_args()


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

if not os.path.isfile('reblog-history.log'):
    if not args.dry and not args.force:
        print('Warning, no logfile of a previous file detected. You might want to use --dry first to not boost any old toots! Use --force if you really want to do this.')
        sys.exit()
    pathlib.Path('reblog-history.log').touch()

with open('reblog-history.log', 'r') as history:
    reblog_history = history.readlines()

reblog_history = [l.strip() for l in reblog_history]

for account in mast.account_following(mast.me(), limit=200):
    uname = account['username']
    uid = str(account['id'])
    uid_fn = f'{uid}.log'
    if os.path.isfile(uid_fn):
        new_account = False
        with open(uid_fn, 'r') as uid_f:
            #user already known, fetch since last boosted post
            user_last_boosted_toot_id = uid_f.read().strip()
            statuses = mast.account_statuses(account['id'], tagged=hashtag_to_boost, since_id=user_last_boosted_toot_id, limit = 10)
    else:
        new_account = True
        #fetch only the most recent matching toot of this user
        statuses = mast.account_statuses(account['id'], tagged=hashtag_to_boost, limit = 1)
    if new_account and statuses:
        print(f"New account {uname} since last run, with existing post, ignoring until next run.")

    print(f'Fetching toots for {uname} (Id: {uid})')

    for toot in statuses:
        toot_id = str(toot['id'])
        toot_url = toot['url']
        if toot_id in reblog_history:
            continue
        with open(uid_fn, 'w') as user_last_log:
            user_last_log.write(toot_id)
        with open('reblog-history.log', 'a') as history:
            history.write(toot_url + '\n')
        if toot['reblogged']:
            # maybe already manually boosted
            continue
        if not args.dry and not new_account:
            print(f'Found new toot to reblog: {toot_url}')
            breakpoint()
            mast.status_reblog(toot_id, visibility='public')
        else:
            print(f'Dry run selected or new account found. Not boosting {toot_url}.')


