# -*- coding: utf-8 -*-
# !/usr/bin/python3

# python3 -m pip install tweepy yagmail selenium --no-cache-dir

import datetime
import json
import os
import urllib.parse

import tweepy
import yagmail
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


def get911(key):
    f = open('/home/pi/.911')
    data = json.load(f)
    f.close()
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


def tweet(tweetStr):
    api.update_status(tweetStr)
    print("Tweeted - " + tweetStr)

    return True


def getRandom(browser):
    browser.get("https://www.urbandictionary.com/random.php")

    post = browser.find_elements(By.CLASS_NAME, "definition")[0]
    word = post.find_elements(By.CLASS_NAME, "word")[0].text
    meaning = post.find_elements(By.CLASS_NAME, "meaning")[0].text
    contributor = post.find_elements(By.CLASS_NAME, "contributor")[0].text
    link = post.find_elements(By.TAG_NAME, "a")[0].get_attribute('href').split("?text=")[-1]
    link = urllib.parse.unquote(link)

    return link, word, meaning, contributor


def getTweets(tags, dateSince, numbTweets):
    tags = tags.replace(" ", " OR ")
    tweets = tweepy.Cursor(api.search_tweets, q=tags, since=dateSince).items(numbTweets)
    tweets = [tw for tw in tweets]
    return tweets


def favTweets(tweets):
    for tw in tweets:
        try:
            tw.favorite()
            print(str(tw.id) + " - Like")
        except Exception as e:
            print(str(tw.id) + " - " + str(e))
            pass

    return True


def main():
    options = Options()
    options.headless = True
    service = Service("/home/pi/geckodriver")
    browser = webdriver.Firefox(service=service, options=options)

    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        print("Login as: " + api.verify_credentials().screen_name)

        # Get link, word, meaning, contributor and hashtags
        link, word, meaning, contributor = getRandom(browser)
        hashtags = "#UrbanDictionary" + " " + "#" + word.replace(" ", "")

        # Reduce meaning if necessary
        if len(word + "\n\n" + meaning + "\n\n" + "(" + contributor + ")" + "\n" + link + "\n" + hashtags) > 280:
            meaning = meaning[0:280 - (6 + 2 + 3) - len(word) - len(meaning) - len(contributor) - len(link) - len(hashtags)] + "..."

        # Tweet!
        tweet(word + "\n\n" + meaning + "\n\n" + "(" + contributor + ")" + "\n" + link + "\n" + hashtags)

        # Set deltaDate | Set numbTweets | Set Hashtags
        deltaDate = datetime.date.today() + relativedelta(months=-1)
        numTweets = 10

        # Get tweets -> Like them
        tws = getTweets(hashtags, deltaDate, numTweets)
        favTweets(tws)
    except Exception as ex:
        print(ex)
        yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "Error - " + os.path.basename(__file__), str(ex))
    finally:
        browser.close()


if __name__ == "__main__":
    main()
