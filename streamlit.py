import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Sample data
data = [
    {"Name": "Alice", "Age": 30},
    {"Name": "Bob", "Age": 25},
    {"Name": "Charlie", "Age": 35}
]

# Convert to DataFrame
df = pd.DataFrame(data)

# Python function to run
def handle_action(row_data):
    name = row_data.get("Name", "Unknown")
    age = row_data.get("Age", "Unknown")
    st.success(f"✅ Function executed for {name} (Age: {age})")

# Build AgGrid options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection(selection_mode="single", use_checkbox=True)_
