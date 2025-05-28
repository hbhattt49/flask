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

# Define a Python function to execute
def handle_action(row):
    st.success(f"✅ Function executed for: {row['Name']} (Age: {row['Age']})")

# Set up AgGrid options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single', use_checkbox=True)
grid_options = gb.build()

# Display the grid
st.title("✅ AgGrid Table with Selectable Row + Run Action")

response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True
)

# 🔍 Inspect actual return type (debugging step)
st.markdown("#### 🧪 Raw AgGrid Response:")
st.write(response)

selected_rows = response.get("selected_rows", [])

# ✅ Correctly handle row selection
if isinstance(selected_rows, list) and len(selected_rows) > 0:
    selected_row = selected_rows[0]  # ✅ this is a dict
    st.json(selected_row)

    if st.button("Run"):
        handle_action(selected_row)
else:
    st.info("Select a row using the checkbox to show the 'Run' button.")
