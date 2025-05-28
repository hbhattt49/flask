import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ✅ Sample data
df = pd.DataFrame([
    {"Name": "Alice", "Age": 30},
    {"Name": "Bob", "Age": 25},
    {"Name": "Charlie", "Age": 35}
])

# ✅ AgGrid config
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single', use_checkbox=True)
grid_options = gb.build()

# ✅ Show the grid
response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    height=300,
    allow_unsafe_jscode=True
)

# ✅ Inspect what's returned
selected_rows = response.get("selected_rows", [])

st.write("Type of selected_rows:", type(selected_rows))
if len(selected_rows) > 0:
    st.json(selected_rows[0])  # ✅ this should be a dict
    if st.button("Run"):
        row = selected_rows[0]
        st.success(f"Function executed for {row['Name']} (Age: {row['Age']})")
else:
    st.info("Please select a row using the checkbox.")
