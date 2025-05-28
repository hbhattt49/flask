import streamlit as st
import pandas as pd

# Sample JSON data
json_data = [
    {"Name": "Alice", "Age": 30, "Country": "India"},
    {"Name": "Bob", "Age": 25, "Country": "USA"},
    {"Name": "Charlie", "Age": 35, "Country": "UK"}
]

# CSS for better table layout
st.markdown("""
    <style>
    .custom-table {
        border-collapse: collapse;
        width: 100%;
        margin-top: 10px;
    }
    .custom-table th, .custom-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
        vertical-align: middle;
    }
    .custom-table th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Beautiful Table with Per-Row Buttons")

# Create table header
table_html = """
<table class="custom-table">
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Country</th>
            <th>Run</th>
        </tr>
    </thead>
    <tbody>
"""

# Create table rows
for i, row in enumerate(json_data):
    button_placeholder = st.empty()
    table_html += f"""
    <tr>
        <td>{row['Name']}</td>
        <td>{row['Age']}</td>
        <td>{row['Country']}</td>
        <td>{button_placeholder._id}</td>
    </tr>
    """

# Close table
table_html += "</tbody></table>"

# Render the HTML table (without buttons)
st.markdown(table_html, unsafe_allow_html=True)

# Render real buttons below, mapped by index
for i, row in enumerate(json_data):
    if st.button(f"▶️ Run for {row['Name']}", key=f"btn_{i}"):
        st.success(f"✅ Function executed for {row['Name']} (Age: {row['Age']}, Country: {row['Country']})")
