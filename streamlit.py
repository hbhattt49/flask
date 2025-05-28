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

# Add a hidden ID to track rows
df["id"] = df.index

# Function to be triggered
def handle_action(row):
    st.success(f"✅ Function executed for: {row['Name']} (Age: {row['Age']})")

# Use AgGrid with row selection
gb = GridOptionsBuilder.from_dataframe(df.drop(columns=["id"]))
gb.configure_selection("single", use_checkbox=True)
grid_options = gb.build()

st.title("📊 DataFrame-like Table with Row Selection and Button")

# Display the grid
response = AgGrid(
    df.drop(columns=["id"]),
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    height=300
)

# If a row is selected, show a Run button
selected_rows = response.get("selected_rows", [])

if len(selected_rows) > 0:
    selected_row = selected_rows[0]
    st.write("🔍 Selected Row:", selected_row)

    if st.button("Run"):
        handle_action(selected_row)
else:
    st.info("Select a row to enable the Run button.")
