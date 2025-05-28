import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Sample Data
data = [
    {"Name": "Alice", "Age": 30},
    {"Name": "Bob", "Age": 25},
    {"Name": "Charlie", "Age": 35}
]
df = pd.DataFrame(data)

# Function to run
def handle_action(row_data):
    name = row_data.get("Name", "Unknown")
    age = row_data.get("Age", "Unknown")
    st.success(f"✅ Function executed for: {name} (Age: {age})")

# Configure AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single', use_checkbox=True)
grid_options = gb.build()

# Display table
st.title("📋 Data Table with Per-Row Action Button")

response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    height=300,
    allow_unsafe_jscode=True
)

# Extract selected row(s)
selected_rows = response.get("selected_rows", [])

# Ensure selected_rows is a list and non-empty
if isinstance(selected_rows, list) and len(selected_rows) > 0:
    selected_row = selected_rows[0]  # First selected row
    st.write("Selected Row:", selected_row)

    if st.button("Run"):
        handle_action(selected_row)
else:
    st.info("👉 Please select a row to enable the 'Run' button.")
