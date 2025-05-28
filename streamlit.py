import streamlit as st
import pandas as pd

# Sample JSON data
json_data = [
    {"Name": "Alice", "Age": 30, "Country": "India"},
    {"Name": "Bob", "Age": 25, "Country": "USA"},
    {"Name": "Charlie", "Age": 35, "Country": "UK"}
]

# Table Styling
st.markdown("""
    <style>
    .grid-row {
        display: grid;
        grid-template-columns: 3fr 1fr 2fr 1fr;
        border-bottom: 1px solid #ddd;
        padding: 6px 0;
        align-items: center;
    }
    .grid-header {
        font-weight: bold;
        background-color: #f0f0f0;
        border-top: 1px solid #ddd;
    }
    .grid-cell {
        padding-left: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📋 JSON Grid Table with Per-Row Button")

# Header
st.markdown("""
<div class="grid-row grid-header">
    <div class="grid-cell">Name</div>
    <div class="grid-cell">Age</div>
    <div class="grid-cell">Country</div>
    <div class="grid-cell">Action</div>
</div>
""", unsafe_allow_html=True)

# Data rows
for i, row in enumerate(json_data):
    cols = st.columns([3, 1, 2, 1])
    with cols[0]:
        st.markdown(f"<div class='grid-cell'>{row['Name']}</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='grid-cell'>{row['Age']}</div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='grid-cell'>{row['Country']}</div>", unsafe_allow_html=True)
    with cols[3]:
        if st.button("▶️", key=f"run_{i}"):
            st.success(f"✅ Function executed for {row['Name']} (Age: {row['Age']}, Country: {row['Country']})")
