# -*- coding: utf-8 -*-
# !/usr/bin/python3

# python3 -m pip install tweepy yagmail beautifulsoup4 html5lib python-dateutil --no-cache-dir

import datetime
import json
import os
import urllib

import yagmail
from dateutil.relativedelta import relativedelta
import requests
import tweepy
from bs4 import BeautifulSoup


def get911(key):
    with open('/home/pi/.911') as f:
        data = json.load(f)
    return data[key]


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


def getRandom():
    pageContent = requests.get("https://www.urbandictionary.com/random.php").text
    soup = BeautifulSoup(pageContent, 'html.parser')

    post = soup.find("div", {"class": "definition"})
    word = post.find("a", {"class": "word"}).text
    meaning = post.find("div", {"class": "meaning"}).text
    contributor = post.find("div", {"class": "contributor"}).text
    link = post.find("a", {"data-network": "twitter"})["href"].split("?text=")[-1]
    link = urllib.parse.unquote(link)
    return link, word, meaning, contributor


def tweet(tweetStr):
    api.update_status(tweetStr)
    print("Tweeted - " + tweetStr)

    return True


def favTweets(tags, numbTweets):
    tags = tags.replace(" ", " OR ")
    tweets = tweepy.Cursor(api.search_tweets, q=tags).items(numbTweets)
    tweets = [tw for tw in tweets]

    for tw in tweets:
        try:
            tw.favorite()
            print(str(tw.id) + " - Like")
        except Exception as e:
            print(str(tw.id) + " - " + str(e))
            pass

    return True


def main():
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        print("Login as: " + api.verify_credentials().screen_name)

        # Get link, word, meaning, contributor and hashtags
        link, word, meaning, contributor = getRandom()
        hashtags = "#UrbanDictionary" + " " + "#" + word.replace(" ", "")

        # Reduce meaning if necessary
        if len(word + "\n\n" + meaning + "\n\n" + "(" + contributor + ")" + "\n" + link + "\n" + hashtags) > 280:
            meaning = meaning[0:280 - (6 + 2 + 3) - len(word) - len(meaning) - len(contributor) - len(link) - len(hashtags)] + "..."

        # Tweet!
        tweet(word + "\n\n" + meaning + "\n\n" + "(" + contributor + ")" + "\n" + link + "\n" + hashtags)

        # Get tweets -> Like them
        favTweets(hashtags, 10)
    except Exception as ex:
        print(ex)
        yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "Error - " + os.path.basename(__file__), str(ex))


if __name__ == "__main__":
    main()
