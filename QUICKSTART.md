# OntoTrain Quick Start Guide

Get up and running with OntoTrain in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- 8GB RAM minimum (16GB recommended)
- 5GB free disk space

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/MavrickRody/OntoTrain.git
cd OntoTrain

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Install and Setup Ollama

```bash
# 1. Download and install Ollama from https://ollama.ai
# For macOS/Linux, or use your package manager

# 2. Start Ollama service (in one terminal)
ollama serve

# 3. In another terminal, pull a model
ollama pull mistral

# Alternative models:
# ollama pull llama2
# ollama pull codellama
# ollama pull phi
```

## Create Sample Dataset

```bash
# Generate a sample RDF knowledge graph
python main.py --create-sample-dataset
```

This creates `data/dataset.ttl` with sample data.

## Run the Agent

```bash
# Make sure Ollama is running first (in another terminal):
ollama serve

# Then run the agent
python main.py

# Or run with verbose output
python main.py --verbose

# Or run for fewer iterations
python main.py --iterations 5

# Use a different model
python main.py --model llama2
```

## What Happens?

The agent will:

1. **Connect** to Ollama with your chosen model
2. **Parse** the RDF dataset
3. **Execute** autonomous reasoning loop:
   - **Think**: Reason about what to explore
   - **Act**: Choose and execute an action
   - **Observe**: Collect results
   - **Learn**: Generate and persist insights
4. **Save** updated graph with insights to `data/dataset.ttl`
5. **Persist** memory to `data/agent_memory.json`

## Example Output

```
============================================================
Initializing Autonomous RDF AI Agent
============================================================
Connecting to Ollama with model: mistral
Model 'mistral' is available!
Loaded RDF dataset from: data/dataset.ttl
Total triples: 15

============================================================
Starting Autonomous Agent Loop
============================================================

============================================================
Iteration 1/10
============================================================

[THOUGHT PHASE]
Thought: I should start by getting statistics...

[ACTION PHASE]
Selected Action: inspect_statistics

[OBSERVATION PHASE]
Observation:
Graph Statistics:
  total_triples: 15
  ...

[LEARNING PHASE]
Insight: The graph contains a small knowledge base...
```

## Use Your Own Data

Replace the sample dataset with your own RDF file:

```bash
# Copy your RDF file (must be Turtle format)
cp /path/to/your/ontology.ttl data/dataset.ttl

# Run the agent
python main.py
```

## Troubleshooting

**Ollama not running?**
- Make sure Ollama is installed from https://ollama.ai
- Start it with: `ollama serve`

**Model not available?**
- Pull the model first: `ollama pull mistral`
- List available models: `ollama list`

**Slow inference?**
- Use a smaller model: `python main.py --model phi`
- Check Ollama has adequate resources

## Next Steps

- Explore `data/agent_memory.json` to see what the agent learned
- Check `data/dataset.ttl` for new insight triples
- Customize actions in `agent/agent.py`
- Adjust LLM parameters in `agent/llm.py`

## Help

For more details, see the full [README.md](README.md)

For issues, visit: https://github.com/MavrickRody/OntoTrain/issues

---

**Happy exploring! 🚂**
