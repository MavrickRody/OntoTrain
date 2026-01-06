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
    
    def explore_entity(self, entity_uri: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Explore all properties and relationships of a specific entity.
        
        Args:
            entity_uri: URI of the entity to explore
            max_depth: Maximum depth for relationship traversal
            
        Returns:
            Dictionary containing entity information
        """
        entity = URIRef(entity_uri) if not isinstance(entity_uri, URIRef) else entity_uri
        
        result = {
            'uri': str(entity),
            'outgoing': [],
            'incoming': [],
            'types': []
        }
        
        # Get types
        for o in self.graph.objects(entity, RDF.type):
            result['types'].append(str(o))
        
        # Get outgoing relationships
        for p, o in self.graph.predicate_objects(entity):
            result['outgoing'].append({
                'predicate': str(p),
                'object': str(o)
            })
        
        # Get incoming relationships
        for s, p in self.graph.subject_predicates(entity):
            result['incoming'].append({
                'subject': str(s),
                'predicate': str(p)
            })
        
        return result
    
    def find_connected_entities(self, entity_uri: str, max_hops: int = 2) -> List[str]:
        """
        Find entities connected to a given entity within max_hops.
        
        Args:
            entity_uri: Starting entity URI
            max_hops: Maximum number of hops to traverse
            
        Returns:
            List of connected entity URIs
        """
        entity = URIRef(entity_uri) if not isinstance(entity_uri, URIRef) else entity_uri
        visited = set()
        current_level = {entity}
        
        for _ in range(max_hops):
            next_level = set()
            for ent in current_level:
                if ent in visited:
                    continue
                visited.add(ent)
                
                # Add connected entities (both directions)
                for o in self.graph.objects(ent):
                    if isinstance(o, URIRef):
                        next_level.add(o)
                for s in self.graph.subjects(object=ent):
                    if isinstance(s, URIRef):
                        next_level.add(s)
            
            current_level = next_level
        
        return [str(e) for e in visited if e != entity]
    
    def extract_subgraph(self, entity_uris: List[str]) -> Graph:
        """
        Extract a subgraph containing specified entities and their connections.
        
        Args:
            entity_uris: List of entity URIs to include
            
        Returns:
            New Graph containing the subgraph
        """
        subgraph = Graph()
        entities = [URIRef(uri) if not isinstance(uri, URIRef) else uri for uri in entity_uris]
        entity_set = set(entities)
        
        for s, p, o in self.graph:
            if s in entity_set or o in entity_set:
                subgraph.add((s, p, o))
        
        return subgraph
    
    def find_entity_clusters(self, min_cluster_size: int = 3) -> List[Dict[str, Any]]:
        """
        Find clusters of highly connected entities.
        
        Args:
            min_cluster_size: Minimum number of entities in a cluster
            
        Returns:
            List of clusters with their entities
        """
        # Simple clustering based on shared predicates
        predicate_groups = {}
        
        for s, p, o in self.graph:
            p_str = str(p)
            if p_str not in predicate_groups:
                predicate_groups[p_str] = set()
            if isinstance(s, URIRef):
                predicate_groups[p_str].add(str(s))
            if isinstance(o, URIRef):
                predicate_groups[p_str].add(str(o))
        
        clusters = []
        for pred, entities in predicate_groups.items():
            if len(entities) >= min_cluster_size:
                clusters.append({
                    'predicate': pred,
                    'size': len(entities),
                    'entities': list(entities)[:10]  # Limit to first 10 for readability
                })
        
        return sorted(clusters, key=lambda x: x['size'], reverse=True)[:10]
    
    def find_hierarchies(self) -> List[Dict[str, Any]]:
        """
        Identify hierarchical relationships in the graph.
        
        Returns:
            List of hierarchical structures found
        """
        hierarchies = []
        hierarchy_predicates = [
            RDFS.subClassOf,
            RDFS.subPropertyOf,
            URIRef("http://www.w3.org/2004/02/skos/core#broader"),
            URIRef("http://www.w3.org/2004/02/skos/core#narrower")
        ]
        
        for pred in hierarchy_predicates:
            hierarchy = {'predicate': str(pred), 'relationships': []}
            for s, p, o in self.graph.triples((None, pred, None)):
                hierarchy['relationships'].append({
                    'child': str(s),
                    'parent': str(o)
                })
            
            if hierarchy['relationships']:
                hierarchies.append(hierarchy)
        
        return hierarchies
    
    def validate_graph(self) -> Dict[str, Any]:
        """
        Validate the RDF graph for common issues.
        
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        # Check for blank nodes
        blank_count = sum(1 for s in self.graph.subjects() if not isinstance(s, URIRef))
        if blank_count > 0:
            warnings.append(f"Found {blank_count} blank nodes")
        
        # Check for undefined classes
        for s, p, o in self.graph.triples((None, RDF.type, None)):
            if isinstance(o, URIRef):
                # Check if class is defined
                class_defined = any(self.graph.triples((o, RDF.type, OWL.Class))) or \
                               any(self.graph.triples((o, RDF.type, RDFS.Class)))
                if not class_defined and str(o) not in ['http://www.w3.org/2002/07/owl#Thing']:
                    warnings.append(f"Potentially undefined class: {o}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues[:10],  # Limit to first 10
            'warnings': warnings[:10],
            'total_issues': len(issues),
            'total_warnings': len(warnings)
        }
    
    def export_to_format(self, output_path: str, format: str = 'json-ld') -> bool:
        """
        Export graph to various formats.
        
        Args:
            output_path: Path to save the exported file
            format: Export format (json-ld, n3, nt, xml, turtle)
            
        Returns:
            True if successful
        """
        try:
            self.graph.serialize(destination=output_path, format=format)
            print(f"Exported graph to {output_path} in {format} format")
            return True
        except Exception as e:
            print(f"Error exporting graph: {e}")
            return False
    
    def generate_custom_sparql(self, description: str) -> str:
        """
        Generate a SPARQL query template based on description.
        This is a simple template generator - could be enhanced with LLM.
        
        Args:
            description: Description of what to query
            
        Returns:
            SPARQL query string
        """
        # Simple template based on keywords
        desc_lower = description.lower()
        
        if 'class' in desc_lower or 'type' in desc_lower:
            return """
            SELECT DISTINCT ?class (COUNT(?instance) as ?count) WHERE {
                ?instance a ?class .
            }
            GROUP BY ?class
            ORDER BY DESC(?count)
            LIMIT 20
            """
        elif 'property' in desc_lower or 'predicate' in desc_lower:
            return """
            SELECT DISTINCT ?property (COUNT(*) as ?count) WHERE {
                ?s ?property ?o .
            }
            GROUP BY ?property
            ORDER BY DESC(?count)
            LIMIT 20
            """
        elif 'connect' in desc_lower or 'relationship' in desc_lower:
            return """
            SELECT ?s ?p ?o WHERE {
                ?s ?p ?o .
            }
            LIMIT 100
            """
        else:
            return """
            SELECT ?s ?p ?o WHERE {
                ?s ?p ?o .
            }
            LIMIT 20
            """
    
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
