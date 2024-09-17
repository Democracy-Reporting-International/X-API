# This script was used in the July 2024 investigation into political speech on X by the DD team.
# It allows you to access the X API, for which you will need a paid basic developer account, and retrieve all tweets from a group of users within a time frame.

import requests
import pandas as pd
import time
import os
import tweepy
from datetime import datetime, timedelta

#Replace the "" with the actual keys retrieved from the developer portal. They should be long strings of digits and letters.
client = tweepy.Client(bearer_token="bearer token",
                       consumer_key="consumer key",
                       consumer_secret="consumer secret",
                       access_token="access token",
                       access_token_secret="access token secret")

PATH = "/content/drive/" #if using Google Collab

# DEFINE THE FUNCTIONS

#The function below is for retrieving ALL the tweets from a single user within a defined time frame. It has several checks within it in case the connection to the API times out or the rate or post limit is exceeded.
#For each tweet, this request will retrieve all relevant information allowed by the API v2, including information about the account which posted it.
def get_tweets_in_timeframe(client, user_id, start_date, end_date, retries=3, backoff_factor=2):
    # Convert dates to the correct format
    start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_date_str = (end_date + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')  # Add one day to include end_date

    tweets_data = []
    next_token = None

    while True:
        for attempt in range(retries):
            try:
                # Fetch tweets within the date range
                response = client.get_users_tweets(
                    id=user_id,
                    start_time=start_date_str,
                    end_time=end_date_str,
                    tweet_fields=['id', 'created_at', 'text', 'public_metrics', 'author_id', 'conversation_id', 'entities', 'geo', 'in_reply_to_user_id', 'lang', 'possibly_sensitive', 'referenced_tweets', 'source', 'attachments', 'withheld'],
                    user_fields=['id', 'name', 'username', 'location', 'description', 'verified', 'profile_image_url', 'public_metrics'],
                    expansions=['author_id'],
                    max_results=100,
                    pagination_token=next_token
                )
                break  # If request is successful, exit the loop
            except (ConnectionError, Timeout, TooManyRequests) as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    sleep_time = backoff_factor * (2 ** attempt)
                    print(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    print("Max retries reached. Moving on.")
                    return tweets_data

        if response.data is None:
            print(f"No tweets found for user_id {user_id} in the specified date range.")
            return tweets_data

        users = {u['id']: u for u in response.includes['users']} if 'users' in response.includes else {}

        for tweet in response.data:
            author = users.get(tweet.author_id)
            tweets_data.append({
                'id': tweet.id,
                'created_at': tweet.created_at.replace(tzinfo=None),  # Make datetime timezone naive
                'text': tweet.text,
                'retweet_count': tweet.public_metrics['retweet_count'],
                'reply_count': tweet.public_metrics['reply_count'],
                'like_count': tweet.public_metrics['like_count'],
                'quote_count': tweet.public_metrics['quote_count'],
                'author_id': tweet.author_id,
                'conversation_id': tweet.conversation_id,
                'entities': tweet.entities,
                'geo': tweet.geo,
                'in_reply_to_user_id': tweet.in_reply_to_user_id,
                'lang': tweet.lang,
                'possibly_sensitive': tweet.possibly_sensitive,
                'referenced_tweets': tweet.referenced_tweets,
                'source': tweet.source,
                'attachments': tweet.attachments,
                'withheld': tweet.withheld,
                'author_name': author['name'] if author else None,
                'author_username': author['username'] if author else None,
                'author_location': author['location'] if author else None,
                'author_description': author['description'] if author else None,
                'author_verified': author['verified'] if author else None,
                'author_profile_image_url': author['profile_image_url'] if author else None,
                'author_followers_count': author['public_metrics']['followers_count'] if author else None,
                'author_following_count': author['public_metrics']['following_count'] if author else None,
                'author_tweet_count': author['public_metrics']['tweet_count'] if author else None,
                'author_listed_count': author['public_metrics']['listed_count'] if author else None
            })

        next_token = response.meta.get('next_token')
        if not next_token:
            break

    print(f"Number of tweets retrieved for user_id {user_id}: {len(tweets_data)}")
    return tweets_data

def export_to_excel(tweets_data, filename):
    # Convert the list to a DataFrame
    df = pd.DataFrame(tweets_data)
    # Define the path to save the file to Google Drive
    file_path = f'/content/drive/My Drive/{filename}'
    # Export the DataFrame to an Excel file
    df.to_excel(file_path, index=False)
    print(f"Tweets data exported to {file_path}")

# DEFINE THE TIMEFRAME AND ACCOUNT OF INTEREST

# Define the date range
start_date = datetime(2024, 4, 9)
end_date = datetime(2024, 6, 9)

#Replace with the username of interest
usernames = ["AfD"]

all_tweets_data = []

for username in usernames:
    user_get = client.get_user(username=username)
    user_id = user_get.data.id
    tweets_data = get_tweets_in_timeframe(client, user_id, start_date, end_date)
    all_tweets_data.extend(tweets_data)

# EXPORT 

# Export tweets data to an Excel file
export_to_excel(tweets_data, 'data.xlsx')
