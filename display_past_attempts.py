import pandas as pd
import os
import json
import streamlit as st

def display_past_attempts():
    st.title("Past Attempts")

    attempts = load_past_attempts()
    if not attempts:
        st.write("No past attempts found.")
        return

    df = pd.DataFrame(attempts)

    operations = df['Operation'].unique()
    selected_operation = st.selectbox("Select Operation", ['All'] + list(operations))

    if selected_operation != 'All':
        df = df[df['Operation'] == selected_operation]

    st.dataframe(df)

    csv = df.to_csv(index=False)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=f"math_practice_results_{selected_operation}.csv",
        mime="text/csv",
    )

def load_past_attempts():
    attempts = []
    directory = "users"
    if not os.path.exists(directory):
        return attempts
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as file:
                data = json.load(file)
                attempts.append(data)
    return attempts