import streamlit as st
import pandas as pd

# Sample JSON data
data = [
    {"Name": "Alice", "Age": 30},
    {"Name": "Bob", "Age": 25},
    {"Name": "Charlie", "Age": 35}
]
df = pd.DataFrame(data)

st.title("Custom Data Table with Buttons")

# Header row
cols = st.columns([2, 1, 1])  # Adjust column widths
cols[0].markdown("**Name**")
cols[1].markdown("**Age**")
cols[2].markdown("**Action**")

# Render rows with buttons
for i, row in df.iterrows():
    cols = st.columns([2, 1, 1])
    cols[0].write(row["Name"])
    cols[1].write(row["Age"])
    if cols[2].button("Run", key=f"run_{i}"):
        st.success(f"Function executed for: {row['Name']} (Age: {row['Age']})")
