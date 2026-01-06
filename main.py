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


def check_files(model_path: str, dataset_path: str) -> bool:
    """
    Check if required files exist.
    
    Args:
        model_path: Path to the model file
        dataset_path: Path to the dataset file
        
    Returns:
        True if all files exist, False otherwise
    """
    issues = []
    
    if not os.path.exists(model_path):
        issues.append(f"Model file not found: {model_path}")
        issues.append(f"  Please download a GGUF model (e.g., Mistral 7B Instruct Q4)")
        issues.append(f"  Example: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
    
    if not os.path.exists(dataset_path):
        issues.append(f"Dataset file not found: {dataset_path}")
        issues.append(f"  Please provide an RDF dataset in Turtle format")
        issues.append(f"  The agent will create this file if it doesn't exist")
    
    if issues:
        print("=" * 60)
        print("WARNING: Missing files")
        print("=" * 60)
        for issue in issues:
            print(issue)
        print("=" * 60)
        
        if not os.path.exists(model_path):
            return False
    
    return True


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
  python main.py --model models/mistral-7b-instruct.Q4_K_M.gguf --dataset data/dataset.ttl
  python main.py --iterations 5 --verbose
  python main.py --create-sample-dataset
        """
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='models/mistral-7b-instruct.Q4_K_M.gguf',
        help='Path to the GGUF model file (default: models/mistral-7b-instruct.Q4_K_M.gguf)'
    )
    
    parser.add_argument(
        '--dataset',
        type=str,
        default='data/dataset.ttl',
        help='Path to the RDF dataset file (default: data/dataset.ttl)'
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
    print("=" * 60)
    
    if not check_files(args.model, args.dataset):
        print("\nCannot proceed without required files.")
        print("\nTo create a sample dataset, run:")
        print(f"  python main.py --create-sample-dataset")
        return 1
    
    try:
        agent = AutonomousAgent(
            model_path=args.model,
            dataset_path=args.dataset,
            memory_file=args.memory,
            max_iterations=args.iterations,
            verbose=args.verbose
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
