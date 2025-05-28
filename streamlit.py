import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Sample data
data = [
    {"Name": "Alice", "Age": 30},
    {"Name": "Bob", "Age": 25},
    {"Name": "Charlie", "Age": 35}
]
df = pd.DataFrame(data)

# Function to call
def handle_action(row_data):
    name = row_data.get("Name", "Unknown")
    age = row_data.get("Age", "Unknown")
    st.success(f"✅ Function executed for: {name} (Age: {age})")

# Configure AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection("single", use_checkbox=True)
grid_options = gb.build()

# Render table
st.title("📊 Interactive Table with Row Selection")
response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    height=300,
    allow_unsafe_jscode=True
)

# Safe selection
selected_rows = response.get("selected_rows", [])

if isinstance(selected_rows, list) and len(selected_rows) > 0:
    selected_row = selected_rows[0]  # ✅ already a dict
    st.write("Selected Row:", selected_row)

    if st.button("Run"):
        handle_action(selected_row)
else:
    st.info("Please select a row from the table.")
