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

# Function to run when user clicks Run
def handle_action(row_data):
    st.success(f"Function executed for: {row_data['Name']} (Age: {row_data['Age']})")

# Grid config
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single', use_checkbox=True)  # Enable row selection
grid_options = gb.build()

# Display grid
st.title("Styled Table with Row Action")
response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True
)

# Check if a row is selected
selected = response['selected_rows']
if len(selected) > 0:
    st.markdown("### Action on Selected Row:")
    if st.button("Run"):
        handle_action(selected[0])
