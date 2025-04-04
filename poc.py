import streamlit as st
import pandas as pd
import networkx as nx
from collections import defaultdict

def load_data(uploaded_file):
    """Load and preprocess the CSV data"""
    df = pd.read_csv(uploaded_file)
    # Ensure column names are standardized (case-insensitive)
    df.columns = [col.lower().strip() for col in df.columns]
    return df

def build_dependency_graph(df):
    """Build a directed graph of dependencies"""
    G = nx.DiGraph()
    
    # Add all procedures as nodes first
    all_procedures = set(df['procedure name'].unique())
    for proc in all_procedures:
        G.add_node(proc, type='procedure')
    
    # Add table nodes and edges
    for _, row in df.iterrows():
        source = row['source table']
        target = row['target table']
        procedure = row['procedure name']
        
        G.add_node(source, type='table')
        G.add_node(target, type='table')
        G.add_edge(source, procedure)
        G.add_edge(procedure, target)
    
    return G

def get_final_procedures(G):
    """Identify procedures that don't feed into other procedures (final procedures)"""
    final_procs = []
    for node in G.nodes():
        if G.nodes[node]['type'] == 'procedure':
            successors = list(G.successors(node))
            # If all successors are tables (not procedures), it's a final procedure
            if all(G.nodes[succ]['type'] == 'table' for succ in successors):
                final_procs.append(node)
    return final_procs

def get_dependencies(G, procedure, level=0, max_level=10):
    """Recursively get dependencies up to a certain level"""
    if level > max_level:
        return []
    
    dependencies = []
    for predecessor in G.predecessors(procedure):
        node_type = G.nodes[predecessor]['type']
        deps = get_dependencies(G, predecessor, level+1, max_level)
        dependencies.append({
            'name': predecessor,
            'type': node_type,
            'level': level,
            'dependencies': deps
        })
    
    return dependencies

def display_dependency_tree(dependency, expanded_levels):
    """Recursively display the dependency tree with expanders"""
    if dependency['level'] > expanded_levels:
        return
    
    with st.expander(f"{dependency['type'].title()}: {dependency['name']}", expanded=dependency['level']==0):
        for dep in dependency['dependencies']:
            display_dependency_tree(dep, expanded_levels)

def main():
    st.title("Procedure Dependency Explorer")
    
    # File upload
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    if not uploaded_file:
        st.info("Please upload a CSV file with source table, target table, and procedure name columns")
        return
    
    # Load and process data
    df = load_data(uploaded_file)
    G = build_dependency_graph(df)
    final_procedures = get_final_procedures(G)
    
    st.subheader("Final Procedures")
    
    # Slider to control expansion depth
    expanded_levels = st.slider("Expansion Depth", 0, 10, 0, 
                               help="Control how many levels of dependencies to show by default")
    
    # Display each final procedure with its dependencies
    for proc in final_procedures:
        dependencies = [{
            'name': proc,
            'type': 'procedure',
            'level': 0,
            'dependencies': get_dependencies(G, proc, 1, expanded_levels)
        }]
        
        for dep in dependencies:
            display_dependency_tree(dep, expanded_levels)

if __name__ == "__main__":
    main()
