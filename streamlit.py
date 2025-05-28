import streamlit as st
import pandas as pd

# Sample JSON data
json_data = [
    {"Name": "Alice", "Age": 30, "Country": "India"},
    {"Name": "Bob", "Age": 25, "Country": "USA"},
    {"Name": "Charlie", "Age": 35, "Country": "UK"}
]

# Convert to DataFrame
df = pd.DataFrame(json_data)

# Apply styling and show table
st.markdown("### 📋 Data Table")
st.markdown(
    df.to_html(index=False, classes="styled-table", escape=False),
    unsafe_allow_html=True
)

# CSS to style the HTML table
st.markdown("""
    <style>
    .styled-table {
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 16px;
        width: 100%;
    }
    .styled-table th, .styled-table td {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
    }
    .styled-table th {
        background-color: #f2f2f2;
    }
    </style>
""", unsafe_allow_html=True)

# Row-wise buttons
st.markdown("### 🧩 Actions")
for i, row in enumerate(json_data):
    if st.button(f"▶️ Run for {row['Name']}", key=f"run_{i}"):
        st.success(f"✅ Function executed for {row['Name']} (Age: {row['Age']}, Country: {row['Country']})")
