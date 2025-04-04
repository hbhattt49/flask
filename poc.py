import streamlit as st
import pandas as pd
import networkx as nx
import hashlib

def load_data(uploaded_file):
    """Load and preprocess the CSV data"""
    df = pd.read_csv(uploaded_file)
    df.columns = [col.lower().strip() for col in df.columns]
    return df

def build_dependency_graph(df):
    """Build a directed graph of dependencies"""
    G = nx.DiGraph()
    
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

def generate_unique_key(node_name, prefix=""):
    """Generate a unique key using hash of the node name"""
    return f"{prefix}_{hashlib.md5(node_name.encode()).hexdigest()}"

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
    
    # Generate unique keys for each expander and button
    expander_key = generate_unique_key(f"exp_{node_info['name']}_{node_info['direction']}_{node_info['level']}")
    button_key = generate_unique_key(f"btn_{node_info['name']}_{node_info['direction']}_{node_info['level']}")
    
    with st.expander(f"{node_type_icon} {node_info['name']} ({node_info['type']}) {direction_icon}", 
                   expanded=node_info['level'] < expanded_levels,
                   key=expander_key):
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"{node_info['type'].title()} - Level {node_info['level']}")
        with col2:
            if st.button("Explore", key=button_key):
                st.session_state['selected_node'] = node_info['name']
                st.rerun()
        
        for dep in node_info['dependencies']:
            display_node_with_dependencies(dep, expanded_levels)

def main():
    st.set_page_config(layout="wide")
    st.title("Procedure Dependency Explorer")
    
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
    
    # Get all nodes for selection
    all_nodes = sorted(list(G.nodes()))
    
    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        expanded_levels = st.slider("Default Expansion Depth", 0, 5, 1)
        view_direction = st.radio(
            "View Direction", 
            ['downstream', 'upstream'], 
            index=0,
            key='view_direction_radio'
        )
        
        selected_node = st.selectbox(
            "Select a node to explore:",
            all_nodes,
            index=all_nodes.index(st.session_state['selected_node']) if st.session_state['selected_node'] in all_nodes else 0,
            key='node_selectbox'
        )
        
        if st.button("Explore Node", key='explore_node_btn'):
            st.session_state['selected_node'] = selected_node
            st.rerun()
        
        if st.button("Reset View", key='reset_view_btn'):
            st.session_state['selected_node'] = None
            st.rerun()
    
    # Main display
    if st.session_state['selected_node']:
        node = st.session_state['selected_node']
        node_type = G.nodes[node]['type']
        
        st.header(f"Exploring {node_type.title()}: {node}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Upstream Dependencies (Inputs)")
            upstream_deps = [{
                'name': node,
                'type': node_type,
                'direction': 'upstream',
                'level': 0,
                'dependencies': get_node_dependencies(G, node, 'upstream', expanded_levels, 1)
            }]
            for dep in upstream_deps:
                display_node_with_dependencies(dep, expanded_levels)
        
        with col2:
            st.subheader("Downstream Dependencies (Outputs)")
            downstream_deps = [{
                'name': node,
                'type': node_type,
                'direction': 'downstream',
                'level': 0,
                'dependencies': get_node_dependencies(G, node, 'downstream', expanded_levels, 1)
            }]
            for dep in downstream_deps:
                display_node_with_dependencies(dep, expanded_levels)
    else:
        # Default view - show all tables and procedures
        st.subheader("All Nodes")
        
        tables = [n for n in G.nodes() if G.nodes[n]['type'] == 'table']
        procedures = [n for n in G.nodes() if G.nodes[n]['type'] == 'procedure']
        
        tab1, tab2 = st.tabs(["Tables", "Procedures"])
        
        with tab1:
            for table in sorted(tables):
                if st.button(f"📊 {table}", key=generate_unique_key(f"table_btn_{table}")):
                    st.session_state['selected_node'] = table
                    st.rerun()
        
        with tab2:
            for proc in sorted(procedures):
                if st.button(f"⚙️ {proc}", key=generate_unique_key(f"proc_btn_{proc}")):
                    st.session_state['selected_node'] = proc
                    st.rerun()

if __name__ == "__main__":
    main()
