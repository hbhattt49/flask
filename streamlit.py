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

# Custom JS button per row
button_renderer = JsCode('''
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
                const event = new CustomEvent('runRow', {{ detail: params.data }});
                window.dispatchEvent(event);
            });
        }
        getGui() {
            return this.eGui;
        }
    }
''')

# Add dummy "Action" column for button
df["Action"] = ""

# Grid options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Action", header_name="Run", cellRenderer=button_renderer)
grid_options = gb.build()

# Display grid
st.title("Styled Table with Buttons (Like st.dataframe)")
AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.NO_UPDATE,
    allow_unsafe_jscode=True,
    height=300,
    fit_columns_on_grid_load=True
)

# Inject JS to listen for row button click
st.components.v1.html(
    """
    <script>
    window.addEventListener('runRow', function(e) {
        const row = e.detail;
        alert("Function executed for " + row.Name + " (Age: " + row.Age + ")");
        // Optionally: send row data to Streamlit via URL param or hidden form
    });
    </script>
    """,
    height=0,
)
