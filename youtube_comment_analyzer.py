# Import necessary libraries
import os
from googleapiclient.discovery import build
import re
import emoji
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()


def fetch_recent_videos(channel_id):
    
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    
    video_response = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=5,
        order='date',
        type='video'
    ).execute()
    
    
    videos = [video['id']['videoId'] for video in video_response['items'] if 'short' not in video['snippet']['title'].lower()]
    
    return videos


def fetch_comments(video_id):
    
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    comments = []
    nextPageToken = None
    
    while len(comments) < 400:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            pageToken=nextPageToken
        )
        response = request.execute()
        
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append(comment['textDisplay'])
                
        nextPageToken = response.get('nextPageToken')
        
        if not nextPageToken:
            break
    
    return comments


def filter_comments(comments):
    relevant_comments = []
    
    hyperlink_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    
    threshold_ratio = 0.65
    
    for comment_text in comments:
        comment_text = comment_text.lower().strip()
        emojis = emoji.emoji_count(comment_text)
        text_characters = len(re.sub(r'\s', '', comment_text))
        
        if (any(char.isalnum() for char in comment_text)) and not hyperlink_pattern.search(comment_text):
            if emojis == 0 or (text_characters / (text_characters + emojis)) > threshold_ratio:
                relevant_comments.append(comment_text)
                
    return relevant_comments

# Function to analyze sentiment of comments
def analyze_sentiment(comments):
    analyzer = SentimentIntensityAnalyzer()
    polarity = []
    positive_comments = []
    negative_comments = []
    neutral_comments = []
    
    for comment in comments:
        sentiment_dict = analyzer.polarity_scores(comment)
        polarity.append(sentiment_dict['compound'])
        
        if sentiment_dict['compound'] > 0.05:
            positive_comments.append(comment)
        elif sentiment_dict['compound'] < -0.05:
            negative_comments.append(comment)
        else:
            neutral_comments.append(comment)
    
    return len(positive_comments), len(negative_comments), len(neutral_comments), polarity


def plot_sentiment_analysis(video_titles, positive_counts, negative_counts, neutral_counts):
    plt.figure(figsize=(7, 4))
    bar_width = 0.2
    index = range(len(video_titles))
    
    plt.bar(index, positive_counts, bar_width, label='Positive', color='blue')
    plt.bar([i + bar_width for i in index], negative_counts, bar_width, label='Negative', color='red')
    plt.bar([i + 2 * bar_width for i in index], neutral_counts, bar_width, label='Neutral', color='grey')
    
    plt.xlabel('Video')
    plt.ylabel('Comment Count')
    plt.title('Sentiment Analysis of Recent Videos')
    plt.xticks([i + bar_width for i in index], video_titles)
    plt.legend()
    plt.tight_layout()
    plt.savefig("./static/comment.png")


def YTcommentAnalylise(channel_id):
    
    # channel_id = 'UCX6OQ3DkcsbYNE6H8uQQuVA'
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    recent_videos = fetch_recent_videos(channel_id)
    
    
    video_titles = []
    positive_counts = []
    negative_counts = []
    neutral_counts = []
    
    for video_id in recent_videos:
        
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        video_titles.append(video_response['items'][0]['snippet']['title'])
        
        comments = fetch_comments(video_id)
        
       
        relevant_comments = filter_comments(comments)
        
       
        positive_count, negative_count, neutral_count, _ = analyze_sentiment(relevant_comments)
        positive_counts.append(positive_count)
        negative_counts.append(negative_count)
        neutral_counts.append(neutral_count)
    
    
    plot_sentiment_analysis(video_titles, positive_counts, negative_counts, neutral_counts)


