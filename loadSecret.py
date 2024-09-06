import json
import streamlit as st
import os

# Read the client secret from secrets.toml
client_secret = st.secrets["g-client_secret"]

# Read the existing google_credentials.json file
json_file_path = "./google_credentials.json"
with open(json_file_path, "r") as file:
    credentials = json.load(file)

# Update the client_secret in the credentials
credentials["web"]["client_secret"] = client_secret

# Write the updated credentials back to the file
with open(json_file_path, "w") as file:
    json.dump(credentials, file, indent=2)
