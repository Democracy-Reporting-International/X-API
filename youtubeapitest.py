
import pandas as pd
import os
from googleapiclient.discovery import build

all_videos_df = pd.DataFrame(columns=["Title", "Published At", "Channel", "Description", "Video ID", "Video URL"])


def fetch_videos(query, published_after, published_before):
    global all_videos_df

    # Set up API details
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyAxa45p95rs9b8rR1JZpTfV6W9kfggSSGE"
    #"AIzaSyBbFjui_l3LQSYs-60so4VFZ2aryX-E7Jo" #"AIzaSyAxa45p95rs9b8rR1JZpTfV6W9kfggSSGE" AIzaSyDfTTNMiXIW1nrPkX2SOFNgpPDdQqHsW2E

    youtube = build(api_service_name, api_version, developerKey=api_key)

    max_results_per_page = 50
    region_code = "DE"
    next_page_token = None

    while True:
        # Make the API request
        request = youtube.search().list(
            part="snippet",
            channelType="any",
            eventType="none",
            maxResults=max_results_per_page,
            order="viewCount",
            publishedAfter=published_after,
            publishedBefore=published_before,
            q=query,
            pageToken=next_page_token,
            regionCode=region_code  # Uncomment and set if needed
        )
        response = request.execute()

        # Extract video information and create a temporary DataFrame
        video_data = [
            {
                "Title": item['snippet']['title'],
                "Published At": item['snippet']['publishedAt'],
                "Channel": item['snippet']['channelTitle'],
                "Description": item['snippet']['description'],
                "Video ID": item['id']['videoId'],
                "Video URL": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            for item in response['items']
        ]

        temp_df = pd.DataFrame(video_data)

        # Concatenate the temporary DataFrame with the main one
        all_videos_df = pd.concat([all_videos_df, temp_df], ignore_index=True)

        # Check if there is another page of results
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

def display_videos_as_table():
    # Display the DataFrame as a table
    print(all_videos_df)

if __name__ == "__main__":
    # Example: Fetch videos with a specific query
    fetch_videos("Europe immigration exposed", "2024-04-01T00:00:00Z", "2024-06-30T00:00:00Z")

all_videos_df

PATH = "/content/drive/MyDrive/"
df_cleaned = all_videos_df.drop_duplicates(subset=['Video ID'])

#df_cleaned.to_excel(PATH+'immigration_ultimate.xlsx', index=False)

excel_df1 = pd.read_excel(PATH+'ukraine_videos.xlsx')
excel_df2 = pd.read_excel(PATH+'climate_ultimate.xlsx')

# Append the data from the Excel file to df_cleaned
df_combined = pd.concat([df_cleaned, excel_df1, excel_df2], ignore_index=True)
df_combined_cleaned = df_combined.drop_duplicates(subset=['Video ID'])

print(df_combined_cleaned)

video_ids = df_combined_cleaned['Video ID'].tolist()
comma_separated_ids = ','.join(video_ids)

# Step 3: Output the string so you can manually copy it
print(comma_separated_ids)

df_combined_cleaned.to_excel(PATH+'disinformation_ultimate.xlsx', index=False)

display_videos_as_table()

all_videos

import json

def read_json_file(file_path):
    # Load the JSON data from the file
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def parse_videos(data):
    # Initialize an empty list to hold the video data
    video_list = []

    # Loop through each video in the JSON data
    for video in data['videos']:
        # Extract the video details
        video_id = video.get('id')
        title = video.get('title')
        description = video.get('description')
        duration = video.get('duration')
        views = video.get('views')
        likes = video.get('likes')
        dislikes = video.get('dislikes')

        # Append the details to the video list
        video_list.append([video_id, title, description, duration, views, likes, dislikes])

    return video_list

def main():
    # Specify the path to the JSON file
    json_file_path = 'videos.json'

    # Read the JSON data from the file
    data = read_json_file(json_file_path)

    # Parse the videos and get the list
    video_list = parse_videos(data)

    # Print the list (optional)
    for video in video_list:
        print(video)

# Call the main function
if __name__ == '__main__':
    main()

import pandas
import seaborn

from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns

api_key = 'AIzaSyBbFjui_l3LQSYs-60so4VFZ2aryX-E7Jo'
#channel_id = ''
#channel ids can be aquired via the url in the channel of interest, or through third party websites like:
#https://www.streamweasels.com/tools/youtube-channel-id-and-user-id-convertor/
channel_ids = ['UCqnbDFdCpuN8CMEg0VuEBqA',
               'UCczAxLCL79gHXKYaEc9k-ZQ',
               'UCZaT_X_mc0BI-djXOlfhqWQ',

              ]

youtube = build('youtube', 'v3', developerKey=api_key)

"""## Get statistics on a single channel"""

def get_1channel_stats(youtube, channel_id):
  Request = youtube.channels().list(
      part = 'snippet,contentDetails,statistics',
      id = channel_id)
  response = Request.execute()

  return response

channel_id = 'UCczAxLCL79gHXKYaEc9k-ZQ'
get_1channel_stats(youtube, channel_id)

"""## Function to get multiple channels' statistics"""

def get_channel_stats(youtube, channel_ids):

  all_data = []

  request = youtube.channels().list(
      part = 'snippet,contentDetails,statistics',
      id = ','.join(channel_ids))
  response = request.execute()

  for i in range(len(response['items'])):

     data = dict(Channel_name = response['items'][i]['snippet']['title'],
               views = response['items'][i]['statistics']['viewCount'],
               subscribers = response['items'][i]['statistics']['subscriberCount'],
               total_videos = response['items'][i]['statistics']['videoCount'],
                 playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
     all_data.append(data)


  return all_data

channel_statistics = get_channel_stats(youtube, channel_ids)

channel_data = pd.DataFrame(channel_statistics)
channel_data

channel_data['subscribers'] = pd.to_numeric(channel_data['subscribers'])
channel_data['views'] = pd.to_numeric(channel_data['views'])
channel_data['total_videos'] = pd.to_numeric(channel_data['total_videos'])
channel_data.dtypes

sns.set(rc={'figure.figsize':(10,8)})
ax = sns.barplot(x='Channel_name', y='total_videos', data=channel_data)

"""## Get the videos in a channel and their stats"""

#access the playlist id for the particular channel
playlist_id = channel_data.loc[channel_data['Channel_name'] == 'IMPERIAL', 'playlist_id'].iloc[0]
playlist_id

#Fetch all the video ids for a particular channel
def get_video_ids(youtube, playlist_id):
  request = youtube.playlistItems().list(
      part = 'contentDetails',
      playlistId = playlist_id,
      maxResults = 50)
  response = request.execute()

  video_ids = []  #list to store video ids

  for i in range(len(response['items'])):
    video_ids.append(response['items'][i]['contentDetails']['videoId'])

  #need to paginate if there are more than 50 videos, this loop will make sure we get them all
  next_page_token = response.get('nextPageToken')
  more_pages = True

  while more_pages:
    if next_page_token is None:
      more_pages = False
    else:
        request = youtube.playlistItems().list(
            part = 'contentDetails',
            playlistId = playlist_id,
            maxResults = 50,
            pageToken = next_page_token)
        response = request.execute()

        for i in range(len(response['items'])):
            video_ids.append(response['items'][i]['contentDetails']['videoId'])
        next_page_token = response.get('nextPageToken')
  return video_ids

#put all the video ids in a list
video_ids = get_video_ids(youtube, playlist_id)
video_ids

"""## Function to get video details"""

def get_video_details(youtube, video_ids):

  all_video_stats = []

  #limit of 50 videos per request via Youtube API
  for i in range(0, len(video_ids), 50):
    request = youtube.videos().list(
        part = 'snippet,statistics',
        id = ','.join(video_ids[i:i+50]))
    response = request.execute()

    #for each 50 videos, get all their info
    for video in response['items']:
      video_stats = dict(Title = video['snippet']['title'],
                        Published_date = video['snippet']['publishedAt'],
                        Views = video['statistics']['viewCount'],
                        Likes = video['statistics']['likeCount'],
                        Comments = video['statistics']['commentCount']
      )
      all_video_stats.append(video_stats)

  return all_video_stats

#put the details in a list
video_details = get_video_details(youtube, video_ids)

video_data = pd.DataFrame(video_details)

#make sure the numerical values are ints
video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Comments'] = pd.to_numeric(video_data['Comments'])
video_data.dtypes

top10_videos = video_data.sort_values(by='Views', ascending=False).head(10)
top10_videos

ax1 = sns.barplot(x='Views', y='Title', data=top10_videos)

#sort data by most recent uploads
video_data['Month'] = pd.to_datetime(video_data['Published_date']).dt.strftime('%b')
video_data

videos_per_month = video_data.groupby('Month', as_index=False).size()
videos_per_month

sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
videos_per_month.index = pd.CategoricalIndex(videos_per_month['Month'], categories=sort_order, ordered=True)
videos_per_month = videos_per_month.sort_index()

ax2 = sns.barplot(x='Month', y='size', data=videos_per_month)
