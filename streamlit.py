import streamlit as st

# Sample JSON data
json_data = [
    {"Name": "Alice", "Age": 30, "Country": "India"},
    {"Name": "Bob", "Age": 25, "Country": "USA"},
    {"Name": "Charlie", "Age": 35, "Country": "UK"}
]

st.markdown("""
<style>
.table-row {
    border-bottom: 1px solid #DDD;
    padding: 8px 0;
}
.table-header {
    font-weight: bold;
    border-bottom: 2px solid #AAA;
    padding-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

st.title("📋 Table with Aligned Per-Row Buttons")

# Header
header_cols = st.columns([3, 1, 2, 1])
header_cols[0].markdown("<div class='table-header'>Name</div>", unsafe_allow_html=True)
header_cols[1].markdown("<div class='table-header'>Age</div>", unsafe_allow_html=True)
header_cols[2].markdown("<div class='table-header'>Country</div>", unsafe_allow_html=True)
header_cols[3].markdown("<div class='table-header'>Action</div>", unsafe_allow_html=True)

# Rows
for i, row in enumerate(json_data):
    cols = st.columns([3, 1, 2, 1])
    cols[0].markdown(f"<div class='table-row'>{row['Name']}</div>", unsafe_allow_html=True)
    cols[1].markdown(f"<div class='table-row'>{row['Age']}</div>", unsafe_allow_html=True)
    cols[2].markdown(f"<div class='table-row'>{row['Country']}</div>", unsafe_allow_html=True)
    with cols[3]:
        if st.button("▶️", key=f"run_{i}"):
            st.success(f"✅ Function executed for {row['Name']} (Age: {row['Age']}, Country: {row['Country']})")
