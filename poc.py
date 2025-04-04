import streamlit as st
import pandas as pd
import networkx as nx
from collections import defaultdict

def load_data(uploaded_file):
    """Load and preprocess the CSV data"""
    df = pd.read_csv(uploaded_file)
    # Ensure column names are standardized
    df.columns = [col.lower().strip() for col in df.columns]
    return df

def build_dependency_graph(df):
    """Build a directed graph of dependencies"""
    G = nx.DiGraph()
    
    # Add all procedures and tables as nodes
    for _, row in df.iterrows():
        source = row['source table']
        target = row['target table']
        procedure = row['procedure name']
        
        G.add_node(source, type='table')
        G.add_node(target, type='table')
        G.add_node(procedure, type='procedure')
        G.add_edge(source, procedure)
        G.add_edge(procedure, target)
    
    return G

def get_node_dependencies(G, node, direction='downstream', max_level=3, current_level=0):
    """Get dependencies in specified direction with level limitation"""
    if current_level > max_level:
        return []
    
    dependencies = []
    neighbors = G.successors(node) if direction == 'downstream' else G.predecessors(node)
    
    for neighbor in neighbors:
        node_type = G.nodes[neighbor]['type']
        deps = get_node_dependencies(G, neighbor, direction, max_level, current_level+1)
        dependencies.append({
            'name': neighbor,
            'type': node_type,
            'direction': direction,
            'level': current_level,
            'dependencies': deps
        })
    
    return dependencies

def display_node_with_dependencies(node_info, expanded_levels):
    """Display a node with its dependencies as expandable tree"""
    node_type_icon = "📊" if node_info['type'] == 'table' else "⚙️"
    direction_icon = "⬇️" if node_info['direction'] == 'downstream' else "⬆️"
    
    with st.expander(f"{node_type_icon} {node_info['name']} ({node_info['type']}) {direction_icon}", 
                   expanded=node_info['level'] < expanded_levels):
        
        # Display node type and action buttons
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"{node_info['type'].title()} - Level {node_info['level']}")
        with col2:
            if st.button("Explore", key=f"explore_{node_info['name']}"):
                st.session_state['selected_node'] = node_info['name']
        
        # Display dependencies
        for dep in node_info['dependencies']:
            display_node_with_dependencies(dep, expanded_levels)

def main():
    st.title("Advanced Procedure Dependency Explorer")
    
    # Initialize session state
    if 'selected_node' not in st.session_state:
        st.session_state['selected_node'] = None
    if 'view_direction' not in st.session_state:
        st.session_state['view_direction'] = 'downstream'
    
    # File upload
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    if not uploaded_file:
        st.info("Please upload a CSV file with source table, target table, and procedure name columns")
        return
    
    # Load and process data
    df = load_data(uploaded_file)
    G = build_dependency_graph(df)
    
    # Get all final tables (those not used as sources)
    all_tables = [n for n in G.nodes() if G.nodes[n]['type'] == 'table']
    final_tables = [t for t in all_tables if not any(G.nodes[p]['type'] == 'procedure' for p in G.successors(t))]
    
    # Control panel
    st.sidebar.header("Controls")
    expanded_levels = st.sidebar.slider("Default Expansion Depth", 0, 5, 1)
    st.session_state['view_direction'] = st.sidebar.radio(
        "View Direction", 
        ['downstream', 'upstream'], 
        format_func=lambda x: 'Downstream (output)' if x == 'downstream' else 'Upstream (input)'
    )
    
    # Node selection dropdown
    all_nodes = sorted(list(G.nodes()))
    selected_node = st.sidebar.selectbox(
        "Or select a specific node to explore:",
        all_nodes,
        index=all_nodes.index(st.session_state['selected_node']) if st.session_state['selected_node'] in all_nodes else 0
    )
    
    if st.sidebar.button("Explore Selected Node"):
        st.session_state['selected_node'] = selected_node
    
    # Main display
    if st.session_state['selected_node']:
        # Show selected node and its dependencies
        node = st.session_state['selected_node']
        node_type = G.nodes[node]['type']
        
        st.header(f"Exploring {node_type.title()}: {node}")
        
        # Show both upstream and downstream dependencies
        tab1, tab2 = st.tabs(["Downstream Dependencies", "Upstream Dependencies"])
        
        with tab1:
            downstream_deps = [{
                'name': node,
                'type': node_type,
                'direction': 'downstream',
                'level': 0,
                'dependencies': get_node_dependencies(G, node, 'downstream', expanded_levels, 1)
            }]
            for dep in downstream_deps:
                display_node_with_dependencies(dep, expanded_levels)
        
        with tab2:
            upstream_deps = [{
                'name': node,
                'type': node_type,
                'direction': 'upstream',
                'level': 0,
                'dependencies': get_node_dependencies(G, node, 'upstream', expanded_levels, 1)
            }]
            for dep in upstream_deps:
                display_node_with_dependencies(dep, expanded_levels)
    else:
        # Default view - show final tables
        st.subheader("Final Tables (not used as sources)")
        for table in final_tables:
            if st.button(f"📊 {table}", key=f"table_{table}"):
                st.session_state['selected_node'] = table
            
            # Show immediate procedures that write to this table
            writers = list(G.predecessors(table))
            if writers:
                st.caption(f"Written by: {', '.join(writers)}")
            else:
                st.caption("No writing procedures found")

if __name__ == "__main__":
    main()
