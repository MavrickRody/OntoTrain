"""
Local LLM loader and inference module.

Uses Ollama for running models locally via API.
"""

import os
from typing import Optional, Dict, Any
import ollama


class LocalLLM:
    """Local LLM wrapper using Ollama."""
    
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        verbose: bool = False,
        **kwargs
    ):
        """
        Initialize the local LLM with Ollama.
        
        Args:
            model_name: Name of the Ollama model (e.g., 'mistral', 'llama2', 'codellama')
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            verbose: Enable verbose output
            **kwargs: Additional arguments (ignored for Ollama compatibility)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.verbose = verbose
        
        print(f"Connecting to Ollama with model: {model_name}")
        
        try:
            models = ollama.list()
            model_names = [m['name'] for m in models.get('models', [])]
            
            if not any(model_name in name for name in model_names):
                print(f"Warning: Model '{model_name}' not found in Ollama.")
                print(f"Available models: {', '.join(model_names)}")
                print(f"Attempting to pull model '{model_name}'...")
                ollama.pull(model_name)
                print(f"Model '{model_name}' pulled successfully!")
            else:
                print(f"Model '{model_name}' is available!")
        except Exception as e:
            print(f"Warning: Could not verify Ollama model: {e}")
            print("Make sure Ollama is running: 'ollama serve'")
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[list] = None
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            stop: List of stop sequences (not used in Ollama)
            
        Returns:
            Generated text
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'temperature': temp,
                    'num_predict': max_tok,
                }
            )
            
            return response['response'].strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            print("Make sure Ollama is running: 'ollama serve'")
            return f"Error: {str(e)}"
    
    def create_prompt(self, system: str, user: str, template: str = "mistral") -> str:
        """
        Create a formatted prompt for instruction-tuned models.
        
        Args:
            system: System instruction
            user: User query
            template: Prompt template format ('mistral', 'llama2', or 'simple')
            
        Returns:
            Formatted prompt
        """
        if template == "mistral":
            return f"""<s>[INST] {system}

{user} [/INST]"""
        elif template == "llama2":
            return f"""<s>[INST] <<SYS>>
{system}
<</SYS>>

{user} [/INST]"""
        else:
            return f"""{system}

{user}"""
    
    def think(self, context: str, task: str) -> str:
        """
        Generate a thought/reasoning step.
        
        Args:
            context: Current context
            task: Task to reason about
            
        Returns:
            Reasoning output
        """
        system = "You are an analytical AI assistant helping to reason about RDF knowledge graphs."
        user = f"""Context: {context}

Task: {task}

Provide your reasoning:"""
        
        prompt = self.create_prompt(system, user)
        return self.generate(prompt, temperature=0.3)
    
    def decide_action(self, thought: str, available_actions: list) -> str:
        """
        Decide which action to take based on reasoning.
        
        Args:
            thought: Current reasoning
            available_actions: List of available action names
            
        Returns:
            Selected action
        """
        actions_str = "\n".join(f"- {action}" for action in available_actions)
        
        system = "You are an AI agent that selects the most appropriate action."
        user = f"""Reasoning: {thought}

Available actions:
{actions_str}

Select ONE action that best helps accomplish the goal. Respond with only the action name:"""
        
        prompt = self.create_prompt(system, user)
        action = self.generate(prompt, temperature=0.1, max_tokens=50)
        
        for available_action in available_actions:
            if available_action.lower() in action.lower():
                return available_action
        
        return available_actions[0]
    
    def generate_insight(self, observation: str) -> str:
        """
        Generate an insight from an observation.
        
        Args:
            observation: Observation to analyze
            
        Returns:
            Generated insight
        """
        system = "You are an AI that generates concise insights from data."
        user = f"""Observation: {observation}

Generate a concise, factual insight (1-2 sentences):"""
        
        prompt = self.create_prompt(system, user)
        return self.generate(prompt, temperature=0.5, max_tokens=100)
    
    def should_continue(self, iteration: int, max_iterations: int, recent_history: str) -> bool:
        """
        Decide whether to continue the agent loop.
        
        Args:
            iteration: Current iteration number
            max_iterations: Maximum allowed iterations
            recent_history: Recent actions and observations
            
        Returns:
            True if should continue, False otherwise
        """
        if iteration >= max_iterations:
            return False
        
        system = "You are an AI that decides when a task is complete."
        user = f"""Iteration: {iteration}/{max_iterations}

Recent history:
{recent_history}

Has the agent gathered enough useful information? Respond with only 'CONTINUE' or 'STOP':"""
        
        prompt = self.create_prompt(system, user)
        decision = self.generate(prompt, temperature=0.1, max_tokens=10)
        
        return 'continue' in decision.lower()
