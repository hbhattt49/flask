import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Sample JSON data
data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
]

# Convert to DataFrame
df = pd.DataFrame(data)

# Function to call on selection
def handle_action(selected_row):
    name = selected_row["name"]
    st.success(f"Function executed for: {name}")

st.title("DataFrame with Action Button")

# Configure AgGrid with row selection
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single', use_checkbox=True)  # Enable row selection
grid_options = gb.build()

# Render the data table
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=200,
    fit_columns_on_grid_load=True
)

# Extract selected row
selected = grid_response['selected_rows']

# Show button to trigger action
if selected:
    if st.button("Run on selected row"):
        handle_action(selected[0])
