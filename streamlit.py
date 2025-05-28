import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ✅ Your JSON input
json_data = [
    {"Name": "Alice", "Age": 30, "Country": "India"},
    {"Name": "Bob", "Age": 25, "Country": "USA"},
    {"Name": "Charlie", "Age": 35, "Country": "UK"}
]

# ✅ Convert to DataFrame
df = pd.DataFrame(json_data)
df["row_id"] = df.index  # Add index to identify row
df["Action"] = "▶️ Run"  # This will act as a button

# ✅ Grid builder (free features only)
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Action", editable=False)
gb.configure_column("row_id", hide=True)
gb.configure_selection('single', use_checkbox=True)  # Optional
grid_options = gb.build()

# ✅ Display the grid
st.title("📊 JSON Grid with Per-Row Button")
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False  # ✅ NO watermark
)

# ✅ Get selected row
selected = grid_response.get("selected_rows", [])
if selected:
    row = selected[0]
    if st.button(f"▶️ Run for {row['Name']}", key=row["row_id"]):
        st.success(f"Function executed for {row['Name']} (Age: {row['Age']}, Country: {row['Country']})")
else:
    st.info("Select a row using the checkbox to enable the Run button.")
