import json
import os
import praw
from datetime import datetime
from helper_tools import remove_emojis
from crewai_tools import BaseTool
import streamlit as st

class RedditTrends(BaseTool):
    name: str = "Reddit Trends"
    description: str = "Fetches the latest trends from our favorite subreddits."

    def _run(self, subreddits=None) -> dict:
        """
        Executes the Reddit API to scrape the top posts and their best two comments from specified subreddits.

        Parameters:
            subreddits (list of str): Optional; a list of subreddit names to scrape. If not provided, the function defaults to
                                      scraping posts from 'selfhosted', 'homelab', 'HomeNetworking', and 'HomeServer'.
                                      A maximum of three subreddits can be specified at a time.

        Returns:
            dict: A dictionary where each key is a subreddit and the value is a list of the top posts from that subreddit,
                  each post accompanied by its top two comments.

        Notes:
            Ensure that the subreddit names are correctly spelled and are existing subreddits on Reddit. The function is
            limited to scraping no more than three subreddits at once to maintain performance and adhere to API usage guidelines.
        """
        return self.scrape_reddit(subreddits)

    def scrape_reddit(self, subreddits=None):
        """
        Executes the Reddit API to scrape the top posts and their best two comments from specified subreddits.

        Parameters:
            subreddits (list of str): Optional; a list of subreddit names to scrape. If not provided, the function defaults to
                                      scraping posts from 'selfhosted', 'homelab', 'HomeNetworking', and 'HomeServer'.
                                      A maximum of three subreddits can be specified at a time.

        Returns:
            dict: A dictionary where each key is a subreddit and the value is a list of the top posts from that subreddit,
                  each post accompanied by its top two comments.

        Notes:
            Ensure that the subreddit names are correctly spelled and are existing subreddits on Reddit. The function is
            limited to scraping no more than three subreddits at once to maintain performance and adhere to API usage guidelines.
        """

        print("Scraping Reddit for the latest trends...")
        # Setup Credentials
        reddit = praw.Reddit(
            client_id=st.secrets["REDDIT_CLIENT_ID"],
            client_secret=st.secrets["REDDIT_CLIENT_SECRET"],
            user_agent="aiquill by /u/tuantruong84",
        )

        # Start up with these subreddits
        if subreddits is None:
            subreddits = ["Startup_Ideas", "startups", "Entrepreneur"]

        if len(subreddits) > 3:
            raise Exception("Maximum of 3 subreddits at the time.")

        print(f"Scraping Reddit for the latest trends from {subreddits}...")
        max_amount_of_posts = 3

        scrapped_reddit_data = {}
        for subreddit in subreddits:
            sub = reddit.subreddit(subreddit)

            for post in sub.hot(limit=max_amount_of_posts):
                posts = {
                    "title": remove_emojis(post.title),
                    "url": post.url,
                    "score": post.score,
                    # "description": post.selftext,
                    "comments": [],
                    "created": datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
                }

                try:
                    post.comments.replace_more(limit=0)
                    comments = post.comments.list()[:5]

                    for comment in comments:
                        posts["comments"].append(remove_emojis(comment.body))

                    scrapped_reddit_data.setdefault(sub.display_name, []).append(posts)

                except praw.exceptions.APIException as e:
                    print(f"API exception occurred {e}")
        print("scraping done!",scrapped_reddit_data)
        return scrapped_reddit_data


def testCode():
    reddit = RedditTrends()
    results = reddit.scrape_reddit()
    print(len(results))

    with open("data.json", "w") as f:
        json.dump(results, f)


if __name__ == "__main__":
    testCode()
