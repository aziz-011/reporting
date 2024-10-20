import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Function to authenticate and send an email
def send_email(subject, body, recipient):
    creds = None

    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials available, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEText(body)
        message['to'] = recipient
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        service.users().messages().send(userId='me', body={'raw': raw}).execute()
        st.success(f"Email notification sent to {recipient}.")
    except Exception as error:
        # Print the exact error and more context
        st.error(f'An error occurred while sending the email: {error}')
        print(f'Error details: {error}')
