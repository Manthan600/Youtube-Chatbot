import os
import requests
import logging
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=API_KEY)

def search_videos(keyword):
    try:
        search_response = youtube.search().list(
            q=keyword,
            type='video',
            part='id',
            maxResults=5
        ).execute()

        video_ids = [item['id']['videoId'] for item in search_response['items']]
        return video_ids
    except HttpError as e:
        logging.error(f'YouTube API Error: {e}')
        return []

def suggest_keywords_and_hashtags(user_input_keyword):
    try:
        video_ids = search_videos(user_input_keyword)

        if not video_ids:
            return []

        tags = []
        for video_id in video_ids:
            url = f'https://www.youtube.com/watch?v={video_id}'
            video_tags = videotags(url)
            if video_tags:
                tags.extend(video_tags.split(', '))

        generated_keywords = list(set(tags))[:20]

        ranked_keywords = rank_keywords_by_average_views(generated_keywords)

        return ranked_keywords[:10]

    except Exception as e:
        logging.error(e)
        return []

def videotags(url):
    try:
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')
        tags = ', '.join([meta.attrs.get("content") for meta in soup.find_all(
            "meta", {"property": "og:video:tag"})])
        return tags
    except Exception as e:
        logging.error(e)
        return False

def rank_keywords_by_average_views(keywords):
    ranked_keywords = []
    for keyword in keywords:
        video_ids = search_videos(keyword)

        if video_ids:
            average_views = calculate_average_views(video_ids[:7])
            ranked_keywords.append((keyword, average_views))

    ranked_keywords.sort(key=lambda x: x[1], reverse=True)

    return ranked_keywords

def calculate_average_views(video_ids):
    total_views = 0
    for video_id in video_ids:
        video_info = youtube.videos().list(part='statistics', id=video_id).execute()
        if 'items' in video_info and video_info['items']:
            total_views += int(video_info['items'][0]['statistics']['viewCount'])

    return total_views // len(video_ids) if len(video_ids) > 0 else 0

# user_input_keyword = input('Enter a keyword: ')
def getHashtags(user_input_keyword):
    result = suggest_keywords_and_hashtags(user_input_keyword)

    if result:
        return result
    else:
        return 'Error occurred during keyword and hashtag suggestion.'
