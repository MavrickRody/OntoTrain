"""
Local LLM loader and inference module.

Uses llama-cpp-python for running GGUF models locally.
"""

import os
from typing import Optional, Dict, Any
from llama_cpp import Llama


class LocalLLM:
    """Local LLM wrapper using llama-cpp-python."""
    
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 4096,
        n_threads: int = 4,
        n_gpu_layers: int = 0,
        temperature: float = 0.7,
        max_tokens: int = 512,
        verbose: bool = False
    ):
        """
        Initialize the local LLM.
        
        Args:
            model_path: Path to the GGUF model file
            n_ctx: Context window size
            n_threads: Number of CPU threads to use
            n_gpu_layers: Number of layers to offload to GPU (0 for CPU only)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            verbose: Enable verbose output
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at: {model_path}")
        
        self.model_path = model_path
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        print(f"Loading model from: {model_path}")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers,
            verbose=verbose
        )
        print("Model loaded successfully!")
    
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
            stop: List of stop sequences
            
        Returns:
            Generated text
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        response = self.llm(
            prompt,
            temperature=temp,
            max_tokens=max_tok,
            stop=stop or [],
            echo=False
        )
        
        return response['choices'][0]['text'].strip()
    
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
