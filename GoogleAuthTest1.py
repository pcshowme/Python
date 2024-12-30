from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes you need
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    # OAuth Flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', SCOPES
    )
    credentials = flow.run_console()

    # Build YouTube API service
    youtube = build('youtube', 'v3', credentials=credentials)

    # Make a sample API call
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        mine=True
    )
    response = request.execute()

    # Print the response
    print("API Response:")
    print(response)

if __name__ == "__main__":
    main()
