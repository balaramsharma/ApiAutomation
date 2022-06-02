import os.path
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import base64
import email

SCOPES = ['https://mail.google.com/']
CLIENT_FILE = "credential/secret.json"
TOKEN_FILE = "credential/token.json"
SENDER = "nobody@amazon.com"
# SUBJECT_LIST = ["Your Amazon Business account will be closed in 48 hours",
#                 "Your Amazon Business account has been closed"]
SUBJECT_LIST = ["Your Amazon Business account will be closed in 48 hours"]
BASE_URL = "https://amazon.com"
ENDPOINT = f"{BASE_URL}/buy_account/add-account-group"


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
                                                  q="is:unread AND from:{} AND subject:\"{}\"".format(sender_email,
                                                                                                      email_subject)).execute()

        messages = results.get('messages', [])
        if not messages:
            print("No message found.")
            return

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = msg['payload']['headers']
            from_email = [mail for mail in email_data if mail.get('name') == 'From'][0]['value']
            subject_txt = [mail for mail in email_data if mail.get('name') == 'Subject'][0]['value']
            to_email = [mail for mail in email_data if mail.get('name') == 'To'][0]['value']

            print("========================")
            print("Found unread email from: " + from_email + "with subject: " + subject_txt)
            print("========================Mail Header===========")
            print(email_data)
            print("========================Mail Content==========")
            # if update_amazon_buy_account():
            #     print("Marking email to read")
            #     service.users().messages().modify(userId='me', id=message['id'], body={
            #         'removeLabelIds': ['UNREAD']}).execute()

            msg_1 = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
            msg_str = base64.urlsafe_b64decode(msg_1['raw'].encode('ASCII'))
            mime_msg = email.message_from_bytes(msg_str)
            print(mime_msg)

            print("========================")
            break

    except HttpError as error:
        print(f'An error occurred: {error}')


def update_amazon_buy_account():
    print("Forwarding mail to an endpoint")
    token = "<>"
    headers = {
        'Authorization': f'Token {token}'
    }
    data = {
        "email": "paul.abc@gmail.com",
        "account_groups": "Parent Business Removed",
        "parent": True
    }
    try:
        response = requests.post(ENDPOINT, data=data, headers=headers)
        if response.status_code == 200:
            response_text = response.text
            # response_json = response.json()
            print(response_text)
            print("Data posted to the server successfully")
            return True
        else:
            print("The response status is: ", response.status_code)

    except Exception as e:
        print(f"Error occurred while updating endpoint:{e}")
    return False


if __name__ == '__main__':
    creds = get_credentials()
    my_gmail_service = build('gmail', 'v1', credentials=creds)
    # my_gmail_service = build('gmail', 'v1', developerKey=API_KEY)
    print(my_gmail_service)
    for subject in SUBJECT_LIST:
        check_email_and_perform_action(my_gmail_service, SENDER, subject)
