# -*- coding: utf-8 -*-
# !/usr/bin/python3

# python3 -m pip install tweepy yagmail beautifulsoup4 html5lib python-dateutil psutil --no-cache-dir

import os
import urllib.parse
import psutil
import yagmail
import requests
import tweepy
import traceback
import logging
from bs4 import BeautifulSoup
from Misc import get911


def getRandom():
    pageContent = requests.get("https://www.urbandictionary.com/random.php").text
    soup = BeautifulSoup(pageContent, 'html5lib')

    post = soup.find("div", {"class": "definition"})
    word = post.find("a", {"class": "word"}).text
    meaning = post.find("div", {"class": "meaning"}).text
    contributor = post.find("div", {"class": "contributor"}).text
    link = post.find("a", {"data-network": "twitter"})["href"].split("?text=")[-1]
    link = urllib.parse.unquote(link)
    return link, word, meaning, contributor


def tweet(tweetStr):
    try:
        api.update_status(tweetStr)
        logger.info("Tweeted")
        return True
    except Exception as ex:
        logger.error(ex)
    return False


def favTweets(tags, numbTweets):
    logger.info("favTweets")
    tags = tags.replace(" ", " OR ")
    tweets = tweepy.Cursor(api.search_tweets, q=tags).items(numbTweets)
    tweets = [tw for tw in tweets]

    for tw in tweets:
        try:
            tw.favorite()
        except Exception as e:
            pass

    return True


def main():
    # Get link, word, meaning, contributor and hashtags
    link, word, meaning, contributor = getRandom()
    hashtags = "#UrbanDictionary" + " " + "#" + word.replace(" ", "")
    logger.info(word)
    # logger.info(meaning)
    # logger.info(link)
    # logger.info(contributor)
    # logger.info(hashtags)

    # Reduce meaning if necessary
    if len(word + "\n\n" + meaning + "\n\n" + "(" + contributor + ")" + "\n" + link + "\n" + hashtags) > 280:
        meaning = meaning[0:280 - (6 + 2 + 3) - len(word) - len(meaning) - len(contributor) - len(link) - len(hashtags)] + "..."

    # Tweet!
    tweet(word + "\n\n" + meaning + "\n\n" + "(" + contributor + ")" + "\n" + link + "\n" + hashtags)

    # Get tweets -> Like them
    favTweets(hashtags, 10)


if __name__ == "__main__":
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.abspath(__file__).replace(".py", ".log"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("----------------------------------------------------")

    CONSUMER_KEY = get911('TWITTER_URBAN_CONSUMER_KEY')
    CONSUMER_SECRET = get911('TWITTER_URBAN_CONSUMER_SECRET')
    ACCESS_TOKEN = get911('TWITTER_URBAN_ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = get911('TWITTER_URBAN_ACCESS_TOKEN_SECRET')
    EMAIL_USER = get911('EMAIL_USER')
    EMAIL_APPPW = get911('EMAIL_APPPW')
    EMAIL_RECEIVER = get911('EMAIL_RECEIVER')

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    # Check if script is already running
    procs = [proc for proc in psutil.process_iter(attrs=["cmdline"]) if os.path.basename(__file__) in '\t'.join(proc.info["cmdline"])]
    if len(procs) > 2:
        logger.info("isRunning")
    else:
        try:
            main()
        except Exception as ex:
            logger.error(traceback.format_exc())
            yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "Error - " + os.path.basename(__file__), str(traceback.format_exc()))
        finally:
            logger.info("End")
