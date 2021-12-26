# -*- coding: utf-8 -*-
# !/usr/bin/python3

# python3 -m pip install tweepy yagmail selenium --no-cache-dir

import json
import os

import tweepy
import yagmail
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


def tweet(str):
    api.update_status(str)
    print("Tweeted - " + str)

    return True


def getRandom():
    options = Options()
    options.headless = True
    service = Service("/home/pi/geckodriver")
    browser = webdriver.Firefox(service=service, options=options)
    browser.get("https://www.urbandictionary.com/random.php")

    post = browser.find_elements(By.CLASS_NAME, "def-panel")[0]
    header = post.find_elements(By.CLASS_NAME, "def-header")[0].find_elements(By.CLASS_NAME, "word")[0]
    link = header.get_attribute('href')
    word = header.text
    meaning = post.find_elements(By.CLASS_NAME, "meaning")[0].text
    contributor = post.find_elements(By.CLASS_NAME, "contributor")[0].text

    browser.close()
    return link, word, meaning, contributor


if __name__ == "__main__":
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        print("Login as: " + api.verify_credentials().screen_name)

        link, word, meaning, contributor = getRandom()
        hashtags = "#UrbanDictionary" + " " + "#" + word.replace(" ", "")

        if len(word + "\n\n" + meaning + "\n\n" + "(" + contributor + ")" + "\n" + link + "\n" + hashtags) > 280:
            meaning = meaning[0:280 - (6 + 2 + 3) - len(word) - len(meaning) - len(contributor) - len(link) - len(hashtags)] + "..."

        tweetStr = word + "\n\n" + meaning + "\n\n" + "(" + contributor + ")" + "\n" + link + "\n" + hashtags
        tweet(tweetStr)
    except Exception as ex:
        print(ex)
        yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "Error - " + os.path.basename(__file__), str(ex))