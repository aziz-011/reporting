import streamlit as st
import pandas as pd
import yagmail
import os


# Email setup
def send_email(notification_email, machine_name):
    yag = yagmail.SMTP("aziz.bengandia11@gmail.com", "20999252A")
    subject = "Analysis Completed"
    body = f"The analysis for machine {machine_name} has been completed."
    yag.send(to=notification_email, subject=subject, contents=body)
    st.success(f"Email notification sent to {notification_email}.")


# Admin login check
def admin_login():
    username = st.sidebar.text_input("Admin Username")
    password = st.sidebar.text_input("Admin Password", type="password")
    if username == "admin" and password == "adminpassword":
        return True
    return False


# Initialize data for machines
if not os.path.exists("machines.csv"):
    df = pd.DataFrame(columns=["Machine Name", "Analysis Completed"])
    df.to_csv("machines.csv", index=False)

# Read machine data
df = pd.read_csv("machines.csv")

st.title("Machine Analysis Tracking")

# Admin Panel
if admin_login():
    st.sidebar.write("Admin Panel")

    # Add a new machine
    machine_name = st.sidebar.text_input("Enter Machine Name:")
    if st.sidebar.button("Add Machine"):
        new_row = pd.DataFrame({"Machine Name": [machine_name], "Analysis Completed": [False]})
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv("machines.csv", index=False)
        st.sidebar.success(f"Machine {machine_name} added.")

    # View and manage all machines
    st.write("All Machines:")
    st.write(df)

# Standard User View
else:
    st.sidebar.write("Standard User Panel")

    # Select machine and mark analysis as done
    machine = st.selectbox("Select a machine", df["Machine Name"])
    if st.button(f"Mark {machine} as Done"):
        df.loc[df["Machine Name"] == machine, "Analysis Completed"] = True
        df.to_csv("machines.csv", index=False)
        st.success(f"Analysis for {machine} marked as completed.")

        # Send notification email when analysis is marked done
        send_email("admin_email@example.com", machine)

    # View machines that are pending analysis
    st.write("Machines pending analysis:")
    st.write(df[df["Analysis Completed"] == False])

