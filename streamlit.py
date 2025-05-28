import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Sample data
data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
]
df = pd.DataFrame(data)

# Dummy column to simulate action button
df["Action"] = ["Run"] * len(df)

# Function to be called
def handle_action(row_data):
    st.success(f"Function executed for: {row_data['name']} (Age: {row_data['age']})")

# Build GridOptions with cell click enabled
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_columns(df.columns, editable=False)
gb.configure_column("Action", header_name="Action", cellStyle={'color': 'white', 'backgroundColor': 'green', 'textAlign': 'center'})
gb.configure_grid_options(enableCellTextSelection=True)
grid_options = gb.build()

# Render the table
st.title("DataFrame with Action Column")

grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    height=300,
    enable_enterprise_modules=False
)

# Detect clicks
selected = grid_response['data']
clicked = grid_response.get('selected_rows', [])

# Button-like simulation: if last clicked cell is in "Action" column
if grid_response['selected_rows']:
    last_row = grid_response['selected_rows'][0]
    if last_row["Action"] == "Run":
        handle_action(last_row)
