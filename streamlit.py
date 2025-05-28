import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
from streamlit_js_eval import streamlit_js_eval

# Sample JSON data
json_data = [
    {"Name": "Alice", "Age": 30, "Country": "India"},
    {"Name": "Bob", "Age": 25, "Country": "USA"},
    {"Name": "Charlie", "Age": 35, "Country": "UK"}
]

# Convert to DataFrame
df = pd.DataFrame(json_data)
df["row_index"] = df.index
df["Run"] = ""

# Define the Python function to be triggered
def handle_action(row):
    st.success(f"✅ Python function executed for {row['Name']} (Age: {row['Age']}, Country: {row['Country']})")

# JavaScript button renderer using postMessage
run_button_renderer = JsCode("""
class BtnCellRenderer {
    init(params) {
        this.params = params;
        this.eGui = document.createElement('span');
        this.eGui.innerHTML = '▶️';
        this.eGui.style.cursor = 'pointer';
        this.eGui.style.fontSize = '18px';
        this.eGui.style.marginLeft = '10px';
        this.eGui.addEventListener('click', () => {
            const event = new CustomEvent("rowClicked", { detail: params.data.row_index });
            window.dispatchEvent(event);
        });
    }
    getGui() {
        return this.eGui;
    }
}
""")

# Build grid config
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Run", header_name="Action", cellRenderer=run_button_renderer)
gb.configure_column("row_index", hide=True)
grid_options = gb.build()

# Display grid
st.title("📊 Clickable Icon Inside Table Row")
AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.NO_UPDATE,
    fit_columns_on_grid_load=True,
    height=300,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
)

# Inject JS to send message to Streamlit parent window
streamlit_js_eval(js_expressions="""
window.addEventListener("rowClicked", (e) => {
    window.parent.postMessage({ isStreamlitMessage: true, type: "rowIndex", data: e.detail }, "*");
});
""", key="inject-js-listener", want_output=False)

# Receive message in Python
clicked_index = streamlit_js_eval(js_expressions="""
await new Promise((resolve) => {
    window.addEventListener("message", (e) => {
        if (e.data && e.data.type === "rowIndex") {
            resolve(e.data.data);
        }
    }, { once: true });
});
""", key="await-click")

# Handle click
if clicked_index is not None and str(clicked_index).isdigit():
    clicked_row = json_data[int(clicked_index)]
    handle_action(clicked_row)
