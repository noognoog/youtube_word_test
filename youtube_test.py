from googleapiclient.discovery import build
import pandas as pd 
import streamlit as st 
from wordcloud import WordCloud
from PIL import Image
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.font_manager as fm 
from datetime import datetime, timedelta

font_path = 'C:/Users/noognoog/NanumGothic.ttf'
font_prop = fm.FontProperties(fname=font_path)

# Create a function to get the video tags and generate a word cloud
def get_video_tags_wordcloud(query, upload_date):
    API_KEY = 'AIzaSyDC_GEk_5U5inzMS2ZkZfP0RS8nDZwdKv4'  # Replace with your API key
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Set the upload date filter
    date_filter = (datetime.strptime(upload_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    search_response = youtube.search().list(q=query, type='video', part='id', maxResults=200, publishedAfter=date_filter).execute()
    video_ids = [item['id']['videoId'] for item in search_response['items']]

    videos = []
    for video_id in video_ids:
        video_response = youtube.videos().list(id=video_id, part='snippet,statistics').execute()
        if not video_response['items'][0]['snippet'].get('tags'):
            continue
        try:
            video = {
                'id': video_id,
                'view_count': int(video_response['items'][0]['statistics']['viewCount']),
                'like_count': int(video_response['items'][0]['statistics']['likeCount']),
                'tags': video_response['items'][0]['snippet'].get('tags', [])
            }
        except KeyError:
            continue
        videos.append(video)

    df = pd.DataFrame(videos)

    df_tags_concat = pd.DataFrame()
    for i in range(len(df)):
        try:
            words = df['tags'][i]
            count = Counter(words)
            for k in count.keys():
                count[k] = count[k] * (10*int(df['like_count'][i])+int(df['view_count'][i]))   
            df_tags_new = pd.DataFrame.from_dict(count, orient='index').reset_index()   
            df_tags_concat=pd.concat([df_tags_concat,df_tags_new])
        except Exception as e:
            continue

    df_tags_concat.reset_index(drop=True)
    df_tags_concat.columns=['keyword','count']
    df_tags_concat_grouped = df_tags_concat.groupby('keyword').sum().sort_values(by='count', ascending=False)
    df_fnl = df_tags_concat_grouped.reset_index()

    wc=df_fnl.set_index('keyword').to_dict()['count']
    wordCloud=WordCloud(font_path=font_path, width=400, height=400, max_font_size=100, background_color='white').generate_from_frequencies(wc)
    st.image(wordCloud.to_array(), use_column_width=True)

# Create the streamlit app
st.title("Video Tags Word Cloud")
query = st.text_input("Enter your query:")
upload_date = st.text_input("Enter the upload date (YYYY-MM-DD):")
if query and upload_date:
    get_video_tags_wordcloud(query, upload_date)