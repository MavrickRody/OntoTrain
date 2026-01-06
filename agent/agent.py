"""
Autonomous RDF AI Agent.

Implements the Thought → Action → Observation → Learning loop.
"""

from typing import Optional, Dict, Any
import time
from agent.llm import LocalLLM
from agent.rdf_tools import RDFTools
from agent.memory import AgentMemory


class AutonomousAgent:
    """Autonomous RDF AI Agent with reasoning loop."""
    
    def __init__(
        self,
        model_name: str,
        dataset_path: str,
        memory_file: str = "data/agent_memory.json",
        max_iterations: int = 10,
        verbose: bool = True,
        goal: Optional[str] = None
    ):
        """
        Initialize the autonomous agent.
        
        Args:
            model_name: Name of the Ollama model (e.g., 'mistral', 'llama2')
            dataset_path: Path to the RDF dataset
            memory_file: Path to memory persistence file
            max_iterations: Maximum number of agent loop iterations
            verbose: Enable verbose output
            goal: Optional exploration goal for the agent
        """
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.goal = goal or "Explore and understand the RDF graph structure"
        self.context = []  # Store important findings across iterations
        
        print("=" * 60)
        print("Initializing Autonomous RDF AI Agent")
        print("=" * 60)
        if self.goal:
            print(f"Goal: {self.goal}")
        
        self.llm = LocalLLM(
            model_name=model_name,
            temperature=0.7,
            verbose=False
        )
        
        self.rdf_tools = RDFTools(dataset_path=dataset_path)
        self.memory = AgentMemory(memory_file=memory_file)
        
        self.available_actions = [
            'inspect_statistics',
            'list_classes',
            'list_properties',
            'query_sparql',
            'discover_patterns',
            'summarize_graph',
            'explore_entity',
            'find_clusters',
            'find_hierarchies',
            'validate_graph',
            'custom_sparql_query'
        ]
        
        print("\nAgent initialized successfully!")
        print("=" * 60)
    
    def run(self) -> None:
        """Execute the autonomous agent loop."""
        print("\n" + "=" * 60)
        print("Starting Autonomous Agent Loop")
        print("=" * 60)
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{'=' * 60}")
            print(f"Iteration {iteration}/{self.max_iterations}")
            print("=" * 60)
            
            thought = self._think(iteration)
            
            action = self._decide_action(thought, iteration)
            
            observation = self._execute_action(action, iteration)
            
            self._learn(observation, iteration)
            
            if not self._should_continue(iteration):
                print("\n" + "=" * 60)
                print("Agent has decided to stop.")
                print("=" * 60)
                break
            
            time.sleep(0.5)
        
        self._finalize()
    
    def _think(self, iteration: int) -> str:
        """
        Thought phase: Generate reasoning about current state.
        
        Args:
            iteration: Current iteration number
            
        Returns:
            Thought/reasoning text
        """
        print("\n[THOUGHT PHASE]")
        
        graph_summary = self.rdf_tools.summarize_graph()
        recent_history = self.memory.get_recent_history(n=3)
        
        # Build context-aware prompt
        context_info = ""
        if self.context:
            context_info = f"\n\nKey Findings So Far:\n" + "\n".join(f"- {c}" for c in self.context[-5:])
        
        context = f"""You are an autonomous AI agent exploring an RDF knowledge graph.

Goal: {self.goal}

Graph Summary:
{graph_summary}

Recent History:
{recent_history}
{context_info}

Iteration: {iteration}/{self.max_iterations}

Available actions: {', '.join(self.available_actions)}
"""
        
        task = "Based on your goal and what you've learned, what should you do next to make progress?"
        
        thought = self.llm.think(context, task)
        
        self.memory.add_thought(thought, iteration)
        
        if self.verbose:
            print(f"Thought: {thought}")
        
        return thought
    
    def _decide_action(self, thought: str, iteration: int) -> str:
        """
        Action phase: Decide which action to take.
        
        Args:
            thought: Current reasoning
            iteration: Current iteration number
            
        Returns:
            Selected action name
        """
        print("\n[ACTION PHASE]")
        
        action = self.llm.decide_action(thought, self.available_actions)
        
        if action not in self.available_actions:
            action = self.available_actions[0]
        
        if self.verbose:
            print(f"Selected Action: {action}")
        
        return action
    
    def _execute_action(self, action: str, iteration: int) -> str:
        """
        Observation phase: Execute action and observe results.
        
        Args:
            action: Action to execute
            iteration: Current iteration number
            
        Returns:
            Observation text
        """
        print("\n[OBSERVATION PHASE]")
        
        self.memory.add_action(action, None, iteration)
        
        observation = ""
        
        if action == 'inspect_statistics':
            stats = self.rdf_tools.get_statistics()
            observation = f"Graph Statistics:\n"
            for key, value in stats.items():
                observation += f"  {key}: {value}\n"
        
        elif action == 'list_classes':
            classes = self.rdf_tools.get_classes(limit=10)
            observation = f"Found {len(classes)} classes:\n"
            for cls in classes:
                observation += f"  - {cls}\n"
        
        elif action == 'list_properties':
            properties = self.rdf_tools.get_properties(limit=10)
            observation = f"Found {len(properties)} properties:\n"
            for prop in properties:
                observation += f"  - {prop}\n"
        
        elif action == 'query_sparql':
            query = """
            SELECT ?s ?p ?o WHERE {
                ?s ?p ?o .
            }
            """
            results = self.rdf_tools.execute_sparql(query, limit=5)
            observation = f"SPARQL Query Results ({len(results)} rows):\n"
            for i, result in enumerate(results, 1):
                observation += f"  {i}. {result}\n"
        
        elif action == 'discover_patterns':
            patterns = self.rdf_tools.discover_patterns()
            observation = f"Discovered {len(patterns)} patterns:\n"
            for pattern in patterns:
                observation += f"  - {pattern['type']}: {pattern.get('predicate', 'N/A')} (count: {pattern.get('count', 0)})\n"
        
        elif action == 'summarize_graph':
            observation = self.rdf_tools.summarize_graph()
        
        elif action == 'explore_entity':
            # Pick a random entity to explore
            classes = self.rdf_tools.get_classes(limit=5)
            if classes:
                entity_info = self.rdf_tools.explore_entity(classes[0])
                observation = f"Entity Exploration: {entity_info['uri']}\n"
                observation += f"Types: {', '.join(entity_info['types'][:5])}\n"
                observation += f"Outgoing relationships: {len(entity_info['outgoing'])}\n"
                observation += f"Incoming relationships: {len(entity_info['incoming'])}\n"
                if entity_info['outgoing']:
                    observation += "Sample outgoing:\n"
                    for rel in entity_info['outgoing'][:3]:
                        observation += f"  - {rel['predicate']} -> {rel['object']}\n"
            else:
                observation = "No entities found to explore"
        
        elif action == 'find_clusters':
            clusters = self.rdf_tools.find_entity_clusters()
            observation = f"Found {len(clusters)} entity clusters:\n"
            for cluster in clusters[:5]:
                observation += f"  - Predicate: {cluster['predicate']}, Size: {cluster['size']}\n"
                observation += f"    Sample entities: {', '.join(cluster['entities'][:3])}\n"
        
        elif action == 'find_hierarchies':
            hierarchies = self.rdf_tools.find_hierarchies()
            observation = f"Found {len(hierarchies)} hierarchical structures:\n"
            for hier in hierarchies:
                observation += f"  - Predicate: {hier['predicate']}, Relationships: {len(hier['relationships'])}\n"
                for rel in hier['relationships'][:3]:
                    observation += f"    {rel['child']} -> {rel['parent']}\n"
        
        elif action == 'validate_graph':
            validation = self.rdf_tools.validate_graph()
            observation = f"Graph Validation Results:\n"
            observation += f"Valid: {validation['valid']}\n"
            observation += f"Issues: {validation['total_issues']}\n"
            observation += f"Warnings: {validation['total_warnings']}\n"
            if validation['warnings']:
                observation += "Sample warnings:\n"
                for warning in validation['warnings'][:3]:
                    observation += f"  - {warning}\n"
        
        elif action == 'custom_sparql_query':
            # Generate a query for finding class distributions
            query = self.rdf_tools.generate_custom_sparql("class distribution")
            results = self.rdf_tools.execute_sparql(query, limit=10)
            observation = f"Custom SPARQL Results ({len(results)} rows):\n"
            for i, result in enumerate(results, 1):
                observation += f"  {i}. {result}\n"
        
        else:
            observation = f"Unknown action: {action}"
        
        self.memory.add_observation(observation, iteration)
        
        if self.verbose:
            print(f"Observation:\n{observation[:500]}...")
        
        return observation
    
    def _learn(self, observation: str, iteration: int) -> None:
        """
        Learning phase: Generate and persist insights.
        
        Args:
            observation: Current observation
            iteration: Current iteration number
        """
        print("\n[LEARNING PHASE]")
        
        insight = self.llm.generate_insight(observation)
        
        self.memory.add_insight(insight, "agent_loop", iteration)
        
        # Add significant insights to context
        if len(insight) > 50:  # Only add substantial insights
            self.context.append(insight[:200])  # Truncate for context window
        
        subject = f"insight_{iteration}"
        predicate = "hasContent"
        self.rdf_tools.add_insight_triple(subject, predicate, insight)
        
        # Add confidence scoring
        confidence = self._score_insight_confidence(observation, insight)
        confidence_pred = "hasConfidence"
        self.rdf_tools.add_insight_triple(subject, confidence_pred, str(confidence))
        
        if self.verbose:
            print(f"Insight: {insight}")
            print(f"Confidence: {confidence:.2f}")
    
    def _score_insight_confidence(self, observation: str, insight: str) -> float:
        """
        Score the confidence of an insight based on observation quality.
        
        Args:
            observation: The observation data
            insight: The generated insight
            
        Returns:
            Confidence score between 0 and 1
        """
        # Simple heuristic-based confidence scoring
        confidence = 0.5  # Base confidence
        
        # More data points increase confidence
        if 'count:' in observation:
            confidence += 0.2
        
        # Specific numbers increase confidence
        if any(char.isdigit() for char in observation):
            confidence += 0.1
        
        # Longer, more detailed insights might be more confident
        if len(insight) > 100:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _should_continue(self, iteration: int) -> bool:
        """
        Decide whether to continue the agent loop.
        
        Args:
            iteration: Current iteration number
            
        Returns:
            True if should continue, False otherwise
        """
        if iteration >= self.max_iterations:
            return False
        
        recent_history = self.memory.get_recent_history(n=5)
        
        should_continue = self.llm.should_continue(
            iteration=iteration,
            max_iterations=self.max_iterations,
            recent_history=recent_history
        )
        
        return should_continue
    
    def _finalize(self) -> None:
        """Finalize the agent session."""
        print("\n" + "=" * 60)
        print("Finalizing Agent Session")
        print("=" * 60)
        
        # Generate and save comprehensive report
        report = self._generate_report()
        report_path = "data/agent_report.md"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"Saved comprehensive report to: {report_path}")
        
        # Export graph in multiple formats
        self.rdf_tools.export_to_format("data/dataset_with_insights.json", "json-ld")
        self.rdf_tools.export_to_format("data/dataset_with_insights.nt", "nt")
        
        self.rdf_tools.save_graph()
        self.memory.save_memory()
        
        print("\n" + self.memory.summarize_session())
        
        print("\n" + "=" * 60)
        print("Agent session completed successfully!")
        print("=" * 60)
    
    def _generate_report(self) -> str:
        """
        Generate a comprehensive exploration report.
        
        Returns:
            Markdown-formatted report
        """
        stats = self.rdf_tools.get_statistics()
        validation = self.rdf_tools.validate_graph()
        insights = self.memory.get_all_insights()
        
        report = f"""# OntoTrain RDF Exploration Report

## Exploration Goal
{self.goal}

## Graph Statistics
- Total Triples: {stats['total_triples']}
- Unique Subjects: {stats['total_subjects']}
- Unique Predicates: {stats['total_predicates']}
- Unique Objects: {stats['total_objects']}
- Total Classes: {stats['total_classes']}
- Total Properties: {stats['total_properties']}

## Validation Results
- Valid: {validation['valid']}
- Issues: {validation['total_issues']}
- Warnings: {validation['total_warnings']}

## Key Findings
"""
        
        for i, ctx in enumerate(self.context, 1):
            report += f"\n{i}. {ctx}\n"
        
        report += f"\n## All Insights ({len(insights)})\n"
        for i, insight in enumerate(insights[-10:], 1):  # Last 10 insights
            report += f"\n### Insight {i}\n"
            report += f"- **Content**: {insight.get('content', 'N/A')}\n"
            report += f"- **Source**: {insight.get('source', 'N/A')}\n"
            report += f"- **Iteration**: {insight.get('iteration', 'N/A')}\n"
        
        report += "\n## Recommendations for Further Exploration\n"
        report += "- Consider using custom SPARQL queries for specific data extraction\n"
        report += "- Explore entity clusters to find groups of related concepts\n"
        report += "- Investigate hierarchical relationships for ontology structure\n"
        
        return report
