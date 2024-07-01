from flask import Flask, render_template, request, jsonify


# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch
import spacy
# from fuzzywuzzy import process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from final_hashtags import getHashtags
from youtube_content_suggestion import getSuggestions
from channel_statistics_final import get_youtube_data
from youtube_comment_analyzer import YTcommentAnalylise

nlp = spacy.load("en_core_web_sm")
exit_flag = False

channel_id_flag = False
video_description_flag = False
current_intent = ""

data = {
    'hi': {'intent': 'Greeting', 'channel_id': None},
    'hello': {'intent': 'Greeting', 'channel_id': None},
    'hey': {'intent': 'Greeting', 'channel_id': None},
    'hi there': {'intent': 'Greeting', 'channel_id': None},
    'hello there': {'intent': 'Greeting', 'channel_id': None},
    'hi, how are you doing?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how are you?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how are you?': {'intent': 'Greeting', 'channel_id': None},
    'hi everyone': {'intent': 'Greeting', 'channel_id': None},
    'good morning': {'intent': 'Greeting', 'channel_id': None},
    'good afternoon': {'intent': 'Greeting', 'channel_id': None},
    'good evening': {'intent': 'Greeting', 'channel_id': None},
    'hey folks': {'intent': 'Greeting', 'channel_id': None},
    'what\'s up?': {'intent': 'Greeting', 'channel_id': None},
    'howdy': {'intent': 'Greeting', 'channel_id': None},
    'nice to meet you': {'intent': 'Greeting', 'channel_id': None},
    'hey there, how\'s it going?': {'intent': 'Greeting', 'channel_id': None},
    'hi, it\'s great to see you': {'intent': 'Greeting', 'channel_id': None},
    'how are you?': {'intent': 'Greeting', 'channel_id': None},
    'hi, nice to see you': {'intent': 'Greeting', 'channel_id': None},
    'hello, what\'s up?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s everything?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how have you been?': {'intent': 'Greeting', 'channel_id': None},
    'how have you been lately?': {'intent': 'Greeting', 'channel_id': None},
    'hey, what\'s happening?': {'intent': 'Greeting', 'channel_id': None},
    'hi, it\'s been a while': {'intent': 'Greeting', 'channel_id': None},
    'hello, long time no see': {'intent': 'Greeting', 'channel_id': None},
    'hey, what\'s new?': {'intent': 'Greeting', 'channel_id': None},
    'hi, good to see you again': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your day?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything going?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how have you been lately?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your week been?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how are things with you?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s life treating you?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your day going so far?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how are things in your world?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s your day been?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your week going so far?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your day been going?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how are you today?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s it been lately?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s everything with you?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how are things going on your end?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how have you been doing?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your day going today?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s your week been so far?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s everything been with you lately?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s it been going for you?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything on your side?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your day shaping up?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s everything been going lately?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything been on your end?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how have you been today?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your day treating you?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s your week been going?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s everything been going for you?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s everything been for you lately?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s it been going on your side?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your day been treating you so far?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s everything been going on your side?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s it been going for you lately?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s everything been going on your end?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your day been treating you today?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything been on your side lately?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s it been going on your end lately?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s everything been on your end lately?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything been on your side today?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your day been going for you so far?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s everything been on your side so far today?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s your week been going so far?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s everything been going for you today?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s everything been on your end today?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s your day been treating you lately?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s everything been on your side so far?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your week been treating you so far?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s your week been going today?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s everything been on your end today?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your day treating you so far today?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything been going for you so far today?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your week been going for you so far?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your day been treating you lately?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything been on your side lately?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your week been treating you lately?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s everything been going for you lately?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything been on your end lately?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your day been going for you lately?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s everything been on your side lately?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s your week been treating you lately?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your day been treating you so far lately?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s everything been going for you so far lately?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything been on your end so far lately?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your week been going for you so far lately?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your day been treating you lately?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything been on your side so far lately?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your week been treating you so far lately?': {'intent': 'Greeting', 'channel_id': None},
    'hi, how\'s your day been going for you so far today?': {'intent': 'Greeting', 'channel_id': None},
    'hello, how\'s everything been going for you so far today?': {'intent': 'Greeting', 'channel_id': None},
    'hey, how\'s your week been going for you so far today?': {'intent': 'Greeting', 'channel_id': None},

    'bye': {'intent': 'Exit', 'channel_id': None},
    'exit': {'intent': 'Exit', 'channel_id': None},
    'goodbye': {'intent': 'Exit', 'channel_id': None},
    'see you later': {'intent': 'Exit', 'channel_id': None},
    'farewell': {'intent': 'Exit', 'channel_id': None},
    'take care': {'intent': 'Exit', 'channel_id': None},
    'bye, see you soon': {'intent': 'Exit', 'channel_id': None},
    'goodbye, have a nice day': {'intent': 'Exit', 'channel_id': None},
    'see you later, alligator': {'intent': 'Exit', 'channel_id': None},
    'farewell, until we meet again': {'intent': 'Exit', 'channel_id': None},
    'take care, stay safe': {'intent': 'Exit', 'channel_id': None},
    'goodbye, see you tomorrow': {'intent': 'Exit', 'channel_id': None},
    'bye, take it easy': {'intent': 'Exit', 'channel_id': None},
    'see you later, have a good one': {'intent': 'Exit', 'channel_id': None},
    'farewell, see you around': {'intent': 'Exit', 'channel_id': None},
    'exit, bye for now': {'intent': 'Exit', 'channel_id': None},
    'goodbye, have a great day': {'intent': 'Exit', 'channel_id': None},
    'farewell, take care': {'intent': 'Exit', 'channel_id': None},
    'see you later, until next time': {'intent': 'Exit', 'channel_id': None},
    'bye, have a good day': {'intent': 'Exit', 'channel_id': None},
    'exit, take care': {'intent': 'Exit', 'channel_id': None},
    'goodbye, see you soon': {'intent': 'Exit', 'channel_id': None},
    'see you later, goodbye': {'intent': 'Exit', 'channel_id': None},
    'farewell, goodbye': {'intent': 'Exit', 'channel_id': None},
    'take care, goodbye': {'intent': 'Exit', 'channel_id': None},
    'bye for now, take care': {'intent': 'Exit', 'channel_id': None},
    'goodbye, farewell': {'intent': 'Exit', 'channel_id': None},
    'see you later, take care': {'intent': 'Exit', 'channel_id': None},
    'farewell, until next time': {'intent': 'Exit', 'channel_id': None},
    'take care, see you soon': {'intent': 'Exit', 'channel_id': None},
    'bye, until next time': {'intent': 'Exit', 'channel_id': None},
    'exit, goodbye': {'intent': 'Exit', 'channel_id': None},
    'goodbye, take care': {'intent': 'Exit', 'channel_id': None},
    'see you later, farewell': {'intent': 'Exit', 'channel_id': None},
    'farewell, see you later': {'intent': 'Exit', 'channel_id': None},
    'take care, farewell': {'intent': 'Exit', 'channel_id': None},
    'bye, take care of yourself': {'intent': 'Exit', 'channel_id': None},
    'exit, see you later': {'intent': 'Exit', 'channel_id': None},
    'goodbye, until next time': {'intent': 'Exit', 'channel_id': None},
    'see you later, take it easy': {'intent': 'Exit', 'channel_id': None},
    'farewell, goodbye for now': {'intent': 'Exit', 'channel_id': None},
    'take care, until we meet again': {'intent': 'Exit', 'channel_id': None},
    'bye, goodbye': {'intent': 'Exit', 'channel_id': None},
    'exit, farewell': {'intent': 'Exit', 'channel_id': None},
    'goodbye, see you later': {'intent': 'Exit', 'channel_id': None},
    'see you later, until next time': {'intent': 'Exit', 'channel_id': None},
    'farewell, take care of yourself': {'intent': 'Exit', 'channel_id': None},
    'take care, goodbye for now': {'intent': 'Exit', 'channel_id': None},
    'bye, farewell': {'intent': 'Exit', 'channel_id': None},
    'exit, take it easy': {'intent': 'Exit', 'channel_id': None},
    'goodbye, see you soon': {'intent': 'Exit', 'channel_id': None},
    'see you later, take care of yourself': {'intent': 'Exit', 'channel_id': None},
    'farewell, until next time': {'intent': 'Exit', 'channel_id': None},
    'take care, until next time': {'intent': 'Exit', 'channel_id': None},
    'bye, take care of yourself': {'intent': 'Exit', 'channel_id': None},
    'exit, until next time': {'intent': 'Exit', 'channel_id': None},
    'goodbye, take care of yourself': {'intent': 'Exit', 'channel_id': None},
    'see you later, goodbye for now': {'intent': 'Exit', 'channel_id': None},
    'farewell, see you soon': {'intent': 'Exit', 'channel_id': None},
    'take care, goodbye, have a great day': {'intent': 'Exit', 'channel_id': None},
    'bye, take care, see you soon': {'intent': 'Exit', 'channel_id': None},
    'exit, goodbye, take care': {'intent': 'Exit', 'channel_id': None},
    'goodbye, see you later, take care': {'intent': 'Exit', 'channel_id': None},
    'see you later, farewell, until next time': {'intent': 'Exit', 'channel_id': None},
    'farewell, take care, see you soon': {'intent': 'Exit', 'channel_id': None},
    'take care, farewell, until we meet again': {'intent': 'Exit', 'channel_id': None},
    'bye, goodbye, take care': {'intent': 'Exit', 'channel_id': None},
    'exit, farewell, until next time': {'intent': 'Exit', 'channel_id': None},
    'goodbye, see you later, take care of yourself': {'intent': 'Exit', 'channel_id': None},
    'see you later, take care, goodbye for now': {'intent': 'Exit', 'channel_id': None},
    'farewell, see you soon, take care': {'intent': 'Exit', 'channel_id': None},
    'take care, until next time, goodbye': {'intent': 'Exit', 'channel_id': None},
    'bye, take care, farewell': {'intent': 'Exit', 'channel_id': None},
    'exit, goodbye, have a nice day': {'intent': 'Exit', 'channel_id': None},
    'goodbye, see you later, until next time': {'intent': 'Exit', 'channel_id': None},
    'see you later, farewell, take care of yourself': {'intent': 'Exit', 'channel_id': None},
    'farewell, take care, until we meet again': {'intent': 'Exit', 'channel_id': None},
    'take care, see you soon, goodbye': {'intent': 'Exit', 'channel_id': None},
    'bye, goodbye, have a nice day': {'intent': 'Exit', 'channel_id': None},
    'exit, farewell, take care': {'intent': 'Exit', 'channel_id': None},
    'goodbye, see you later, until next time': {'intent': 'Exit', 'channel_id': None},
    'see you later, take care, have a great day': {'intent': 'Exit', 'channel_id': None},
    'farewell, take care, see you later': {'intent': 'Exit', 'channel_id': None},
    'take care, until next time, goodbye for now': {'intent': 'Exit', 'channel_id': None},
    'bye, take care, see you soon, farewell': {'intent': 'Exit', 'channel_id': None},
    'exit, goodbye, until next time, take care': {'intent': 'Exit', 'channel_id': None},
    'goodbye, see you later, take care, farewell': {'intent': 'Exit', 'channel_id': None},
    'see you later, farewell, until next time, take care': {'intent': 'Exit', 'channel_id': None},
    'farewell, take care, see you soon, goodbye': {'intent': 'Exit', 'channel_id': None},
    'take care, until next time, goodbye, have a nice day': {'intent': 'Exit', 'channel_id': None},
    'bye, take care, farewell, see you soon': {'intent': 'Exit', 'channel_id': None},
    'exit, goodbye, take care, until next time': {'intent': 'Exit', 'channel_id': None},
    'goodbye, see you later, until next time, take care': {'intent': 'Exit', 'channel_id': None},
    'see you later, take care, goodbye for now, farewell': {'intent': 'Exit', 'channel_id': None},
    'farewell, take care, until we meet again, goodbye': {'intent': 'Exit', 'channel_id': None},
    'take care, see you soon, goodbye, have a nice day': {'intent': 'Exit', 'channel_id': None},

    'Give appropriate hashtags for the video description': {'intent': 'Hashtag', 'channel_id': None},
    'Could you suggest relevant hashtags for this video?': {'intent': 'Hashtag', 'channel_id': None},
    'What hashtags should I use for my video description?': {'intent': 'Hashtag', 'channel_id': None},
    'How can I improve my video description with hashtags?': {'intent': 'Hashtag', 'channel_id': None},
    'Suggest some tags for my YouTube video.': {'intent': 'Hashtag', 'channel_id': None},
    'Provide hashtags based on the video content.': {'intent': 'Hashtag', 'channel_id': None},
    'Can you suggest some tags for my YouTube video?': {'intent': 'Hashtag', 'channel_id': None},
    'What are the best hashtags for YouTube video SEO?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I optimize my video description with hashtags?': {'intent': 'Hashtag', 'channel_id': None},
    'Give me relevant tags for my video.': {'intent': 'Hashtag', 'channel_id': None},
    'Suggest hashtags for my video.': {'intent': 'Hashtag', 'channel_id': None},
    'Could you provide some hashtags for my video description?': {'intent': 'Hashtag', 'channel_id': None},
    'What tags would you recommend for my video?': {'intent': 'Hashtag', 'channel_id': None},
    'How should I tag my video for better visibility?': {'intent': 'Hashtag', 'channel_id': None},
    'Give me some hashtags to improve my video reach.': {'intent': 'Hashtag', 'channel_id': None},
    'Can you suggest hashtags based on my video topic?': {'intent': 'Hashtag', 'channel_id': None},
    'Provide me with some hashtags for my video.': {'intent': 'Hashtag', 'channel_id': None},
    'I need hashtags to boost my video engagement.': {'intent': 'Hashtag', 'channel_id': None},
    'What hashtags can I use to increase my video views?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I choose the right hashtags for my video?': {'intent': 'Hashtag', 'channel_id': None},
    'Give me some tags to optimize my video description.': {'intent': 'Hashtag', 'channel_id': None},
    'Could you suggest some hashtags to grow my video channel?': {'intent': 'Hashtag', 'channel_id': None},
    'What hashtags are trending for my video niche?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I use hashtags effectively in my video description?': {'intent': 'Hashtag', 'channel_id': None},
    'Provide me with tags to enhance my video visibility.': {'intent': 'Hashtag', 'channel_id': None},
    'I need hashtags to improve my video ranking.': {'intent': 'Hashtag', 'channel_id': None},
    'What are the most popular hashtags for YouTube videos?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I make my video more discoverable with hashtags?': {'intent': 'Hashtag', 'channel_id': None},
    'Suggest hashtags for my video to reach a wider audience.': {'intent': 'Hashtag', 'channel_id': None},
    'Could you provide some relevant tags for my video?': {'intent': 'Hashtag', 'channel_id': None},
    'What hashtags can I use to increase engagement on my videos?': {'intent': 'Hashtag', 'channel_id': None},
    'Give me some tags to improve my video\'s searchability.': {'intent': 'Hashtag', 'channel_id': None},
    'How do I select hashtags that match my video content?': {'intent': 'Hashtag', 'channel_id': None},
    'Provide me with some trending hashtags for my video.': {'intent': 'Hashtag', 'channel_id': None},
    'I need hashtags to attract more viewers to my video.': {'intent': 'Hashtag', 'channel_id': None},
    'What tags will help my video get discovered on YouTube?': {'intent': 'Hashtag', 'channel_id': None},
    'How can I optimize my video tags for better search results?': {'intent': 'Hashtag', 'channel_id': None},
    'Suggest hashtags to increase the visibility of my video.': {'intent': 'Hashtag', 'channel_id': None},
    'Could you recommend some relevant hashtags for my video?': {'intent': 'Hashtag', 'channel_id': None},
    'What are the most effective hashtags for YouTube video promotion?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I find the right hashtags for my video content?': {'intent': 'Hashtag', 'channel_id': None},
    'Provide me with popular hashtags for my video niche.': {'intent': 'Hashtag', 'channel_id': None},
    'I need tags to optimize my video\'s discoverability.': {'intent': 'Hashtag', 'channel_id': None},
    'What hashtags should I avoid using in my video description?': {'intent': 'Hashtag', 'channel_id': None},
    'Suggest some trending hashtags for my video.': {'intent': 'Hashtag', 'channel_id': None},
    'Could you give me some suggestions for relevant hashtags?': {'intent': 'Hashtag', 'channel_id': None},
    'What are the key hashtags I should include in my video description?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I make my video stand out with unique hashtags?': {'intent': 'Hashtag', 'channel_id': None},
    'Provide me with some specific hashtags for my video content.': {'intent': 'Hashtag', 'channel_id': None},
    'I need hashtags to target a specific audience for my video.': {'intent': 'Hashtag', 'channel_id': None},
    'What tags will help my video rank higher in YouTube search results?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I use hashtags strategically to promote my video?': {'intent': 'Hashtag', 'channel_id': None},
    'Suggest hashtags that align with my video\'s theme.': {'intent': 'Hashtag', 'channel_id': None},
    'Could you recommend some niche-specific hashtags for my video?': {'intent': 'Hashtag', 'channel_id': None},
    'What hashtags can I use to target my video towards a specific audience?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I ensure my video gets discovered with the right hashtags?': {'intent': 'Hashtag', 'channel_id': None},
    'Provide me with some evergreen hashtags for my video.': {'intent': 'Hashtag', 'channel_id': None},
    'I need hashtags to boost my video\'s visibility on YouTube.': {'intent': 'Hashtag', 'channel_id': None},
    'What tags will help my video gain traction on social media?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I find trending hashtags relevant to my video content?': {'intent': 'Hashtag', 'channel_id': None},
    'Suggest some location-specific hashtags for my video.': {'intent': 'Hashtag', 'channel_id': None},
    'Could you suggest hashtags to increase engagement on my video?': {'intent': 'Hashtag', 'channel_id': None},
    'What are the most popular hashtags in my video\'s niche?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I create custom hashtags for my video marketing campaign?': {'intent': 'Hashtag', 'channel_id': None},
    'Provide me with some general hashtags for my video.': {'intent': 'Hashtag', 'channel_id': None},
    'I need tags to improve the discoverability of my video.': {'intent': 'Hashtag', 'channel_id': None},
    'What hashtags are commonly used in my video\'s category?': {'intent': 'Hashtag', 'channel_id': None},
    'How do I leverage trending hashtags to promote my video?': {'intent': 'Hashtag', 'channel_id': None},



    'Give me analytics for my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you provide analytics for my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the analytics for my YouTube channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'I need insights into my YouTube channel performance.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How are my videos performing on YouTube?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the statistics for my channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the key metrics for my YouTube channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Provide me with analytics for my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Can you give me an overview of my channel analytics?': {'intent': 'Analytics', 'channel_id': 'required'},
    'I want to see my channel\'s performance data.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the engagement metrics of my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you provide me with a breakdown of my channel analytics?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the top-performing videos on my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the audience demographics for my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How is my channel growing over time?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the retention rates of my YouTube videos.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you analyze the traffic sources for my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the most popular search terms leading to my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the revenue generated by my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How is my channel performing compared to competitors in my niche?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the engagement levels of my YouTube audience.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you provide me with the watch time distribution on my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the most common viewer interactions on my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the playback locations of my YouTube videos.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How is my channel\'s performance trending over time?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the audience engagement trends on my channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you provide me with a breakdown of traffic demographics for my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the key performance indicators for my YouTube channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the ad performance metrics for my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How is my channel\'s subscriber growth over time?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the viewer engagement patterns on my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you analyze the audience retention data for my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the demographics of my YouTube channel audience?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the click-through rates for my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How is my channel\'s performance compared to industry benchmarks?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the video content that resonates most with my audience.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you provide me with the average view duration for my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the top countries by viewer count on my YouTube channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the engagement trends for my YouTube channel over the past year.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How is my channel\'s subscriber retention rate evolving?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the audience engagement metrics of my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you provide me with the viewer distribution by age and gender for my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the top videos driving traffic to my YouTube channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the average watch time for my YouTube videos.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How is my channel\'s performance affected by seasonal trends?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the viewer engagement metrics for my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you provide me with the performance breakdown by device for my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the top engagement metrics for my YouTube channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the traffic sources for my YouTube videos.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How is my channel\'s performance trending in terms of likes and dislikes?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the audience retention patterns on my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you analyze the performance of my channel\'s playlists?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the key engagement metrics I should focus on for my YouTube channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the geographic distribution of my YouTube channel audience.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How is my channel\'s performance impacted by changes in content format?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the audience retention trends on my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you provide me with the traffic breakdown by platform for my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the top engagement metrics driving viewer engagement on my channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the revenue trends for my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'How is my channel\'s performance trending in terms of comments and shares?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Give me insights into the audience behavior patterns on my YouTube channel.': {'intent': 'Analytics', 'channel_id': 'required'},
    'Could you analyze the performance of my channel\'s featured videos?': {'intent': 'Analytics', 'channel_id': 'required'},
    'What are the key engagement metrics I should track for my YouTube channel?': {'intent': 'Analytics', 'channel_id': 'required'},
    'Show me the traffic sources driving views to my YouTube videos.': {'intent': 'Analytics', 'channel_id': 'required'},
    
    'Can you suggest trending video topics for my YouTube channel?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me ideas for new videos that are trending in my niche.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some popular video topics I should cover on my channel?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with trending video ideas for my next YouTube upload.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I need suggestions for creating engaging content that resonates with my audience.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you recommend video topics that are currently popular on YouTube?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some video ideas to boost engagement on my channel.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What topics are trending on YouTube that align with my channel\'s content?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for viral video topics in my niche.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I\'m looking for trending video topics to increase my channel\'s visibility.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you suggest video ideas that are likely to attract a larger audience?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some inspiration for my next YouTube video by suggesting trending topics.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some hot topics in my industry that I can create videos about?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video topics that are currently trending on social media.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I need fresh video ideas to keep my channel interesting and relevant.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you recommend trending video topics that are likely to go viral?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some video topic suggestions based on current trends in my niche.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What types of videos are getting the most views on YouTube right now?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with ideas for video content that will attract new subscribers.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I\'m looking for video topic suggestions that will help me grow my channel.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you suggest video ideas that will keep my audience engaged and interested?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some trending video topics that I can create content around.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are the top video trends in my industry that I should be aware of?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video topics that will set my channel apart from the competition.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I need help brainstorming video ideas that will resonate with my target audience.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you recommend video topics that are likely to generate high engagement?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some fresh video ideas that I can use to diversify my content.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some trending video topics that haven\'t been covered much in my niche?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video topics that will help me establish authority in my field.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I\'m looking for video ideas that will help me attract sponsorships and brand deals.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you suggest video topics that will encourage audience interaction and participation?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some creative video ideas that will showcase my channel\'s unique personality.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some trending video topics that are generating buzz in my industry?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video content that aligns with current cultural trends.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I need video topic suggestions that will help me build a strong online community.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you recommend video ideas that will help me increase watch time and retention?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some video topic suggestions that will appeal to a broad audience.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some evergreen video topics that will remain relevant over time?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video content that addresses current industry challenges or trends.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I\'m looking for video ideas that will help me establish my channel as a thought leader.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you suggest video topics that will help me build credibility and authority in my niche?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some trending video ideas that will attract attention from my target audience.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What types of videos are generating the most engagement on social media platforms?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video content that addresses common questions or concerns in my industry.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I need video topic suggestions that will help me establish trust with my audience.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you recommend video ideas that will help me monetize my channel effectively?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some video topic suggestions that will help me build a loyal fanbase.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some emerging video trends that I should incorporate into my content strategy?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video content that will appeal to different segments of my audience.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I\'m looking for video ideas that will help me generate leads and drive conversions.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you suggest video topics that will help me stay ahead of my competitors?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some trending video ideas that will help me expand my reach.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What types of videos are most likely to be shared and recommended by viewers?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video content that will keep my audience coming back for more.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I need video topic suggestions that will help me build a strong brand identity.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you recommend video ideas that will help me establish a deeper connection with my audience?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some video topic suggestions that will help me create viral content.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some niche-specific video topics that have the potential to go viral?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video content that will help me achieve my channel goals.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I\'m looking for video ideas that will help me attract high-quality subscribers.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you suggest video topics that will help me build a community around my channel?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some video topic suggestions that will help me increase engagement.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some popular video formats that I can use to diversify my content?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video content that will help me achieve my channel growth targets.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I need video topic suggestions that will help me attract sponsorships and brand collaborations.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you recommend video ideas that will help me optimize my channel for search and discovery?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some video topic suggestions that will help me stand out in my niche.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some video topics that are likely to generate discussion and debate among viewers?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video content that will help me capitalize on current trends.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I\'m looking for video ideas that will help me build authority and credibility in my field.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you suggest video topics that will help me establish myself as an expert in my niche?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some video topic suggestions that will help me generate revenue.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some trending video topics that will resonate with my target audience?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video content that will help me create a strong brand image.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I need video topic suggestions that will help me build trust and loyalty with my viewers.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Can you recommend video ideas that will help me maximize engagement and retention?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Give me some video topic suggestions that will help me grow my subscriber base.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'What are some trending video topics that are likely to attract advertisers and sponsors?': {'intent': 'Suggestions', 'channel_id': 'required'},
    'Provide me with suggestions for video content that will help me achieve my long-term channel goals.': {'intent': 'Suggestions', 'channel_id': 'required'},
    'I\'m looking for video ideas that will help me build a strong online presence.': {'intent': 'Suggestions', 'channel_id': 'required'},

    'Analyse the comments on my YouTube channel.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Could you provide insights on the comments section of my channel?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What is the sentiment analysis of the comments on my videos?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Analyze the engagement level of comments on my YouTube channel.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with a breakdown of the types of comments on my channel.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'How are my viewers interacting in the comments section of my videos?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'I need insights into the sentiment of comments left on my YouTube videos.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What are the most common topics discussed in the comments on my channel?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Give me an analysis of the language used in the comments section of my videos.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Can you provide me with demographics of the users commenting on my videos?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'I want to understand the sentiment and tone of the comments on my channel.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with insights into the engagement metrics of comments on my channel.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What is the overall sentiment of the comments on my recent videos?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Give me a summary of the comments section activity on my YouTube channel.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with an analysis of the positive and negative feedback in the comments.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What are the trends in the comments section of my channel over time?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Can you analyze the sentiment of comments related to specific topics on my channel?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Give me an overview of the user engagement levels in the comments on my videos.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with a sentiment analysis report for the comments on my channel.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What are the most frequent words used in the comments section of my videos?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Can you identify any patterns or trends in the comments on my YouTube channel?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Give me insights into the sentiment of comments from different regions or countries.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with feedback analysis for the comments on my recent uploads.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What is the tone of the comments left by my subscribers versus non-subscribers?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Can you categorize the comments based on their emotional tone (positive, negative, neutral)?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Give me insights into the sentiment of comments on my channel related to specific video topics.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with a breakdown of the sentiment analysis for comments on my most popular videos.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What are the most engaging types of comments on my channel (e.g., questions, compliments, critiques)?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Can you identify any spam or irrelevant comments in the comment section of my videos?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Give me an analysis of the sentiment trends in the comments over the past month.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with insights into the sentiment shifts in the comments over different time periods.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What are the sentiment patterns in the comments section during specific events or promotions?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Can you analyze the sentiment of comments related to specific keywords or hashtags?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Give me an overview of the interaction levels between viewers and creators in the comments.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with insights into the sentiment of comments left by viewers who watched the entire video versus those who didn\'t.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What are the common sentiments expressed by viewers in the comments section of my videos?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Can you identify any trends in the comments that correlate with changes in viewer demographics?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Give me insights into the sentiment of comments on videos featuring different types of content (e.g., tutorials, vlogs, reviews).': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with a breakdown of the sentiment analysis for comments left during live streams versus regular video uploads.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What are the sentiments expressed by viewers in response to specific calls-to-action in the videos?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Can you identify any trends in the comments section that align with changes in video production quality or style?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Give me insights into the sentiment of comments left by viewers who are subscribed versus non-subscribed to my channel.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with a breakdown of the sentiment analysis for comments on videos with different engagement levels (e.g., high views, low views).': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What are the sentiments expressed in response to specific topics or controversies discussed in my videos?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Can you analyze the sentiment of comments in different languages on my multilingual channel?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Give me insights into the sentiment of comments left by viewers who have been subscribed for varying durations.': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Provide me with a breakdown of the sentiment analysis for comments on videos of different lengths (short vs. long).': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'What are the sentiments expressed in response to different types of content updates or announcements on my channel?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    'Can you identify any trends in the comments section that correlate with changes in the frequency of uploads on my channel?': {'intent': 'commentAnalyze', 'channel_id': 'required'},
    
}

X = list(data.keys())
y = [data[x]['intent'] for x in data]
# print(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X_train, y_train)


y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)


train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_test_pred)


print("Training Accuracy:", train_accuracy)
print("Testing Accuracy:", test_accuracy)

def lemmatize(video_description):
    doc = nlp(video_description)
    lemmatized_words = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    ans = ['#' + word.lower() for word in lemmatized_words]
    return ans

def handle_user_input(user_input):

    intent = model.predict([user_input])
    print(intent)
    intent = model.predict([user_input])[0]
    global current_intent
    current_intent = intent
    channel_id = None
    
    if (intent == 'Analytics' or intent == 'Suggestions' or intent == 'commentAnalyze'):
        global channel_id_flag
        channel_id_flag = True
        return "Please provide the channel ID: "
    


    return handle_query(intent, channel_id)

def handle_query(intent, channel_id=None):
    if intent == 'Greeting':
        return "Hello! How can I assist you today?"

    elif intent == 'Hashtag':
        global video_description_flag 
        video_description_flag = True
        return "Please provide the video description: "
        

    elif intent == 'Analytics':
        get_youtube_data(channel_id)
        ans = '''
            <img src="../static/short_comment_count.png">
            <img src="../static/short_duration.png">
            <img src="../static/short_like_count.png">
            <img src="../static/video_comment_count.png">
            <img src="../static/video_duration.png">
            <img src="../static/video_like_count.png">
            '''
        return ans
      

    elif intent == 'Suggestions':
        sugg = getSuggestions(channel_id)
        print(sugg)
        return sugg
        

    elif intent == 'commentAnalyze':
        YTcommentAnalylise(channel_id)
        return '<img src="../static/comment.png">'
        

    elif intent == 'Exit':
        global exit_flag
        exit_flag = True
        return "Goodbye! Have a great day!"


def handle_hashtags(video_desc):
    tags = lemmatize(video_desc)
    ans = ' '.join(tags)
    result = getHashtags(ans)
    
    s = ""
    for hash , views in result :
        s= s + "Hashtags " + hash + "Views "+ str(views) + "<br>" 
    
   
    print(result)
    print(s)
    return s


app = Flask(__name__)

@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print("in GET " + msg)
    global channel_id_flag
    global video_description_flag
    if (channel_id_flag):
        channel_id_flag = False
        return handle_query(current_intent,msg)
    elif (video_description_flag):
        video_description_flag = False
        return handle_hashtags(msg)

    s = handle_user_input(input)
    print(" response : " + str(s))
    return s


if __name__ == '__main__':
    app.run()
