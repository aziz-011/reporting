import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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
        st.error(f'An error occurred: {error}')


# Example usage: sending an email when a machine is completed
def notify_machine_done(machine_name):
    subject = f"Machine {machine_name} Analysis Completed"
    body = f"The analysis for machine {machine_name} has been completed."
    recipient = "recipient@example.com"  # Adjust to your recipient
    send_email(subject, body, recipient)


# Function to get the current week number and year
def get_current_week_and_year():
    today = datetime.now()
    return today.isocalendar()[1], today.year  # (week_number, year)


# Initialize the CSV file for the current week
def initialize_csv():
    week, year = get_current_week_and_year()
    csv_filename = f"week_{week}_{year}.csv"

    # Create CSV if it doesn't exist
    if not os.path.exists(csv_filename):
        df = pd.DataFrame(columns=["Machine Name", "Date Added", "Date Completed", "Analysis Completed"])
        df.to_csv(csv_filename, index=False)
    else:
        df = pd.read_csv(csv_filename)
    return df, csv_filename


# Load machine data for the current week and ensure column types
df, current_csv_filename = initialize_csv()


# Admin login check
def admin_login():
    username = st.sidebar.text_input("Admin Username")
    password = st.sidebar.text_input("Admin Password", type="password")
    if username == "admin" and password == "adminpassword":
        return True
    return False


# Function to add a new machine with the suffix "ID" and clear the input field
def add_machine(machine_number):
    machine_name = f"ID{machine_number}"  # Automatically append "ID"
    date_added = datetime.now().strftime("%Y-%m-%d")
    new_row = pd.DataFrame({
        "Machine Name": [machine_name],
        "Date Added": [date_added],
        "Date Completed": [None],
        "Analysis Completed": [False]
    })
    return pd.concat([df, new_row], ignore_index=True)


# Function to mark machine as done and update the date of completion
def mark_machine_as_done(df, machine_name):
    date_completed = datetime.now().strftime("%Y-%m-%d")
    df.loc[df["Machine Name"] == machine_name, "Date Completed"] = date_completed
    df.loc[df["Machine Name"] == machine_name, "Analysis Completed"] = True
    return df


# Main application starts here
st.title("Machine Analysis Tracking")

# Initialize session state for machine number input
if 'machine_number' not in st.session_state:
    st.session_state['machine_number'] = ''

# Admin Panel
if admin_login():
    st.sidebar.write("Admin Panel")

    # Add a new machine with the suffix "ID"
    machine_number = st.sidebar.text_input("Enter Machine Number:", value=st.session_state['machine_number'],
                                           key="machine_input")

    if st.sidebar.button("Add Machine"):
        df = add_machine(machine_number)
        df.to_csv(current_csv_filename, index=False)
        st.sidebar.success(f"Machine ID{machine_number} added on {datetime.now().strftime('%Y-%m-%d')}.")

        # Reset the input field after adding a machine
        st.session_state['machine_number'] = ''  # Clear the input field

    # Display all machines for admin
    st.write("All Machines (including completed ones):")
    st.write(df)

# Standard User View
else:
    st.sidebar.write("Standard User Panel")

    # Filter machines to show only incomplete ones
    visible_df = df[df["Analysis Completed"] == False]

    # Select machine and mark analysis as done
    if not visible_df.empty:
        machine = st.selectbox("Select a machine", visible_df["Machine Name"])
        if st.button(f"Mark {machine} as Done"):
            df = mark_machine_as_done(df, machine)
            df.to_csv(current_csv_filename, index=False)
            st.success(f"Analysis for {machine} marked as completed on {datetime.now().strftime('%Y-%m-%d')}.")
            notify_machine_done(machine)  # Send email notification
    else:
        st.write("No pending machines for analysis.")
