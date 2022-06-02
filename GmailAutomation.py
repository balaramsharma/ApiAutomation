import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from logger import logger

SCOPES = ['https://mail.google.com/']
CLIENT_FILE = 'credential/secret.json'
TOKEN_FILE = 'credential/token.json'
SENDER = 'nobody@amazon.com'
# SUBJECT_LIST = ["Your Amazon Business account will be closed in 48 hours",
#                 "Your Amazon Business account has been closed"]
SUBJECT_LIST = ["Your Amazon Business account will be closed in 48 hours", "Your Amazon Business account has been closed"]


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds


def check_email_and_perform_action(service, sender_email, email_subject):
    try:
        print("Searching emails from sender: {} having subject:{}".format(sender_email, email_subject))
        # This will search unread messages in the INBOX applying From and Subject filters.
        # results = service.users().messages().list(userId='me', labelIds=['INBOX'],
        #                                           q="is:unread AND from:{} AND subject:\"{}\"".format(sender_email,
        #                                                                                               email_subject)).execute()
        results = service.users().messages().list(userId='me',
                                                  q="from:{} AND subject:\"{}\"".format(sender_email,
                                                                                                      email_subject)).execute()
        messages = results.get('messages', [])
        if not messages:
            logger.info("No message found.")
            return

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = msg['payload']['headers']
            from_email = [mail for mail in email_data if mail.get('name') == 'From'][0]['value']
            subject_txt = [mail for mail in email_data if mail.get('name') == 'Subject'][0]['value']
            to_email = [mail for mail in email_data if mail.get('name') == 'To'][0]['value']
            print(f"Found unread email from:{from_email}, sent to:{to_email}, subject:{subject_txt}")

    except HttpError as error:
        logger.info(f"An error occurred: {error}")


def make_database_connection():
    print("")


if __name__ == '__main__':
    creds = get_credentials()
    my_gmail_service = build('gmail', 'v1', credentials=creds)
    for subject in SUBJECT_LIST:
        check_email_and_perform_action(my_gmail_service, SENDER, subject)
