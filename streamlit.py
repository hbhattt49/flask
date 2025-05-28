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

# Python function to run
def handle_action(row_data):
    st.success(f"✅ Function executed for {row_data['Name']} (Age: {row_data['Age']})")

# Build grid options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection("single", use_checkbox=True)  # ✔️ Make sure you use checkbox to select
grid_options = gb.build()

# Display AgGrid
st.title("📊 Data Table with Selectable Row + Action Button")
response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,  # Updates selection immediately
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    height=300
)

# Extract selected row
selected_rows = response.get("selected_rows", [])

# Show Run button only if a row is selected
if len(selected_rows) > 0:
    selected_row = selected_rows[0]  # This is a dict
    st.markdown("### ✅ Selected Row:")
    st.json(selected_row)

    if st.button("Run"):
        handle_action(selected_row)
else:
    st.info("👉 Please select a row using the **checkbox** to enable the 'Run' button.")
