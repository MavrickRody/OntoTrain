"""
Visualization utilities for RDF graphs.

Provides functions to visualize graph structures and patterns.
"""

from typing import List, Dict, Any, Optional
from rdflib import Graph, URIRef
import json


class RDFVisualizer:
    """Create visualizations of RDF graphs."""
    
    def __init__(self, graph: Graph):
        """
        Initialize the visualizer.
        
        Args:
            graph: RDFLib graph to visualize
        """
        self.graph = graph
    
    def generate_graph_viz(self, max_nodes: int = 50) -> Dict[str, Any]:
        """
        Generate graph visualization data in a format suitable for visualization libraries.
        
        Args:
            max_nodes: Maximum number of nodes to include
            
        Returns:
            Dictionary with nodes and edges for visualization
        """
        nodes = set()
        edges = []
        
        # Collect nodes and edges
        count = 0
        for s, p, o in self.graph:
            if count >= max_nodes:
                break
            
            if isinstance(s, URIRef):
                nodes.add(str(s))
            if isinstance(o, URIRef):
                nodes.add(str(o))
                edges.append({
                    'source': str(s),
                    'target': str(o),
                    'label': str(p)
                })
            count += 1
        
        return {
            'nodes': [{'id': n, 'label': self._shorten_uri(n)} for n in nodes],
            'edges': edges[:100]  # Limit edges for readability
        }
    
    def generate_class_hierarchy_viz(self) -> Dict[str, Any]:
        """
        Generate a visualization of the class hierarchy.
        
        Returns:
            Tree structure of classes
        """
        from rdflib.namespace import RDFS
        
        hierarchy = {'name': 'Classes', 'children': []}
        visited = set()
        
        # Find top-level classes (those without superclasses)
        for s, p, o in self.graph.triples((None, RDFS.subClassOf, None)):
            if s not in visited:
                node = self._build_class_tree(s, visited)
                if node:
                    hierarchy['children'].append(node)
        
        return hierarchy
    
    def _build_class_tree(self, class_uri: URIRef, visited: set) -> Optional[Dict[str, Any]]:
        """
        Recursively build class hierarchy tree.
        
        Args:
            class_uri: Class URI to start from
            visited: Set of visited classes
            
        Returns:
            Tree node dictionary
        """
        from rdflib.namespace import RDFS
        
        if class_uri in visited:
            return None
        
        visited.add(class_uri)
        node = {
            'name': self._shorten_uri(str(class_uri)),
            'uri': str(class_uri),
            'children': []
        }
        
        # Find subclasses
        for s in self.graph.subjects(RDFS.subClassOf, class_uri):
            child = self._build_class_tree(s, visited)
            if child:
                node['children'].append(child)
        
        return node
    
    def generate_statistics_viz(self) -> Dict[str, Any]:
        """
        Generate data for statistics visualizations.
        
        Returns:
            Dictionary with various statistics for plotting
        """
        from rdflib.namespace import RDF
        
        # Class instance counts
        class_counts = {}
        for s, p, o in self.graph.triples((None, RDF.type, None)):
            class_uri = str(o)
            class_counts[class_uri] = class_counts.get(class_uri, 0) + 1
        
        # Predicate usage counts
        predicate_counts = {}
        for s, p, o in self.graph:
            pred_uri = str(p)
            predicate_counts[pred_uri] = predicate_counts.get(pred_uri, 0) + 1
        
        return {
            'class_distribution': [
                {'class': self._shorten_uri(k), 'count': v}
                for k, v in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            ],
            'predicate_usage': [
                {'predicate': self._shorten_uri(k), 'count': v}
                for k, v in sorted(predicate_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            ]
        }
    
    def export_visualization_data(self, output_path: str) -> bool:
        """
        Export all visualization data to a JSON file.
        
        Args:
            output_path: Path to save the visualization data
            
        Returns:
            True if successful
        """
        try:
            viz_data = {
                'graph': self.generate_graph_viz(),
                'class_hierarchy': self.generate_class_hierarchy_viz(),
                'statistics': self.generate_statistics_viz()
            }
            
            with open(output_path, 'w') as f:
                json.dump(viz_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting visualization data: {e}")
            return False
    
    def _shorten_uri(self, uri: str) -> str:
        """
        Shorten a URI for display.
        
        Args:
            uri: Full URI
            
        Returns:
            Shortened label
        """
        if '#' in uri:
            return uri.split('#')[-1]
        elif '/' in uri:
            return uri.split('/')[-1]
        return uri
    
    def generate_html_report(self, output_path: str) -> bool:
        """
        Generate an interactive HTML visualization report.
        
        Args:
            output_path: Path to save the HTML file
            
        Returns:
            True if successful
        """
        viz_data = self.generate_graph_viz(max_nodes=30)
        stats = self.generate_statistics_viz()
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>RDF Graph Visualization</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .stats {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .node {{ background: #e3f2fd; padding: 10px; margin: 5px; border-radius: 3px; }}
        .edge {{ background: #fff3e0; padding: 5px; margin: 3px; font-size: 12px; }}
        pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>RDF Graph Visualization Report</h1>
    
    <div class="stats">
        <h2>Graph Statistics</h2>
        <p>Total Nodes: {len(viz_data['nodes'])}</p>
        <p>Total Edges: {len(viz_data['edges'])}</p>
    </div>
    
    <div class="stats">
        <h2>Top Classes by Instance Count</h2>
        <ul>
        {''.join(f"<li>{item['class']}: {item['count']}</li>" for item in stats['class_distribution'][:10])}
        </ul>
    </div>
    
    <div class="stats">
        <h2>Top Predicates by Usage</h2>
        <ul>
        {''.join(f"<li>{item['predicate']}: {item['count']}</li>" for item in stats['predicate_usage'][:10])}
        </ul>
    </div>
    
    <div class="stats">
        <h2>Sample Nodes (limited to {len(viz_data['nodes'][:20])})</h2>
        {''.join(f'<div class="node">{node["label"]}</div>' for node in viz_data['nodes'][:20])}
    </div>
    
    <div class="stats">
        <h2>Sample Relationships (limited to 20)</h2>
        {''.join(f'<div class="edge">{edge["source"]} --[{edge["label"]}]--> {edge["target"]}</div>' for edge in viz_data['edges'][:20])}
    </div>
    
    <p><em>For interactive graph visualization, consider using tools like Cytoscape.js or D3.js with the exported JSON data.</em></p>
</body>
</html>
"""
        
        try:
            with open(output_path, 'w') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            return False
