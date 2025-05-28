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
gb.configure_selection(selection_mode="single", use_checkbox=True)
grid_options = gb.build()

# Render AgGrid
st.title("📊 Data Table with Row Selection and Python Action")
response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    height=300,
    allow_unsafe_jscode=True
)

# Extract selected rows (it's a list of dicts)
selected_rows = response.get("selected_rows", [])

# Safely process selection
if isinstance(selected_rows, list) and len(selected_rows) > 0:
    selected_row = selected_rows[0]  # ✅ This is a dict like {'Name': 'Alice', 'Age': 30}
    st.write("You selected:", selected_row)

    if st.button("Run"):
        handle_action(selected_row)
else:
    st.info("Please select a row using the checkbox to enable the 'Run' button.")
