#!/bin/env python3

import os
import argparse

import twitter # package python-twitter

def store(status, term):
    id = status.id_str
    dir = os.path.join(term, id[:4], id[4:8])
    os.makedirs(dir, exist_ok=True) # from python 3.2, want python 3.4.1+
    path = os.path.join(dir, id)
    exists = os.path.exists(path)
    if not exists:
        with open(path, 'w') as f:
            f.write(status.AsJsonString())
    return not exists

def main(term, max_id=None):
    api = twitter.Api(consumer_key=os.getenv('TWITTER_API_KEY'),
                      consumer_secret=os.getenv('TWITTER_API_SECRET'),
                      access_token_key=os.getenv('TWITTER_ACCESS_TOKEN'),
                      access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))

    # https://dev.twitter.com/rest/reference/get/search/tweets
    count = 0
    new = True
    while new:
        results = api.GetSearch(term=term, count=100, result_type='recent', max_id=max_id)
        # are results ordered by tweet id?
        if results:
            for result in results:
                if not store(result, term):
                    new = False
                else:
                    count += 1
            max_id = results[-1].id - 1
        else:
            break
        print("stored:",count)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('term', help='search term')
    parser.add_argument('--before', type=int, help='search before this point (tweet id)')
    args = parser.parse_args()
    main(args.term, args.before)
