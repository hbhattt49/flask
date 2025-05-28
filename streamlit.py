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
df["row_index"] = df.index  # Add index to identify the clicked row

# JS button renderer
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
            window.localStorage.setItem("clicked_row", params.data.row_index);
            window.dispatchEvent(new Event("storage"));  // Notify change
        });
    }
    getGui() {
        return this.eGui;
    }
}
""")

# Add dummy Action column
df["Run"] = ""

# Build grid options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Run", header_name="Action", cellRenderer=button_renderer)
gb.configure_column("row_index", hide=True)
grid_options = gb.build()

# Render grid
st.title("✅ Data Table with Real Buttons (Python Trigger)")
AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.NO_UPDATE,
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    height=300
)

# Listen for button click via JS event
clicked_index = streamlit_js_eval(js_expressions="""
await new Promise((resolve) => {
    const handler = () => {
        const index = localStorage.getItem("clicked_row");
        resolve(index);
    };
    window.addEventListener("storage", handler, { once: true });
});
""", key="button-listener")

# Handle Python action
if clicked_index and clicked_index.isnumeric():
    row = data[int(clicked_index)]
    st.success(f"🎯 Python function executed for: {row['Name']} (Age: {row['Age']})")
