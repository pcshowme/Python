import sys
sys.stdout.reconfigure(encoding='utf-8')

from googleapiclient.discovery import build
import os
import csv
import datetime

# --- Configuration ---
# https://console.cloud.google.com/apis/credentials?inv=1&invt=Ab1n2Q&project=nodal-vigil-446216-e0

api_key_file = 'D:\\Documents\\_Data-Vault\\Code\\Private\\Keys\\Google-APIv3_key-1.py'
API_KEY = None
try:
    with open(api_key_file, 'r') as f:
        line = f.readline().strip()
        if line.startswith('YOUTUBE_DATA_API_KEY ='):
            API_KEY = line.split('=')[1].strip().strip("'")
except FileNotFoundError:
    print(f"Error: API key file not found at {api_key_file}")
    exit()

if not API_KEY:
    print("Error: API key not found or invalid format in key file.")
    exit()

channel_id = 'UC0Zoz9yO4DbkaRf6cZ9iPTw'  # Your channel ID
max_results_per_page = 50  # Adjust as needed
num_latest_videos = 50      # Number of latest videos to fetch details for

# --- Initialize YouTube API ---
youtube = build("youtube", "v3", developerKey=API_KEY)

# --- Function to fetch all video IDs from a channel ---
def get_all_video_ids(youtube, channel_id, max_results=50):
    video_ids = []
    next_page_token = None
    while True:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=max_results,
            order="date",
            pageToken=next_page_token,
            type="video"  # Ensure we only get videos
        )
        response = request.execute()
        for item in response.get("items", []):
            video_ids.append(item["id"]["videoId"])
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return video_ids

# --- Fetch Channel Details ---
channel_request = youtube.channels().list(
    part="snippet,statistics,contentDetails,brandingSettings",
    id=channel_id
)
channel_response = channel_request.execute()
channel_data = channel_response["items"][0] if channel_response["items"] else None

# --- Fetch Video Details ---
latest_video_ids = get_all_video_ids(youtube, channel_id, max_results_per_page)[:num_latest_videos]
videos_data = []
if latest_video_ids:
    videos_request = youtube.videos().list(
        part="snippet,statistics,contentDetails,topicDetails,liveStreamingDetails,localizations",
        id=latest_video_ids
    )
    videos_response = videos_request.execute()
    videos_data = videos_response.get("items", [])

# --- Print Combined Data ---
if channel_data:
    snippet = channel_data["snippet"]
    statistics = channel_data["statistics"]
    branding = channel_data.get("brandingSettings", {}).get("channel", {})

    print("--- Channel Information ---")
    print(f"Channel Title: {snippet['title']}")
    print(f"Description: {snippet.get('description', 'N/A')}")
    print(f"Published At: {snippet.get('publishedAt', 'N/A')}")
    print(f"Subscribers: {statistics.get('subscriberCount', 'N/A')}")
    print(f"Total Views: {statistics.get('viewCount', 'N/A')}")
    print(f"Total Videos: {statistics.get('videoCount', 'N/A')}")
    print(f"Keywords: {', '.join(branding.get('keywords', [])) if branding.get('keywords') else 'N/A'}")
    # Add more channel details as needed

if videos_data:
    print("\n--- Latest Video Information ---")
    print("Title,Description,Published Date,Views,Likes,Comments,Duration,Tags,Category ID,Topic IDs,Local Title,Local Description")
    for video in videos_data:
        snippet = video["snippet"]
        statistics = video.get("statistics", {})
        content_details = video.get("contentDetails", {})
        topic_details = video.get("topicDetails", {})
        localizations = video.get("localizations", {})

        title = snippet["title"].replace(",", " ")
        description = snippet.get("description", " ").replace(",", " ")
        published_date = snippet["publishedAt"]
        view_count = statistics.get("viewCount", "N/A")
        like_count = statistics.get("likeCount", "N/A")
        comment_count = statistics.get("commentCount", "N/A")
        duration = content_details.get("duration", "N/A")
        tags = ", ".join(snippet.get("tags", [])) if snippet.get("tags") else "N/A"
        category_id = snippet.get("categoryId", "N/A")
        topic_ids = ", ".join(topic_details.get("topicIds", [])) if topic_details and topic_details.get("topicIds") else "N/A"
        local_title = localizations.get("en", {}).get("title", "N/A").replace(",", " ")
        local_description = localizations.get("en", {}).get("description", "N/A").replace(",", " ")

        print(f'"{title}","{description}","{published_date}",{view_count},{like_count},{comment_count},"{duration}","{tags}",{category_id},"{topic_ids}","{local_title}","{local_description}"')

# --- After collecting channel_data and videos_data ---

# Prepare CSV output path with today's date
csv_date = datetime.datetime.now().strftime('%Y%m%d')
csv_path = f'D:/Documents/_Data-Vault/YouTube-Stats/video-details_{csv_date}.csv'

with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    # Write channel info header
    writer.writerow(['Channel Title', 'Description', 'Published At', 'Subscribers', 'Total Views', 'Total Videos', 'Keywords'])
    if channel_data:
        snippet = channel_data["snippet"]
        statistics = channel_data["statistics"]
        branding = channel_data.get("brandingSettings", {}).get("channel", {})
        writer.writerow([
            snippet['title'],
            snippet.get('description', 'N/A'),
            snippet.get('publishedAt', 'N/A'),
            statistics.get('subscriberCount', 'N/A'),
            statistics.get('viewCount', 'N/A'),
            statistics.get('videoCount', 'N/A'),
            ', '.join(branding.get('keywords', [])) if branding.get('keywords') else 'N/A'
        ])
    # Write video info header
    writer.writerow([])
    writer.writerow(["Title", "Description", "Published Date", "Views", "Likes", "Comments", "Duration", "Tags", "Category ID", "Topic IDs", "Local Title", "Local Description"])
    if videos_data:
        for video in videos_data:
            snippet = video["snippet"]
            statistics = video.get("statistics", {})
            content_details = video.get("contentDetails", {})
            topic_details = video.get("topicDetails", {})
            localizations = video.get("localizations", {})
            title = snippet["title"].replace(",", " ")
            description = snippet.get("description", " ").replace(",", " ")
            published_date = snippet["publishedAt"]
            view_count = statistics.get("viewCount", "N/A")
            like_count = statistics.get("likeCount", "N/A")
            comment_count = statistics.get("commentCount", "N/A")
            duration = content_details.get("duration", "N/A")
            tags = ", ".join(snippet.get("tags", [])) if snippet.get("tags") else "N/A"
            category_id = snippet.get("categoryId", "N/A")
            topic_ids = ", ".join(topic_details.get("topicIds", [])) if topic_details and topic_details.get("topicIds") else "N/A"
            local_title = localizations.get("en", {}).get("title", "N/A").replace(",", " ")
            local_description = localizations.get("en", {}).get("description", "N/A").replace(",", " ")
            writer.writerow([
                title, description, published_date, view_count, like_count, comment_count, duration, tags, category_id, topic_ids, local_title, local_description
            ])

print(f"\nData retrieval complete! CSV written to {csv_path}")