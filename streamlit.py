import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode

# Sample data
data = [
    {"Name": "Alice", "Age": 30},
    {"Name": "Bob", "Age": 25},
    {"Name": "Charlie", "Age": 35}
]
df = pd.DataFrame(data)

# Define a JavaScript cell renderer for the button (escaped properly)
button_renderer = JsCode("""
    class BtnCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('button');
            this.eGui.innerText = 'Run';
            this.eGui.style.backgroundColor = '#4CAF50';
            this.eGui.style.color = 'white';
            this.eGui.style.border = 'none';
            this.eGui.style.padding = '4px 8px';
            this.eGui.style.cursor = 'pointer';
            this.eGui.addEventListener('click', () => {
                alert('Function executed for: ' + params.data.Name + ' (Age: ' + params.data.Age + ')');
            });
        }
        getGui() {
            return this.eGui;
        }
    }
""")

# Add dummy Action column
df["Action"] = ""

# Grid setup
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Action", header_name="Run", cellRenderer=button_renderer)
grid_options = gb.build()

# Display the grid
st.title("DataFrame with Inline Buttons")
AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.NO_UPDATE,
    allow_unsafe_jscode=True,
    height=300,
    fit_columns_on_grid_load=True
)
