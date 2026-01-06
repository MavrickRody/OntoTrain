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

# This may take 5-10 minutes due to llama-cpp-python compilation
```

## Download Model

```bash
# Create models directory
mkdir -p models

# Download Mistral 7B Instruct Q4 (recommended, ~4GB)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -O models/mistral-7b-instruct.Q4_K_M.gguf

# Or use curl if wget is not available
curl -L https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -o models/mistral-7b-instruct.Q4_K_M.gguf
```

## Create Sample Dataset

```bash
# Generate a sample RDF knowledge graph
python main.py --create-sample-dataset
```

This creates `data/dataset.ttl` with sample data.

## Run the Agent

```bash
# Run with default settings (10 iterations)
python main.py

# Or run with verbose output
python main.py --verbose

# Or run for fewer iterations
python main.py --iterations 5
```

## What Happens?

The agent will:

1. **Load** the local LLM model (first run takes longer)
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
Loading model from: models/mistral-7b-instruct.Q4_K_M.gguf
Model loaded successfully!
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

**Model not loading?**
- Check the file path matches exactly
- Ensure the file downloaded completely (~4GB)

**Out of memory?**
- Use a smaller model (Q3 or Q2 quantization)
- Close other applications

**Slow inference?**
- Increase `n_threads` in `agent/agent.py`
- Consider GPU acceleration (requires rebuilding llama-cpp-python with CUDA)

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
