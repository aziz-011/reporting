import streamlit as st
import pandas as pd
import os
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


# Function to authenticate and send an email
def send_email(subject, body, recipient):
    creds = None

    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials available, login
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
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEText(body)
        message['to'] = recipient
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        service.users().messages().send(userId="me", body={'raw': raw}).execute()
        st.success(f"Email notification sent to {recipient}.")
    except Exception as error:
        st.error(f'Error occurred: {error}')


# Example call in your app:
def notify_machine_done(machine_name):
    subject = f"Machine {machine_name} Analysis Completed"
    body = f"The analysis for machine {machine_name} has been completed."
    recipient = "recipient@example.com"  # Adjust recipient email here
    send_email(subject, body, recipient)


# Rest of your Streamlit app (simplified example):
df = pd.DataFrame(columns=["Machine Name", "Date Added", "Date Completed", "Analysis Completed"])

# Admin Panel
machine_name = st.text_input("Enter Machine Number:")

if st.button("Add Machine"):
    df = df.append({"Machine Name": f"ID{machine_name}", "Date Added": datetime.now()}, ignore_index=True)
    st.success(f"Machine ID{machine_name} added.")

# Mark machine as done and send notification
if st.button(f"Mark {machine_name} as Done"):
    df.loc[df["Machine Name"] == f"ID{machine_name}", "Date Completed"] = datetime.now()
    st.success(f"Analysis for {machine_name} marked as done.")
    notify_machine_done(f"ID{machine_name}")
