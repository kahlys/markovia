import csv
import json
import random
import re
import tweepy
import schedule
import time
import datetime


def parse_tweets_to_file(account, filename):
    """
    Parse and saves tweets from account to a file

    Parameters:
        account (str): Twitter account name.
        filename (str): The file name where to write tweets.
    """

    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
    auth.set_access_token(config["access_key"], config["access_secret"])
    api = tweepy.API(auth)

    alltweets = []
    new_tweets = api.user_timeline(screen_name=account, count=200, tweet_mode='extended')
    alltweets.extend(new_tweets)
    oldest = alltweets[-1].id - 1
    while len(new_tweets) > 0:
        new_tweets = api.user_timeline(screen_name=account, count=200, max_id=oldest, tweet_mode='extended')
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        print("\rdownloading tweets {} (oldest id {}) ".format(len(alltweets), oldest), end="")
    print()

    # write to file
    with open(filename, 'w+', encoding="utf-8") as f:
        for t in alltweets:
            text = t.full_text
            print(text, file=f)


def generate_markov_text(filename):
    table = {}
    keyLen = 2
    wordMin = 5  # minimum of words needed for a sentence

    fh = open(filename, 'r', encoding="utf-8")

    # create markov dict from sentences in the file
    for line in fh:
        tweet_text = line.strip()
        tweet_text = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet_text, flags=re.MULTILINE) # remove links

        tokens = tweet_text.split()
        if len(tokens) < wordMin:
            continue

        keyList = []
        table.setdefault('#BEGIN#', []).append(tokens[0:keyLen])
        for item in tokens:
            if len(keyList) < keyLen:  # not enough items
                keyList.append(item)
                continue
            table.setdefault(tuple(keyList), []).append(item)
            keyList.pop(0)
            keyList.append(item)

    # generate a sentence, starting by a random BEGIN item
    key = list(random.choice(table['#BEGIN#']))
    res = " ".join(key)
    while True:
        newKey = table.setdefault(tuple(key), "")
        if(newKey == ""):
            break
        newVal = random.choice(newKey)
        res = res + " " + newVal
        if (newVal[-1] == ".") or (newVal[-1] == "?") or (newVal[-1] == "!"):
            break
        key.pop(0)
        key.append(newVal)

    return res


def write_tweet(text):
    auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
    auth.set_access_token(config["access_key"], config["access_secret"])
    api = tweepy.API(auth)
    api.update_status(status=text)


def job(): 
    # parse tweets, generate markov dict, generate sentence, write to twitter
    parse_tweets_to_file("EmmanuelMacron", "dataset.txt")
    sentence = generate_markov_text("dataset.txt")
    print(">>", sentence)
    write_tweet(sentence)


if __name__ == '__main__':
    global config

    # parse twitter api tokens from config file
    config = json.load(open('config.json'))

    schedule.every().day.at("09:22").do(job)
    schedule.every().day.at("16:36").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)