import streamlit as st
import pandas as pd

# Sample JSON data
json_data = [
    {"Name": "Alice", "Age": 30, "Country": "India"},
    {"Name": "Bob", "Age": 25, "Country": "USA"},
    {"Name": "Charlie", "Age": 35, "Country": "UK"}
]

st.title("📋 JSON Table with Inline Action Buttons")

# Table header
header_cols = st.columns([3, 2, 3, 1])
header_cols[0].markdown("**Name**")
header_cols[1].markdown("**Age**")
header_cols[2].markdown("**Country**")
header_cols[3].markdown("**Action**")

# Styled rows with inline buttons
for i, row in enumerate(json_data):
    row_cols = st.columns([3, 2, 3, 1])
    row_cols[0].markdown(f"<div style='padding-top: 8px'>{row['Name']}</div>", unsafe_allow_html=True)
    row_cols[1].markdown(f"<div style='padding-top: 8px'>{row['Age']}</div>", unsafe_allow_html=True)
    row_cols[2].markdown(f"<div style='padding-top: 8px'>{row['Country']}</div>", unsafe_allow_html=True)

    # Inline button
    if row_cols[3].button("▶️", key=f"run_{i}"):
        st.success(f"✅ Function executed for {row['Name']} (Age: {row['Age']}, Country: {row['Country']})")
