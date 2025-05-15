import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# --- Configuration ---
SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']
CREDENTIALS_FILE = 'D:\Documents\_Data-Vault\Code\Private\Keys\Credencials-oAuth-googleusercontent.json'  # Make sure this matches your downloaded file name

def get_authenticated_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('youtubeAnalytics', 'v2', credentials=creds)

def get_top_geographies(youtube_analytics):
    request = youtube_analytics.reports().query(
        ids='channel==MINE',  # Use 'channel==YOUR_CHANNEL_ID' if needed
        startDate='28daysAgo',
        endDate='today',
        metrics='views',
        dimensions='country',
        sort='-views',
        maxResults=10  # Adjust as needed
    )
    response = request.execute()
    print("--- Top Geographies by Views (Last 28 Days) ---")
    if 'rows' in response:
        print("Country\t\tViews")
        for row in response['rows']:
            print(f"{row[0]}\t\t{row[1]}")
    else:
        print("No data found.")

if __name__ == '__main__':
    youtube_analytics = get_authenticated_service()
    get_top_geographies(youtube_analytics)