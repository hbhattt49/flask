import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
from streamlit_js_eval import streamlit_js_eval

# Sample data
data = [
    {"Name": "Alice", "Age": 30},
    {"Name": "Bob", "Age": 25},
    {"Name": "Charlie", "Age": 35}
]
df = pd.DataFrame(data)
df["row_index"] = df.index  # add index to know which row was clicked

# Python function to call on button click
def handle_action(row_data):
    name = row_data.get("Name")
    age = row_data.get("Age")
    st.success(f"✅ Function executed for: {name} (Age: {age})")

# JavaScript code to create a Run button
run_button_renderer = JsCode("""
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
            window.parent.postMessage({isStreamlitMessage: true, type: 'FROM_JS', data: params.data.row_index}, '*');
        });
    }
    getGui() {
        return this.eGui;
    }
}
""")

# AgGrid configuration
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Run", header_name="Action", cellRenderer=run_button_renderer)
gb.configure_column("row_index", hide=True)  # hide internal row index column
grid_options = gb.build()

# Add dummy column to trigger button render
df["Run"] = ""  # this column will show the JS button

# Show table
st.title("🔥 Per-Row Button Table (Run triggers Python)")
AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.NO_UPDATE,
    allow_unsafe_jscode=True,
    height=300,
    fit_columns_on_grid_load=True
)

# Get row index from JS via postMessage
clicked_row_index = streamlit_js_eval(js_expressions="await new Promise(resolve => { window.addEventListener('message', e => { if (e.data && e.data.type === 'FROM_JS') resolve(e.data.data); }); });", key="js_listener")

# If a button was clicked, run Python function
if clicked_row_index is not None:
    clicked_row_data = data[clicked_row_index]
    handle_action(clicked_row_data)
