import streamlit as st
import pandas as pd

# Sample data
data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
]
df = pd.DataFrame(data)

# Function to handle the Run action
def handle_action(row):
    st.success(f"Function executed for: {row['name']} (Age: {row['age']})")

# Display the full DataFrame
st.title("DataFrame View")
st.dataframe(df, use_container_width=True)

# Show buttons row by row
st.markdown("### Actions:")
for i, row in df.iterrows():
    cols = st.columns([6, 1])
    with cols[0]:
        st.write(f"Row {i+1}: {row.to_dict()}")
    with cols[1]:
        if st.button("Run", key=f"run_{i}"):
            handle_action(row)
