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
    .styled
