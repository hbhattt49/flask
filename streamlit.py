import streamlit as st

# Sample JSON-like data
data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
]

# Python function to call on button click
def handle_action(name):
    st.info(f"Function executed for: {name}")

# Title
st.title("JSON Data with Action Button")

# Header row
header1, header2, header3 = st.columns([2, 2, 1])
with header1:
    st.markdown("**Name**")
with header2:
    st.markdown("**Age**")
with header3:
    st.markdown("**Action**")

# Display each row with a button
for i, row in enumerate(data):
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.write(row['name'])

    with col2:
        st.write(row['age'])

    with col3:
        if st.button("Run", key=f"run_{i}"):
            handle_action(row['name'])
