#!/usr/bin/env python3
"""
OntoTrain - Autonomous RDF AI Agent

Main entry point for running the autonomous agent.
"""

import argparse
import os
import sys
from pathlib import Path
from agent.agent import AutonomousAgent


def check_ollama_available() -> bool:
    """
    Check if Ollama is available.
    
    Returns:
        True if Ollama is accessible, False otherwise
    """
    try:
        import ollama
        ollama.list()
        return True
    except Exception as e:
        print("=" * 60)
        print("ERROR: Ollama is not available")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nPlease make sure:")
        print("1. Ollama is installed: https://ollama.ai")
        print("2. Ollama service is running: 'ollama serve'")
        print("=" * 60)
        return False


def create_sample_dataset(dataset_path: str) -> None:
    """
    Create a sample RDF dataset for testing.
    
    Args:
        dataset_path: Path where to create the dataset
    """
    os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
    
    sample_ttl = """@prefix ex: <http://example.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

ex:Person rdf:type owl:Class ;
    rdfs:label "Person" ;
    rdfs:comment "A human being" .

ex:Organization rdf:type owl:Class ;
    rdfs:label "Organization" ;
    rdfs:comment "A group or company" .

ex:name rdf:type owl:DatatypeProperty ;
    rdfs:label "name" ;
    rdfs:domain ex:Person ;
    rdfs:range rdfs:Literal .

ex:worksFor rdf:type owl:ObjectProperty ;
    rdfs:label "works for" ;
    rdfs:domain ex:Person ;
    rdfs:range ex:Organization .

ex:Alice rdf:type ex:Person ;
    ex:name "Alice Smith" ;
    ex:worksFor ex:TechCorp .

ex:Bob rdf:type ex:Person ;
    ex:name "Bob Johnson" ;
    ex:worksFor ex:TechCorp .

ex:Charlie rdf:type ex:Person ;
    ex:name "Charlie Brown" ;
    ex:worksFor ex:DataInc .

ex:TechCorp rdf:type ex:Organization ;
    ex:name "TechCorp Inc." .

ex:DataInc rdf:type ex:Organization ;
    ex:name "Data Inc." .
"""
    
    with open(dataset_path, 'w') as f:
        f.write(sample_ttl)
    
    print(f"Created sample dataset at: {dataset_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OntoTrain - Autonomous RDF AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python main.py
  python main.py --model mistral --dataset data/dataset.ttl
  python main.py --model llama2 --iterations 5 --verbose
  python main.py --create-sample-dataset
  
Available Ollama models: mistral, llama2, codellama, etc.
List models: ollama list
Pull a model: ollama pull mistral
        """
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='mistral',
        help='Name of the Ollama model to use (default: mistral)'
    )
    
    parser.add_argument(
        '--dataset',
        type=str,
        default='data/dataset.ttl',
        help='Path to the RDF dataset file - supports .ttl, .rdf, .xml, .n3, .nt (default: data/dataset.ttl)'
    )
    
    parser.add_argument(
        '--memory',
        type=str,
        default='data/agent_memory.json',
        help='Path to the agent memory file (default: data/agent_memory.json)'
    )
    
    parser.add_argument(
        '--iterations',
        type=int,
        default=10,
        help='Maximum number of agent loop iterations (default: 10)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--create-sample-dataset',
        action='store_true',
        help='Create a sample RDF dataset and exit'
    )
    
    parser.add_argument(
        '--goal',
        type=str,
        default=None,
        help='Exploration goal for the agent (e.g., "Find all person entities and their relationships")'
    )
    
    args = parser.parse_args()
    
    if args.create_sample_dataset:
        create_sample_dataset(args.dataset)
        print("\nSample dataset created successfully!")
        print(f"You can now run the agent with:")
        print(f"  python main.py --model {args.model}")
        return 0
    
    print("=" * 60)
    print("OntoTrain - Autonomous RDF AI Agent")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Dataset: {args.dataset}")
    print(f"Memory: {args.memory}")
    print(f"Max Iterations: {args.iterations}")
    print(f"Verbose: {args.verbose}")
    if args.goal:
        print(f"Goal: {args.goal}")
    print("=" * 60)
    
    if not check_ollama_available():
        return 1
    
    if not os.path.exists(args.dataset):
        print("\nDataset file not found!")
        print(f"  File: {args.dataset}")
        print("\nTo create a sample dataset, run:")
        print(f"  python main.py --create-sample-dataset")
        return 1
    
    try:
        agent = AutonomousAgent(
            model_name=args.model,
            dataset_path=args.dataset,
            memory_file=args.memory,
            max_iterations=args.iterations,
            verbose=args.verbose,
            goal=args.goal
        )
        
        agent.run()
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\nAgent interrupted by user.")
        return 130
    
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
