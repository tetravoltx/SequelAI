from models.db_model import db, Node, Edge
import random

def get_graph_data():
    """Retrieve nodes and edges from the database for graph visualization"""
    
    # Get all nodes and edges
    nodes = Node.query.all()
    edges = Edge.query.all()
    
    # Assign colors based on node clustering or other properties
    # For demonstration, we'll use a set of predefined colors
    colors = ["#7C9FDF", "#B290D6", "#7ED1B8", "#F0E98C", "#D67E7E"]
    
    # Format data for Sigma.js
    nodes_data = []
    for i, node in enumerate(nodes):
        node_data = node.to_dict()
        
        # Assign a color if not already set
        if not node.color or node.color == "#B290D6":
            node_data["color"] = colors[i % len(colors)]
            
        nodes_data.append(node_data)
    
    edges_data = [edge.to_dict() for edge in edges]
    
    # Return formatted graph data
    return {
        "nodes": nodes_data,
        "edges": edges_data
    }

def create_sample_graph():
    """Create a sample graph for demonstration purposes"""
    
    # Check if we already have nodes
    if Node.query.count() > 0:
        return
    
    # Sample concepts related to programming and AI
    concepts = [
        "Runtime Polymorphism",
        "Compile time polymorphism",
        "Method Overloading",
        "Overriding",
        "Memory allocation",
        "Accessing through heap stack"
    ]
    
    # Create nodes
    nodes = []
    for concept in concepts:
        node = Node(label=concept)
        db.session.add(node)
        db.session.flush()
        nodes.append(node)
    
    # Create edges (connections between concepts)
    edges = [
        (0, 1, 0.8),  # Runtime Polymorphism - Compile time polymorphism
        (1, 2, 0.7),  # Compile time polymorphism - Method Overloading
        (0, 3, 0.6),  # Runtime Polymorphism - Overriding
        (0, 4, 0.5),  # Runtime Polymorphism - Memory allocation
        (4, 5, 0.4),  # Memory allocation - Accessing through heap stack
    ]
    
    for source_idx, target_idx, weight in edges:
        edge = Edge(
            source_id=nodes[source_idx].id,
            target_id=nodes[target_idx].id,
            weight=weight
        )
        db.session.add(edge)
    
    # Commit changes
    db.session.commit() 