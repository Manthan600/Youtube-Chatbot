import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import matplotlib.pyplot as plt


load_dotenv()


api_key = os.getenv("YOUTUBE_API_KEY")

def is_short(item):
    
    duration = get_video_details(item["id"]["videoId"])["contentDetails"]["duration"]
    return "PT" in duration and duration.count("M") == 1 and duration[-1] == "S"

def get_youtube_data( channel_id):
    
    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        
        videos_response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",
            type="video",
            maxResults=10
        ).execute()

        
        recent_videos = [item for item in videos_response["items"] if not is_short(item)]
        recent_videos = recent_videos[:5]

        
        shorts_response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",
            type="video",
            maxResults=10
        ).execute()

        
        recent_shorts = [item for item in shorts_response["items"] if is_short(item)]
        recent_shorts = recent_shorts[:5]

        print_videos(recent_videos, "Videos")
        print_videos(recent_shorts, "Shorts")

        
        plot_bar_graphs(recent_videos, recent_shorts, "Likes Counts for Recent Videos", "Likes Counts for Recent Shorts","./static")

    except HttpError as e:
        print(f"An error occurred: {e}")
        return 'Channel id is incorrect'

def print_videos(response, video_type):
    print(f"Recent {video_type}:")
    for idx, item in enumerate(response, start=1):
        video_title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]

        # Get video details including like count
        video_details = get_video_details(video_id)
        like_count = video_details["statistics"]["likeCount"]
        comment_count = video_details["statistics"]["commentCount"]
        duration = get_duration_seconds(video_details["contentDetails"]["duration"])

        print(f"{video_type} {idx}:")
        print(f"Title: {video_title}")
        print(f"Video ID: {video_id}")
        print(f"Like Count: {like_count}")
        print(f"Comment Count: {comment_count}")
        print(f"Duration: {duration}\n")

def get_video_details(video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    video_response = youtube.videos().list(
        part="statistics,contentDetails",
        id=video_id
    ).execute()

    return video_response["items"][0]

# def plot_bar_graphs(video_items, short_items, video_title, short_title, save_path=None):
#     fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(15, 15))

#     # Extract data for each metric for videos
#     video_metrics = ["Like Count", "Comment Count", "Duration"]
#     video_data = [[int(get_video_details(item["id"]["videoId"])["statistics"]["likeCount"]) for item in video_items],
#                   [int(get_video_details(item["id"]["videoId"])["statistics"]["commentCount"]) for item in video_items],
#                   [get_duration_seconds(get_video_details(item["id"]["videoId"])["contentDetails"]["duration"]) for item in video_items]]

#     # Extract data for each metric for shorts
#     short_metrics = ["Like Count", "Comment Count", "Duration"]
#     short_data = [[int(get_video_details(item["id"]["videoId"])["statistics"]["likeCount"]) for item in short_items],
#                   [int(get_video_details(item["id"]["videoId"])["statistics"]["commentCount"]) for item in short_items],
#                   [get_duration_seconds(get_video_details(item["id"]["videoId"])["contentDetails"]["duration"]) for item in short_items]]

#     for i in range(3):
#         # Plot bar graph for videos
#         axs[i, 0].bar([f"{item['snippet']['title']}" for item in video_items], video_data[i], color='skyblue', alpha=0.7)
#         axs[i, 0].set_ylabel(video_metrics[i])
#         axs[i, 0].set_title(video_title)

#         # Plot bar graph for shorts
#         axs[i, 1].bar([f"{item['snippet']['title']}" for item in short_items], short_data[i], color='orange', alpha=0.7)
#         axs[i, 1].set_ylabel(short_metrics[i])
#         axs[i, 1].set_title(short_title)

#     plt.tight_layout()
    
#     if save_path is not None:
#         plt.savefig(save_path)  # Save the plot if save_path is provided
    
#     # plt.show()

def plot_bar_graphs(video_items, short_items, video_title, short_title, save_path=None):
    # Extract data for each metric for videos
    video_metrics = ["Like Count", "Comment Count", "Duration"]
    video_data = [[int(get_video_details(item["id"]["videoId"])["statistics"]["likeCount"]) for item in video_items],
                  [int(get_video_details(item["id"]["videoId"])["statistics"]["commentCount"]) for item in video_items],
                  [get_duration_seconds(get_video_details(item["id"]["videoId"])["contentDetails"]["duration"]) for item in video_items]]

    # Extract data for each metric for shorts
    short_metrics = ["Like Count", "Comment Count", "Duration"]
    short_data = [[int(get_video_details(item["id"]["videoId"])["statistics"]["likeCount"]) for item in short_items],
                  [int(get_video_details(item["id"]["videoId"])["statistics"]["commentCount"]) for item in short_items],
                  [get_duration_seconds(get_video_details(item["id"]["videoId"])["contentDetails"]["duration"]) for item in short_items]]

    for i in range(3):
        fig, ax = plt.subplots(figsize=(7, 4))

        # Plot bar graph for videos
        ax.bar([f"{item['snippet']['title']}" for item in video_items], video_data[i], color='skyblue', alpha=0.7)
        ax.set_ylabel(video_metrics[i])
        ax.set_title(video_title)
        ax.tick_params(axis='x', rotation=45)  

        if save_path is not None:
            plt.savefig(f"{save_path}/video_{video_metrics[i].replace(' ', '_').lower()}.png")
        
        plt.close(fig)  

        fig, ax = plt.subplots(figsize=(7, 4))

        # Plot bar graph for shorts
        ax.bar([f"{item['snippet']['title']}" for item in short_items], short_data[i], color='orange', alpha=0.7)
        ax.set_ylabel(short_metrics[i])
        ax.set_title(short_title)
        ax.tick_params(axis='x', rotation=45)  

        if save_path is not None:
            plt.savefig(f"{save_path}/short_{short_metrics[i].replace(' ', '_').lower()}.png")
        
        plt.close(fig)  



def get_duration_seconds(duration):
    
    split_duration = duration.split('T')

    minutes = 0
    seconds = 0

    if len(split_duration) == 2:
        # Extract minutes
        if 'M' in split_duration[1]:
            minutes = int(split_duration[1].split('M')[0])

        # Extract seconds
        if 'S' in split_duration[1]:
            seconds_str = split_duration[1].split('S')[0]
            seconds = int(seconds_str) if seconds_str.isdigit() else 0

    return minutes * 60 + seconds

# get_youtube_data("UCX6OQ3DkcsbYNE6H8uQQuVA")