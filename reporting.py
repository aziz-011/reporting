import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Initialize SQLite connection
def init_db():
    conn = sqlite3.connect('machines.db')
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_name TEXT NOT NULL,
            date_added TEXT NOT NULL,
            date_completed TEXT,
            analysis_completed BOOLEAN NOT NULL
        )
    ''')
    conn.commit()
    return conn

# Function to add a new machine to the database
def add_machine_to_db(conn, machine_name):
    c = conn.cursor()
    date_added = datetime.now().strftime("%Y-%m-%d")
    c.execute('''
        INSERT INTO machines (machine_name, date_added, date_completed, analysis_completed)
        VALUES (?, ?, NULL, 0)
    ''', (machine_name, date_added))
    conn.commit()

# Function to mark a machine as done in the database
def mark_machine_as_done_in_db(conn, machine_name):
    c = conn.cursor()
    date_completed = datetime.now().strftime("%Y-%m-%d")
    c.execute('''
        UPDATE machines
        SET date_completed = ?, analysis_completed = 1
        WHERE machine_name = ?
    ''', (date_completed, machine_name))
    conn.commit()

# Function to get all machines from the database
def get_all_machines(conn):
    c = conn.cursor()
    c.execute('SELECT * FROM machines')
    rows = c.fetchall()
    columns = ['ID', 'Machine Name', 'Date Added', 'Date Completed', 'Analysis Completed']
    df = pd.DataFrame(rows, columns=columns)
    return df

# Function to get only the incomplete machines
def get_incomplete_machines(conn):
    c = conn.cursor()
    c.execute('SELECT * FROM machines WHERE analysis_completed = 0')
    rows = c.fetchall()
    columns = ['ID', 'Machine Name', 'Date Added', 'Date Completed', 'Analysis Completed']
    df = pd.DataFrame(rows, columns=columns)
    return df

# Initialize SQLite database
conn = init_db()

# Admin login check
def admin_login():
    username = st.sidebar.text_input("Admin Username")
    password = st.sidebar.text_input("Admin Password", type="password")
    if username == "admin" and password == "adminpassword":
        return True
    return False

# Main application starts here
st.title("Machine Analysis Tracking")

# Admin Panel
if admin_login():
    st.sidebar.write("Admin Panel")

    # Add a new machine with the suffix "ID"
    machine_number = st.sidebar.text_input("Enter Machine Number:", key="machine_input")

    if st.sidebar.button("Add Machine"):
        machine_name = f"ID{machine_number}"  # Automatically append "ID"
        add_machine_to_db(conn, machine_name)
        st.sidebar.success(f"Machine ID{machine_number} added on {datetime.now().strftime('%Y-%m-%d')}.")

    # Display all machines for admin
    df_all = get_all_machines(conn)
    st.write("All Machines (including completed ones):")
    st.write(df_all)

    # Provide download link for CSV
    csv_data = df_all.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="machines.csv",
        mime='text/csv',
    )

# Standard User View
else:
    st.sidebar.write("Standard User Panel")

    # Filter machines to show only incomplete ones
    df_incomplete = get_incomplete_machines(conn)

    # Select machine and mark analysis as done
    if not df_incomplete.empty:
        machine = st.selectbox("Select a machine", df_incomplete["Machine Name"])
        if st.button(f"Mark {machine} as Done"):
            mark_machine_as_done_in_db(conn, machine)
            st.success(f"Analysis for {machine} marked as completed on {datetime.now().strftime('%Y-%m-%d')}.")
    else:
        st.write("No pending machines for analysis.")

    # View machines that are pending analysis
    st.write("Machines pending analysis:")
    st.write(df_incomplete)
