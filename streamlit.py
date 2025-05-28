import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
from streamlit_js_eval import streamlit_js_eval

# JSON input
json_data = [
    {"Name": "Alice", "Age": 30, "Country": "India"},
    {"Name": "Bob", "Age": 25, "Country": "USA"},
    {"Name": "Charlie", "Age": 35, "Country": "UK"}
]

# Convert to DataFrame with row index
df = pd.DataFrame(json_data)
df["row_index"] = df.index
df["Run"] = ""  # Action column placeholder

# Python function to run
def handle_action(row):
    st.success(f"✅ Function executed for {row['Name']} (Age: {row['Age']}, Country: {row['Country']})")

# JS Code to render the Run button per row
run_button_renderer = JsCode("""
class BtnCellRenderer {
    init(params) {
        this.params = params;
        this.eGui = document.createElement('span');
        this.eGui.innerHTML = `▶️`;
        this.eGui.style.cursor = 'pointer';
        this.eGui.style.fontSize = '18px';
        this.eGui.style.marginLeft = '10px';
        this.eGui.addEventListener('click', () => {
            window.localStorage.setItem("clicked_row", params.data.row_index);
            window.dispatchEvent(new Event("storage"));
        });
    }
    getGui() {
        return this.eGui;
    }
}
""")

# Grid setup
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Run", header_name="Action", cellRenderer=run_button_renderer)
gb.configure_column("row_index", hide=True)
grid_options = gb.build()

# Show AgGrid
st.title("📊 JSON Grid with Inline Run Icon")
AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.NO_UPDATE,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
    height=300,
    fit_columns_on_grid_load=True
)

# JS → Python bridge: listen to row clicks
clicked_index = streamlit_js_eval(js_expressions="""
await new Promise((resolve) => {
    const handler = () => {
        const index = localStorage.getItem("clicked_row");
        resolve(index);
    };
    window.addEventListener("storage", handler, { once: true });
});
""", key="listen-click")

# If user clicked a row icon
if clicked_index and clicked_index.isnumeric():
    clicked_row = json_data[int(clicked_index)]
    handle_action(clicked_row)
