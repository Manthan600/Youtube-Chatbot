import pandas as pd
import os
import re
from googleapiclient.discovery import build
import google.generativeai as genai
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv('YOUTUBE_API_KEY')
# CHANNEL_ID ="UC00ifCvU8YOOzbL3RdiSTDw"
CHANNEL_ID= "UCX6OQ3DkcsbYNE6H8uQQuVA"

def get_recent_videos_categories(channel_id, api_key, max_results=100):
    
    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        
        uploads_playlist = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Retrieve the most recent videos from the uploads playlist
        playlist_items = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist,
            maxResults=max_results
        ).execute()

        categories_count = {}
        total_videos = len(playlist_items['items'])

        for item in playlist_items['items']:
            video_id = item['snippet']['resourceId']['videoId']

            # Retrieve video details including its category
            video_details = youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()

            if video_details['items']:
                category_id = video_details['items'][0]['snippet']['categoryId']

                # Retrieve category information
                category_info = youtube.videoCategories().list(
                    part='snippet',
                    id=category_id
                ).execute()

                if category_info['items']:
                    category_title = category_info['items'][0]['snippet']['title']
                    category_id = category_info['items'][0]['id']
                    categories_count[category_id] = category_title

        return categories_count

    except Exception as e:
        return f"Error: {str(e)}"

# Function to parse video duration
def parse_duration(duration_str):
    # Parse the duration string and convert it to seconds
    hours = 0
    minutes = 0
    seconds = 0

    # Parse hours
    hours_match = re.search(r'(\d+)H', duration_str)
    if hours_match:
        hours = int(hours_match.group(1))

    # Parse minutes
    minutes_match = re.search(r'(\d+)M', duration_str)
    if minutes_match:
        minutes = int(minutes_match.group(1))

    # Parse seconds
    seconds_match = re.search(r'(\d+)S', duration_str)
    if seconds_match:
        seconds = int(seconds_match.group(1))

    # Convert to total seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

# Function to check if a video is short
def is_short_video(duration):
    
    return duration <= 60  # Duration is in seconds

# Function to search recent videos in a category
def search_recent_videos_in_category(category_id, api_key, max_results=10):
    
    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        #
        one_month_ago = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%dT%H:%M:%SZ')

        regular_search_response = youtube.search().list(
            q="",
            part="snippet",
            type="video",
            videoCategoryId=category_id,
            maxResults=max_results,  
            regionCode="IN",  
            order="viewCount",     
            publishedAfter=one_month_ago,  
            relevanceLanguage="en",  
            videoEmbeddable="true",  
            safeSearch="strict",      
            videoDuration="medium"   
        ).execute()

        
        regular_count = 0

        video_descriptions = []

        video_titles = []

        for item in regular_search_response['items']:
            
            video_id = item['id']['videoId']
            video_details = youtube.videos().list(part="snippet,statistics", id=video_id).execute()

            
            is_short = False

            title = item['snippet']['title']
            published_date = item['snippet']['publishedAt']
            view_count = video_details['items'][0]['statistics']['viewCount']
            description = video_details['items'][0]['snippet']['description']
            # print(f"Regular Video Title: {title}")
            # print(f"Published Date: {published_date}")
            # print(f"View Count: {view_count}")
            # print(f"Description: {description}")
            # print()
            regular_count += 1

            # Add description to the list
            video_descriptions.append(description)
            video_titles.append(title)

            if regular_count == max_results:
                break


        shorts_search_response = youtube.search().list(
            q="",
            part="snippet",
            type="video",
            videoCategoryId=category_id,
            maxResults=max_results,  
            regionCode="IN",  
            order="viewCount",     
            publishedAfter=one_month_ago,  
            relevanceLanguage="en",  
            videoEmbeddable="true",  
            safeSearch="strict",      
            videoDuration="short"    
        ).execute()

        # Initialize counters for shorts
        shorts_count = 0

        # Print titles, published date, view count, description, and video type of the recent shorts
        for item in shorts_search_response['items']:
            # Get video details including description
            video_id = item['id']['videoId']
            video_details = youtube.videos().list(part="snippet,statistics", id=video_id).execute()

            # Determine if the video is a short
            is_short = True

            # Print short video information
            title = item['snippet']['title']
            published_date = item['snippet']['publishedAt']
            view_count = video_details['items'][0]['statistics']['viewCount']
            description = video_details['items'][0]['snippet']['description']
            # print(f"Short Title: {title}")
            # print(f"Published Date: {published_date}")
            # print(f"View Count: {view_count}")
            # print(f"Description: {description}")
            # print()
            shorts_count += 1

            #video_descriptions.append(description)
            #video_titles.append(title)

            if shorts_count == max_results:
                break

        return video_descriptions, video_titles

    except Exception as e:
        print(f"Error: {str(e)}")



def pass_to_gemini_api(video_descriptions, video_titles):
    genai.configure(api_key= os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    ans = ""
    for title, description in zip(video_titles, video_descriptions):
        print()
        print()
        print(f"Title: {title}")
        # print(f"Description: {description}")
        response = model.generate_content(f"Strictly respond in simple text,  suggest youtube video title for my channel from title and description below, dont make it look like input title, try to figure out what video it is about and suggest title: {title}  {description}")
        ans  = ans + response.text + " <br>"
        print()
    return ans


def getSuggestions(channel_id):
    categories = get_recent_videos_categories(channel_id, API_KEY, max_results=100)
    s = ""
    for category_id, category_title in categories.items():
        print(f"Category Title: {category_title}, Category ID: {category_id}")
        video_descriptions, video_titles = search_recent_videos_in_category(category_id, API_KEY)
        s = s + " " +  pass_to_gemini_api(video_descriptions, video_titles) + "<br>"
    return s
