import streamlit as st
import pandas as pd

# Sample JSON data
json_data = [
    {"Name": "Alice", "Age": 30, "Country": "India"},
    {"Name": "Bob", "Age": 25, "Country": "USA"},
    {"Name": "Charlie", "Age": 35, "Country": "UK"}
]

# Title
st.title("📋 Table with Per-Row Clickable Icon")

# Header row
col1, col2, col3, col4 = st.columns([3, 2, 3, 1])
col1.markdown("**Name**")
col2.markdown("**Age**")
col3.markdown("**Country**")
col4.markdown("**Run**")

# Render each row with a button/icon
for i, row in enumerate(json_data):
    col1, col2, col3, col4 = st.columns([3, 2, 3, 1])
    col1.write(row["Name"])
    col2.write(row["Age"])
    col3.write(row["Country"])
    
    if col4.button("▶️", key=f"run_{i}"):
        st.success(f"✅ Function executed for {row['Name']} (Age: {row['Age']}, Country: {row['Country']})")
