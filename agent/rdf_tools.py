"""
RDF and SPARQL tools for querying and manipulating knowledge graphs.

Uses rdflib for RDF processing.
"""

from typing import List, Dict, Tuple, Optional, Any
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL
import re


class RDFTools:
    """RDF and SPARQL query tools."""
    
    def __init__(self, dataset_path: str):
        """
        Initialize RDF tools with a dataset.
        
        Args:
            dataset_path: Path to the RDF dataset file (supports .ttl, .rdf, .xml, .n3, .nt formats)
        """
        self.dataset_path = dataset_path
        self.graph = Graph()
        self.insights_namespace = Namespace("http://ontotrain.ai/insights/")
        
        try:
            # Auto-detect format based on file extension
            # rdflib supports: turtle (.ttl), xml (.rdf, .xml), n3 (.n3), ntriples (.nt), etc.
            try:
                self.graph.parse(dataset_path)
                print(f"Loaded RDF dataset from: {dataset_path}")
                print(f"Total triples: {len(self.graph)}")
            except Exception as first_error:
                # If auto-detection fails, try explicit formats
                print(f"Auto-detection failed, trying alternative formats...")
                formats_to_try = ['xml', 'turtle', 'n3', 'nt']
                
                for fmt in formats_to_try:
                    try:
                        self.graph = Graph()  # Reset graph
                        self.graph.parse(dataset_path, format=fmt)
                        print(f"Successfully loaded dataset using format: {fmt}")
                        print(f"Total triples: {len(self.graph)}")
                        break
                    except Exception:
                        continue
                else:
                    # If all formats fail, raise the original error
                    raise first_error
                    
        except FileNotFoundError:
            print(f"Dataset not found at: {dataset_path}")
            print("Starting with empty graph.")
        except Exception as e:
            print(f"Error loading dataset: {e}")
            print("Starting with empty graph.")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics about the RDF graph.
        
        Returns:
            Dictionary with graph statistics
        """
        stats = {
            'total_triples': len(self.graph),
            'total_subjects': len(set(self.graph.subjects())),
            'total_predicates': len(set(self.graph.predicates())),
            'total_objects': len(set(self.graph.objects())),
        }
        
        classes = list(self.graph.subjects(RDF.type, OWL.Class)) + \
                  list(self.graph.subjects(RDF.type, RDFS.Class))
        stats['total_classes'] = len(set(classes))
        
        properties = list(self.graph.subjects(RDF.type, RDF.Property)) + \
                     list(self.graph.subjects(RDF.type, OWL.ObjectProperty)) + \
                     list(self.graph.subjects(RDF.type, OWL.DatatypeProperty))
        stats['total_properties'] = len(set(properties))
        
        return stats
    
    def get_classes(self, limit: int = 20) -> List[str]:
        """
        Get all classes in the graph.
        
        Args:
            limit: Maximum number of classes to return
            
        Returns:
            List of class URIs
        """
        classes = set()
        
        for s in self.graph.subjects(RDF.type, OWL.Class):
            classes.add(str(s))
        for s in self.graph.subjects(RDF.type, RDFS.Class):
            classes.add(str(s))
        
        for s, p, o in self.graph:
            if p == RDF.type:
                classes.add(str(o))
        
        return sorted(list(classes))[:limit]
    
    def get_properties(self, limit: int = 20) -> List[str]:
        """
        Get all properties in the graph.
        
        Args:
            limit: Maximum number of properties to return
            
        Returns:
            List of property URIs
        """
        properties = set()
        
        for s in self.graph.subjects(RDF.type, RDF.Property):
            properties.add(str(s))
        for s in self.graph.subjects(RDF.type, OWL.ObjectProperty):
            properties.add(str(s))
        for s in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
            properties.add(str(s))
        
        for s, p, o in self.graph:
            properties.add(str(p))
        
        return sorted(list(properties))[:limit]
    
    def execute_sparql(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Execute a SPARQL query.
        
        Args:
            query: SPARQL query string
            limit: Maximum number of results to return
            
        Returns:
            List of result bindings
        """
        try:
            if 'LIMIT' not in query.upper():
                query = query.strip()
                query += f'\nLIMIT {limit}'
            
            results = self.graph.query(query)
            
            output = []
            for row in results:
                binding = {}
                for var in results.vars:
                    value = row[var]
                    binding[str(var)] = str(value) if value else ""
                output.append(binding)
            
            return output
        except Exception as e:
            return [{'error': f"Query failed: {str(e)}"}]
    
    def get_class_instances(self, class_uri: str, limit: int = 10) -> List[str]:
        """
        Get instances of a specific class.
        
        Args:
            class_uri: URI of the class
            limit: Maximum number of instances to return
            
        Returns:
            List of instance URIs
        """
        query = f"""
        SELECT ?instance WHERE {{
            ?instance a <{class_uri}> .
        }} LIMIT {limit}
        """
        
        results = self.execute_sparql(query, limit)
        return [r.get('instance', '') for r in results if 'instance' in r]
    
    def get_property_values(self, subject_uri: str, property_uri: str, limit: int = 10) -> List[str]:
        """
        Get values of a property for a subject.
        
        Args:
            subject_uri: URI of the subject
            property_uri: URI of the property
            limit: Maximum number of values to return
            
        Returns:
            List of property values
        """
        query = f"""
        SELECT ?value WHERE {{
            <{subject_uri}> <{property_uri}> ?value .
        }} LIMIT {limit}
        """
        
        results = self.execute_sparql(query, limit)
        return [r.get('value', '') for r in results if 'value' in r]
    
    def discover_patterns(self) -> List[Dict[str, Any]]:
        """
        Discover common patterns in the graph.
        
        Returns:
            List of discovered patterns
        """
        patterns = []
        
        predicate_counts = {}
        for s, p, o in self.graph:
            p_str = str(p)
            predicate_counts[p_str] = predicate_counts.get(p_str, 0) + 1
        
        top_predicates = sorted(predicate_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for pred, count in top_predicates:
            patterns.append({
                'type': 'frequent_predicate',
                'predicate': pred,
                'count': count
            })
        
        return patterns
    
    def add_insight_triple(self, subject: str, predicate: str, obj: str) -> None:
        """
        Add a new insight triple to the graph.
        
        Args:
            subject: Subject URI or string
            predicate: Predicate URI or string
            obj: Object URI or string
        """
        if not subject.startswith('http'):
            subject = self.insights_namespace[self._make_safe_uri(subject)]
        else:
            subject = URIRef(subject)
        
        if not predicate.startswith('http'):
            predicate = self.insights_namespace[self._make_safe_uri(predicate)]
        else:
            predicate = URIRef(predicate)
        
        if not obj.startswith('http'):
            obj = Literal(obj)
        else:
            obj = URIRef(obj)
        
        self.graph.add((subject, predicate, obj))
        print(f"Added insight triple: {subject} {predicate} {obj}")
    
    def save_graph(self, output_path: Optional[str] = None) -> None:
        """
        Save the graph to a file.
        
        Args:
            output_path: Path to save the graph (defaults to dataset_path)
        """
        path = output_path or self.dataset_path
        
        # Auto-detect format based on file extension
        # If the file extension is recognized by rdflib, it will use that format
        # Otherwise, default to turtle
        try:
            self.graph.serialize(destination=path)
        except Exception:
            # Fallback to turtle format if auto-detection fails
            self.graph.serialize(destination=path, format='turtle')
        
        print(f"Graph saved to: {path}")
    
    def _make_safe_uri(self, text: str) -> str:
        """
        Convert text to a safe URI fragment.
        
        Args:
            text: Text to convert
            
        Returns:
            Safe URI fragment
        """
        safe = re.sub(r'[^a-zA-Z0-9_-]', '_', text)
        safe = re.sub(r'_+', '_', safe)
        return safe.strip('_')
    
    def summarize_graph(self) -> str:
        """
        Generate a human-readable summary of the graph.
        
        Returns:
            Summary string
        """
        stats = self.get_statistics()
        classes = self.get_classes(limit=5)
        properties = self.get_properties(limit=5)
        
        summary = f"""RDF Graph Summary:
- Total triples: {stats['total_triples']}
- Unique subjects: {stats['total_subjects']}
- Unique predicates: {stats['total_predicates']}
- Unique objects: {stats['total_objects']}
- Classes: {stats['total_classes']}
- Properties: {stats['total_properties']}

Sample Classes (top 5):
{chr(10).join(f'  - {c}' for c in classes[:5])}

Sample Properties (top 5):
{chr(10).join(f'  - {p}' for p in properties[:5])}
"""
        return summary
