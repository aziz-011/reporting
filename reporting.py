import streamlit as st
import pandas as pd
import os
from datetime import datetime


# Function to get the current week number and year
def get_current_week_and_year():
    today = datetime.now()
    return today.isocalendar()[1], today.year  # (week_number, year)


# Initialize the DataFrame and load from CSV if available
def initialize_csv():
    week, year = get_current_week_and_year()
    csv_filename = f"week_{week}_{year}.csv"

    # Load from CSV if it exists
    if os.path.exists(csv_filename):
        df = pd.read_csv(csv_filename)
    else:
        df = pd.DataFrame(columns=["Machine Name", "Date Added", "Date Completed", "Analysis Completed"])

    return df, csv_filename


# Save DataFrame to CSV to persist data
def save_to_csv(df, csv_filename):
    df.to_csv(csv_filename, index=False)


# Function to convert dataframe to CSV for download
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


# Load machine data for the current week from the CSV
df, csv_filename = initialize_csv()


# Admin login check
def admin_login():
    username = st.sidebar.text_input("Admin Username")
    password = st.sidebar.text_input("Admin Password", type="password")
    if username == "admin" and password == "adminpassword":
        return True
    return False


# Function to add a new machine with the suffix "ID"
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
def mark_machine_as_done(machine_name):
    date_completed = datetime.now().strftime("%Y-%m-%d")
    df.loc[df["Machine Name"] == machine_name, "Date Completed"] = date_completed
    df.loc[df["Machine Name"] == machine_name, "Analysis Completed"] = True


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
        save_to_csv(df, csv_filename)  # Save the updated DataFrame to CSV
        st.sidebar.success(f"Machine ID{machine_number} added on {datetime.now().strftime('%Y-%m-%d')}.")

        # Reset the input field after adding a machine
        st.session_state['machine_number'] = ''  # Clear the input field

    # Display all machines for admin
    st.write("All Machines (including completed ones):")
    st.write(df)

    # Provide download link for CSV
    csv_data = convert_df_to_csv(df)
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=csv_filename,
        mime='text/csv',
    )

# Standard User View
else:
    st.sidebar.write("Standard User Panel")

    # Filter machines to show only incomplete ones
    visible_df = df[df["Analysis Completed"] == False]

    # Select machine and mark analysis as done
    if not visible_df.empty:
        machine = st.selectbox("Select a machine", visible_df["Machine Name"])
        if st.button(f"Mark {machine} as Done"):
            mark_machine_as_done(machine)
            save_to_csv(df, csv_filename)  # Save the updated DataFrame to CSV
            st.success(f"Analysis for {machine} marked as completed on {datetime.now().strftime('%Y-%m-%d')}.")
    else:
        st.write("No pending machines for analysis.")

    # View machines that are pending analysis
    st.write("Machines pending analysis:")
    st.write(visible_df)
