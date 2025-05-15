import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import csv

# --- Configuration ---
# Data API v3 settings
api_key_file = 'D:\\Documents\\_Data-Vault\\Code\\Private\\Keys\\Google-APIv3_key-1.py'
YOUTUBE_DATA_API_KEY = None
try:
    with open(api_key_file, 'r') as f:
        line = f.readline().strip()
        if line.startswith('YOUTUBE_DATA_API_KEY ='):
            YOUTUBE_DATA_API_KEY = line.split('=')[1].strip().strip("'")
except FileNotFoundError:
    print(f"Error: API key file not found at {api_key_file}")
    exit()

API_KEY = YOUTUBE_DATA_API_KEY
channel_id = 'UC0Zoz9yO4DbkaRf6cZ9iPTw'

# Analytics API v2 settings
SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']
CREDENTIALS_FILE = 'D:\\Documents\\_Data-Vault\\Code\\Private\\Keys\\Credencials-oAuth-googleusercontent.json'  # Update if your file is elsewhere
TOKEN_FILE = 'token.json'
OUTPUT_CSV_FILE = 'D:\\Documents\\_Data-Vault\\YouTube-Stats\\pcSHOWme-Insights.csv'


def get_authenticated_analytics_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('youtubeAnalytics', 'v2', credentials=creds)


def get_youtube_data_service():
    return build("youtube", "v3", developerKey=API_KEY)


def get_channel_overview(youtube_data, channel_id):
    request = youtube_data.channels().list(
        part="snippet,statistics,brandingSettings",
        id=channel_id
    )
    response = request.execute()
    if response and 'items' in response:
        item = response['items'][0]
        return {
            'title': item['snippet']['title'],
            'description': item['snippet'].get('description', 'N/A'),
            'published_date': item['snippet'].get('publishedAt', 'N/A'),
            'subscriber_count': item['statistics'].get('subscriberCount', 'N/A'),
            'total_views': item['statistics'].get('viewCount', 'N/A'),
            'total_videos': item['statistics'].get('videoCount', 'N/A'),
            'keywords': ', '.join(item.get('brandingSettings', {}).get('channel', {}).get('keywords', [])) or 'N/A'
        }
    return {}


def get_recent_performance(youtube_analytics):
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=28)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    request = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,watchTime,averageViewDuration,subscribersGained,likes,comments,shares'
    )
    response = request.execute()
    if response and 'rows' in response:
        return {
            'recent_views': response['rows'][0][0],
            'recent_watch_time': round(response['rows'][0][1] / 60, 2),  # in minutes
            'recent_avg_view_duration': round(response['rows'][0][2], 2),  # in seconds
            'recent_subscribers_gained': response['rows'][0][3],
            'recent_likes': response['rows'][0][4],
            'recent_comments': response['rows'][0][5],
            'recent_shares': response['rows'][0][6]
        }
    return {}


def get_top_videos(youtube_analytics):
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=28)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    request = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views',
        dimensions='video',
        sort='-views',
        maxResults=5
    )
    response = request.execute()
    top_videos = {}
    if response and 'rows' in response:
        video_ids = [row[0] for row in response['rows']]
        video_details_request = get_youtube_data_service().videos().list(  # Corrected this line
            part='snippet',
            id=','.join(video_ids)
        )
        video_details_response = video_details_request.execute()
        if video_details_response and 'items' in video_details_response:
            for item in video_details_response['items']:
                video_id = item['id']
                title = item['snippet']['title'].replace(",", " ")
                views = [row[1] for row in response['rows'] if row[0] == video_id][0]
                top_videos[title] = views
    return top_videos


if __name__ == '__main__':
    youtube_analytics = get_authenticated_analytics_service()
    youtube_data = get_youtube_data_service()

    channel_data = get_channel_overview(youtube_data, channel_id)
    recent_performance = get_recent_performance(youtube_analytics)
    top_videos = get_top_videos(youtube_analytics)

    timestamp = datetime.datetime.now().isoformat()

    # Write to CSV
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Timestamp', 'Channel Title', 'Description', 'Published Date', 'Subscriber Count', 'Total Views',
                      'Total Videos', 'Channel Keywords',
                      'Recent Views (28 Days)', 'Recent Watch Time (Minutes)', 'Recent Avg View Duration (Seconds)',
                      'Recent Subscribers Gained', 'Recent Likes', 'Recent Comments', 'Recent Shares',
                      'Top Video 1 Title', 'Top Video 1 Views',
                      'Top Video 2 Title', 'Top Video 2 Views',
                      'Top Video 3 Title', 'Top Video 3 Views',
                      'Top Video 4 Title', 'Top Video 4 Views',
                      'Top Video 5 Title', 'Top Video 5 Views']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({
            'Timestamp': timestamp,
            'Channel Title': channel_data.get('title', 'N/A').replace(",", " "),
            'Description': channel_data.get('description', 'N/A').replace(",", " "),
            'Published Date': channel_data.get('published_date', 'N/A'),
            'Subscriber Count': channel_data.get('subscriber_count', 'N/A'),
            'Total Views': channel_data.get('total_views', 'N/A'),
            'Total Videos': channel_data.get('total_videos', 'N/A'),
            'Channel Keywords': channel_data.get('keywords', 'N/A'),
            'Recent Views (28 Days)': recent_performance.get('recent_views', 'N/A'),
            'Recent Watch Time (Minutes)': recent_performance.get('recent_watch_time', 'N/A'),
            'Recent Avg View Duration (Seconds)': recent_performance.get('recent_avg_view_duration', 'N/A'),
            'Recent Subscribers Gained': recent_performance.get('recent_subscribers_gained', 'N/A'),
            'Recent Likes': recent_performance.get('recent_likes', 'N/A'),
            'Recent Comments': recent_performance.get('recent_comments', 'N/A'),
            'Recent Shares': recent_performance.get('recent_shares', 'N/A'),
            'Top Video 1 Title': list(top_videos.keys())[0] if top_videos else 'N/A',
            'Top Video 1 Views': list(top_videos.values())[0] if top_videos else 'N/A',
            'Top Video 2 Title': list(top_videos.keys())[1] if len(top_videos) > 1 else 'N/A',
            'Top Video 2 Views': list(top_videos.values())[1] if len(top_videos) > 1 else 'N/A',
            'Top Video 3 Title': list(top_videos.keys())[2] if len(top_videos) > 2 else 'N/A',
            'Top Video 3 Views': list(top_videos.values())[2] if len(top_videos) > 2 else 'N/A\',
            'Top Video 4 Title': list(top_videos.keys())[3] if len(top_videos) > 3 else 'N/A',
            'Top Video 4 Views': list(top_videos.values())[3] if len(top_videos) > 3 else 'N/A',
            'Top Video 5 Title': list(top_videos.keys())[4] if len(top_videos) > 4 else 'N/A',
            'Top Video 5 Views': list(top_videos.values())[4] if len(top_videos) > 4 else 'N/A',
        })
    print(f"Data successfully written to {OUTPUT_CSV_FILE}")
    exit()
