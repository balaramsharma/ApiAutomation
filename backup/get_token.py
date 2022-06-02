import os.path
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

SCOPES = ['https://mail.google.com/']
EMAIL = "catch@autods.com"

def get_credentials(client_file):
    creds = None
    if os.path.exists('credential/token.json'):
        creds = Credentials.from_authorized_user_file('credential/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('credential/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


if __name__ == '__main__':
    creds = get_credentials(sys.argv[1])
    my_gmail_service = build('gmail', 'v1', credentials=creds)
