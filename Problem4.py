__author__ = 'Chan'

import re
import sys
import time
import json
import twitter
from urllib2 import URLError
from httplib import BadStatusLine


"""
# This class mines tweeters from users given.
Users and their tweets are divided into three groups: apple follower, android follower and who follow both.
"""

CONSUMER_KEY = 'Wjt80JOnmCyCdaEaEuRh2A6AY'
CONSUMER_SECRET = 'ro7hJq0pOyap1Ku2qtgLvAcLXnI4lwBfoFhmKeDqT2Aej7RLU5'
OAUTH_TOKEN = '3591772283-m8PplZzZnSkm6mgYiZgkVIAAffJcvtNO4uDaYpC'
OAUTH_TOKEN_SECRET = 'yFN4ZKbthcBfYE1B43TMinhTzGrtVri9fC2gg0nxjZfN0'

HOLDER = 0


def read_txt(path):
    # This is a temp function designed for reading user ID
    f = open(path, 'r')
    id_list = []
    pattern = re.compile('\w+', re.S)
    for line in f:
        id_list.append(line)
    for ids in range(len(id_list)):
        id_list[ids] = re.match(pattern, id_list[ids]).group()
    return id_list


def oath_creator():
    # This function create a standard twitter API.
    # Will be replaced whenever other parts completed.
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api


def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600:  # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e

        # See https://dev.twitter.com/docs/error-codes-responses for common codes

        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429:
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60 * 15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e  # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                                 (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function

    wait_period = 2
    error_count = 0

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise


class TweetMiner(object):
    # Save fans' ID
    # Tweets are saved in dictionary. The keys are ID, the values are words in tweets.
    def __init__(self, apple_fan, android_fan, both_sides):
        self.apple_fan = apple_fan
        self.android_fan = android_fan
        self.both_sides = both_sides
        self.apple_tweets = {}
        self.android_tweets = {}
        self.both_sides_tweets = {}
        self.oath = oath_creator()

    def __str__(self):
        return "TweetMiner mines tweeters from users given. Users and their tweets are divided into three groups."

    def harvest(self, user_id, date='08', year='2015', **group):
        flag = False
        # Given group and user_id, fetch his/her tweets.
        group[user_id] = []
        kw = {  # Keyword args for the Twitter API call
                'count': 200,
                'since_id': 1,
                'user_id': user_id,
                }

        tweets = make_twitter_request(self.oath.statuses.user_timeline, **kw)

        if tweets is None:  # 401 (Not Authorized) - Need to bail out on loop entry
            tweets = []
            group[user_id].append(tweets)
            return

        screen_tweets = []
        for tweet in tweets:
            created_date = tweet["created_at"].split()[1:4]
            created_year = tweet["created_at"].split()[5]
            # If the tweet was created in Sep, convert its format. If not, abandon it.
            if created_date[0] == 'Sep':
                created_date[0] == '09'
            else:
                continue
            if created_date[1] == date:
                if created_year == year:
                    if 'iPhone' in tweet['text'] or 'Apple' in tweet['text'] or 'iphone' in tweet['text'] or 'apple' in tweet['text']:
                        screen_tweets.append(tweet['text'])
                        flag = True

        group[user_id].append([screen_tweet.split() for screen_tweet in screen_tweets])
        if flag:
            print 'hola'


android_group = {}
id_list = read_txt('/Users/Chan/GitHub/GO_DS501/AppStore_followers.txt')
tm = TweetMiner([], [], [])
for ids in id_list:
    tm.harvest(ids, '09', '2015', **android_group)


# test = TweetMiner([3591772283], [], [])
# test.harvest('3591772283', date='19')


