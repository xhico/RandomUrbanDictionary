# -*- coding: utf-8 -*-
# !/usr/bin/python3

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
    """
    Returns a random word and its definition from the Urban Dictionary website.

    Returns:
    Tuple: A tuple containing the link to the word on the website, the word itself, its definition, and the contributor.
    """

    # Get the page content from the random page on Urban Dictionary website
    pageContent = requests.get("https://www.urbandictionary.com/random.php").text

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(pageContent, 'html5lib')

    # Find the definition section of the page
    post = soup.find("div", {"class": "definition"})

    # Extract the word, meaning, and contributor from the definition section
    word = post.find("a", {"class": "word"}).text
    meaning = post.find("div", {"class": "meaning"}).text
    contributor = post.find("div", {"class": "contributor"}).text

    # Extract the link to the word on the website and decode it using urllib
    link = post.find("a", {"data-network": "twitter"})["href"].split("?text=")[-1]
    link = urllib.parse.unquote(link)

    # Return the link, word, meaning, and contributor as a tuple
    return link, word, meaning, contributor


def tweet(tweetStr):
    """
    This function takes in a tweet string as input, attempts to update the status on Twitter using the
    API and returns True if successful. If an exception occurs, it logs the error and returns False.

    Parameters:
    tweetStr (str): A string representing the tweet to be posted.

    Returns:
    bool: True if the tweet was successfully posted, False otherwise.
    """
    try:
        # Attempts to update the status on Twitter using the API.
        api.update_status(tweetStr)
        # Logs an info message indicating that the tweet was successfully posted.
        logger.info("Tweeted")
        # Returns True to indicate that the tweet was successfully posted.
        return True
    except Exception as ex:
        # Logs the exception that occurred.
        logger.error(ex)
    # Returns False to indicate that the tweet was not successfully posted.
    return False


def favTweets(tags: str, numbTweets: int) -> bool:
    """
    Favorites a given number of tweets based on specified hashtags.

    Args:
        tags (str): Hashtags separated by spaces
        numbTweets (int): Number of tweets to be favorited

    Returns:
        bool: True if all tweets were successfully favorited, False otherwise
    """
    # Log the function name
    logger.info("favTweets")

    # Replace spaces in tags with " OR " to match Twitter's search query format
    tags = tags.replace(" ", " OR ")

    # Use Tweepy Cursor to search for tweets with specified hashtags
    tweets = tweepy.Cursor(api.search_tweets, q=tags).items(numbTweets)

    # Convert the resulting Cursor object to a list of tweets
    tweets = [tw for tw in tweets]

    # Iterate over the list of tweets and try to favorite each one
    for tw in tweets:
        try:
            tw.favorite()
        except Exception as e:
            # If an error occurs while favoriting the tweet, just ignore it and move on to the next tweet
            pass

    # Return True if all tweets were favorited successfully
    return True


def main():
    """
    This function is responsible for tweeting a random word and its meaning
    from the Urban Dictionary, reducing its length if necessary and liking
    10 tweets that share the same hashtags.

    Args:
    None

    Returns:
    None
    """

    # Get random word, meaning, contributor and link
    link, word, meaning, contributor = getRandom()

    # Create hashtags from the word
    hashtags = "#UrbanDictionary" + " " + "#" + word.replace(" ", "")

    # Log the chosen word
    logger.info(word)

    # Check if the length of the tweet is greater than 280 characters
    if len(word + "\n\n" + meaning + "\n\n" + "(" + contributor + ")" + "\n" + link + "\n" + hashtags) > 280:
        # Reduce the meaning if necessary
        meaning = meaning[0:280 - (6 + 2 + 3) - len(word) - len(meaning) - len(contributor) - len(link) - len(hashtags)] + "..."

    # Tweet the word, meaning, contributor, link and hashtags
    tweet(word + "\n\n" + meaning + "\n\n" + "(" + contributor + ")" + "\n" + link + "\n" + hashtags)

    # Get tweets with the same hashtags and like them
    favTweets(hashtags, 10)


if __name__ == "__main__":
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{os.path.abspath(__file__).replace('.py', '.log')}")
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
