import json
import streamlit as st
import os


# Path to your google_credentials.json file
json_file_path = "google_credentials.json"
# Read the client secret from secrets.toml
try:
    client_secret = st.secrets["google_credentials"]["g_client_secret"]
except KeyError:
    st.error("Client secret not found in secrets.toml. Please add 'g-client_secret' to your secrets.")
    st.stop()
def loadconfig():
    # Check if the file exists
    if not os.path.exists(json_file_path):
        st.error(f"The file {json_file_path} does not exist.")
        st.stop()

    # Read the existing google_credentials.json file
    with open(json_file_path, "r") as file:
        credentials = json.load(file)

    # Update the client_secret in the credentials
    credentials["web"]["client_secret"] = client_secret

    # Write the updated credentials back to the file
    with open(json_file_path, "w") as file:
        json.dump(credentials, file, indent=2)