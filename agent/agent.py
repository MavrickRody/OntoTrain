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
        verbose: bool = True
    ):
        """
        Initialize the autonomous agent.
        
        Args:
            model_name: Name of the Ollama model (e.g., 'mistral', 'llama2')
            dataset_path: Path to the RDF dataset
            memory_file: Path to memory persistence file
            max_iterations: Maximum number of agent loop iterations
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.max_iterations = max_iterations
        
        print("=" * 60)
        print("Initializing Autonomous RDF AI Agent")
        print("=" * 60)
        
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
            'summarize_graph'
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
        
        context = f"""You are an autonomous AI agent exploring an RDF knowledge graph.

Graph Summary:
{graph_summary}

Recent History:
{recent_history}

Iteration: {iteration}/{self.max_iterations}
"""
        
        task = "What should I explore or analyze next to gain valuable insights from this RDF graph?"
        
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
        
        subject = f"insight_{iteration}"
        predicate = "hasContent"
        self.rdf_tools.add_insight_triple(subject, predicate, insight)
        
        if self.verbose:
            print(f"Insight: {insight}")
    
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
        
        self.rdf_tools.save_graph()
        
        self.memory.save_memory()
        
        print("\n" + self.memory.summarize_session())
        
        print("\n" + "=" * 60)
        print("Agent session completed successfully!")
        print("=" * 60)
