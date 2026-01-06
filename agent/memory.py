"""
Memory and learning layer for the autonomous agent.

Maintains a record of actions, observations, and insights.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os


class AgentMemory:
    """Memory and learning layer for the agent."""
    
    def __init__(self, memory_file: str = "data/agent_memory.json"):
        """
        Initialize the agent memory.
        
        Args:
            memory_file: Path to the memory persistence file
        """
        self.memory_file = memory_file
        self.short_term_memory: List[Dict[str, Any]] = []
        self.insights: List[Dict[str, Any]] = []
        self.action_history: List[Dict[str, Any]] = []
        
        self._load_memory()
    
    def _load_memory(self) -> None:
        """Load memory from disk if it exists."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.short_term_memory = data.get('short_term_memory', [])
                    self.insights = data.get('insights', [])
                    self.action_history = data.get('action_history', [])
                print(f"Loaded memory from: {self.memory_file}")
            except Exception as e:
                print(f"Error loading memory: {e}")
                print("Starting with fresh memory.")
    
    def save_memory(self) -> None:
        """Save memory to disk."""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            
            data = {
                'short_term_memory': self.short_term_memory,
                'insights': self.insights,
                'action_history': self.action_history,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Memory saved to: {self.memory_file}")
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def add_thought(self, thought: str, iteration: int) -> None:
        """
        Record a thought/reasoning step.
        
        Args:
            thought: The reasoning text
            iteration: Current iteration number
        """
        entry = {
            'type': 'thought',
            'content': thought,
            'iteration': iteration,
            'timestamp': datetime.now().isoformat()
        }
        self.short_term_memory.append(entry)
    
    def add_action(self, action: str, parameters: Optional[Dict[str, Any]], iteration: int) -> None:
        """
        Record an action taken.
        
        Args:
            action: Name of the action
            parameters: Action parameters
            iteration: Current iteration number
        """
        entry = {
            'type': 'action',
            'action': action,
            'parameters': parameters or {},
            'iteration': iteration,
            'timestamp': datetime.now().isoformat()
        }
        self.short_term_memory.append(entry)
        self.action_history.append(entry)
    
    def add_observation(self, observation: str, iteration: int) -> None:
        """
        Record an observation/result.
        
        Args:
            observation: The observation text
            iteration: Current iteration number
        """
        entry = {
            'type': 'observation',
            'content': observation,
            'iteration': iteration,
            'timestamp': datetime.now().isoformat()
        }
        self.short_term_memory.append(entry)
    
    def add_insight(self, insight: str, source: str, iteration: int) -> None:
        """
        Record a learned insight.
        
        Args:
            insight: The insight text
            source: Source of the insight
            iteration: Current iteration number
        """
        entry = {
            'insight': insight,
            'source': source,
            'iteration': iteration,
            'timestamp': datetime.now().isoformat()
        }
        self.insights.append(entry)
    
    def get_recent_history(self, n: int = 5) -> str:
        """
        Get recent history as a formatted string.
        
        Args:
            n: Number of recent entries to include
            
        Returns:
            Formatted history string
        """
        recent = self.short_term_memory[-n:] if len(self.short_term_memory) > n else self.short_term_memory
        
        history_parts = []
        for entry in recent:
            if entry['type'] == 'thought':
                history_parts.append(f"Thought: {entry['content']}")
            elif entry['type'] == 'action':
                history_parts.append(f"Action: {entry['action']}")
            elif entry['type'] == 'observation':
                history_parts.append(f"Observation: {entry['content'][:200]}...")
        
        return "\n".join(history_parts) if history_parts else "No recent history"
    
    def get_all_insights(self) -> List[Dict[str, Any]]:
        """
        Get all learned insights.
        
        Returns:
            List of insight dictionaries with metadata
        """
        return self.insights
    
    def get_action_counts(self) -> Dict[str, int]:
        """
        Get counts of each action taken.
        
        Returns:
            Dictionary mapping action names to counts
        """
        counts = {}
        for entry in self.action_history:
            action = entry['action']
            counts[action] = counts.get(action, 0) + 1
        return counts
    
    def summarize_session(self) -> str:
        """
        Generate a summary of the current session.
        
        Returns:
            Summary string
        """
        action_counts = self.get_action_counts()
        total_insights = len(self.insights)
        
        summary = f"""Session Summary:
- Total actions taken: {len(self.action_history)}
- Total insights generated: {total_insights}
- Actions breakdown:
"""
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
            summary += f"  - {action}: {count}\n"
        
        if total_insights > 0:
            summary += "\nRecent Insights:\n"
            for insight_entry in self.insights[-3:]:
                summary += f"  - {insight_entry['insight']}\n"
        
        return summary
    
    def clear_short_term(self) -> None:
        """Clear short-term memory (keeps insights and action history)."""
        self.short_term_memory = []
    
    def reset_all(self) -> None:
        """Reset all memory (use with caution)."""
        self.short_term_memory = []
        self.insights = []
        self.action_history = []
