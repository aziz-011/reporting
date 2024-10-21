import streamlit as st
import pandas as pd
import os
from datetime import datetime


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


# Function to filter incomplete machines and ensure done ones are only removed on Fridays
def filter_incomplete_machines(df):
    today = datetime.now()
    if today.weekday() == 4:  # 4 corresponds to Friday
        return df[df["Analysis Completed"] == False]
    else:
        return df


# Function to handle CSV rollover at the end of the week (on Friday)
def rollover_to_next_week():
    week, year = get_current_week_and_year()
    new_csv_filename = f"week_{week + 1}_{year}.csv"  # Create new CSV for the next week

    # If today is Friday, we update the CSV and prepare for the next week
    today = datetime.now()
    if today.weekday() == 4:  # 4 corresponds to Friday
        # Save completed machines in this week's CSV
        completed_df = df[df["Analysis Completed"] == True]
        completed_df.to_csv(f"completed_week_{week}_{year}.csv", index=False)

        # Carry over incomplete machines to next week
        incomplete_df = df[df["Analysis Completed"] == False]

        # Create a new CSV for next week and add incomplete machines
        if not incomplete_df.empty:
            incomplete_df.to_csv(new_csv_filename, index=False)
        st.success(f"Weekly rollover completed. Incomplete machines moved to {new_csv_filename}.")


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

    # Filter machines to show only incomplete ones and only remove completed ones on Friday
    visible_df = filter_incomplete_machines(df)

    # Select machine and mark analysis as done
    if not visible_df.empty:
        machine = st.selectbox("Select a machine", visible_df["Machine Name"])
        if st.button(f"Mark {machine} as Done"):
            df = mark_machine_as_done(df, machine)
            df.to_csv(current_csv_filename, index=False)
            st.success(f"Analysis for {machine} marked as completed on {datetime.now().strftime('%Y-%m-%d')}.")
    else:
        st.write("No pending machines for analysis.")

    # View machines that are pending analysis
    st.write("Machines pending analysis:")
    st.write(visible_df)

# Automatically handle weekly CSV rollover on Fridays
rollover_to_next_week()
