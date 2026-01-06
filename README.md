# OntoTrain - Autonomous RDF AI Agent

A fully local, open-source, autonomous RDF AI agent implemented in Python. This agent explores RDF knowledge graphs using a **Thought → Action → Observation → Learning** loop, powered by local LLM inference and SPARQL queries.

## Features

- **100% Local**: No cloud APIs, runs entirely on your machine
- **Open Source**: Uses only open-source libraries and models
- **RDF-Native**: Built on rdflib with full SPARQL support
- **Autonomous**: Agent decides what to query and explore next
- **Learning**: Generates and persists insights as RDF triples
- **Memory**: Maintains session history and learned insights

## Technology Stack

- **Python 3.10+**
- **rdflib** - RDF graph manipulation and SPARQL queries
- **llama-cpp-python** - Local LLM inference
- **faiss-cpu** - Vector storage (for future extensions)
- **sentence-transformers** - Text embeddings (for future extensions)

## Architecture

```
OntoTrain/
├── agent/
│   ├── __init__.py
│   ├── agent.py       # Autonomous agent loop
│   ├── llm.py         # Local LLM loader
│   ├── rdf_tools.py   # RDF and SPARQL tools
│   └── memory.py      # Learning and memory layer
├── data/
│   ├── dataset.ttl    # RDF dataset (Turtle format)
│   └── agent_memory.json  # Agent memory persistence
├── models/
│   └── mistral-7b-instruct.Q4_K_M.gguf  # Local GGUF model
├── main.py            # Entry point
├── requirements.txt   # Dependencies
└── README.md          # This file
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/MavrickRody/OntoTrain.git
cd OntoTrain
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Installing `llama-cpp-python` may take a few minutes as it compiles C++ code.

### 4. Download a Local Model

Download a GGUF model (recommended: Mistral 7B Instruct Q4):

```bash
# Create models directory
mkdir -p models

# Download using wget (Linux/Mac)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -O models/mistral-7b-instruct.Q4_K_M.gguf

# OR download using curl
curl -L https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -o models/mistral-7b-instruct.Q4_K_M.gguf
```

**Alternative Models**:
- Any GGUF model from TheBloke's HuggingFace repositories
- Llama 2 7B, Mistral 7B, or similar instruction-tuned models
- Adjust `--model` parameter when running

### 5. Prepare Your RDF Dataset

**Option A**: Create a sample dataset

```bash
python main.py --create-sample-dataset
```

**Option B**: Use your own RDF dataset

Place your Turtle (`.ttl`) format RDF file in `data/dataset.ttl`

Example:
```bash
cp /path/to/your/ontology.ttl data/dataset.ttl
```

## Usage

### Basic Usage

```bash
python main.py
```

This will:
1. Load the model from `models/mistral-7b-instruct.Q4_K_M.gguf`
2. Load the dataset from `data/dataset.ttl`
3. Run the autonomous agent for up to 10 iterations
4. Save insights back to the dataset
5. Persist memory to `data/agent_memory.json`

### Advanced Usage

```bash
# Specify custom paths
python main.py --model models/my-model.gguf --dataset data/my-data.ttl

# Run for 5 iterations
python main.py --iterations 5

# Enable verbose output
python main.py --verbose

# Custom memory file
python main.py --memory data/custom_memory.json

# Create sample dataset
python main.py --create-sample-dataset
```

### Command-Line Options

```
--model PATH          Path to GGUF model (default: models/mistral-7b-instruct.Q4_K_M.gguf)
--dataset PATH        Path to RDF dataset (default: data/dataset.ttl)
--memory PATH         Path to memory file (default: data/agent_memory.json)
--iterations N        Max iterations (default: 10)
--verbose            Enable verbose output
--create-sample-dataset  Create sample RDF dataset and exit
```

## How It Works

### Agent Loop

The agent follows a **Thought → Action → Observation → Learning** cycle:

1. **Thought**: LLM generates reasoning about what to explore next
2. **Action**: Agent selects an action (e.g., query SPARQL, list classes)
3. **Observation**: Action is executed, results are collected
4. **Learning**: LLM generates insights, which are persisted as RDF triples

### Available Actions

- `inspect_statistics` - View graph statistics (triples, classes, properties)
- `list_classes` - List all RDF classes in the graph
- `list_properties` - List all RDF properties
- `query_sparql` - Execute SPARQL queries
- `discover_patterns` - Find common patterns in the graph
- `summarize_graph` - Generate a human-readable summary

### Memory and Learning

- **Short-term memory**: Recent thoughts, actions, observations
- **Long-term memory**: Accumulated insights
- **Action history**: Record of all actions taken
- **Persistence**: Memory saved to JSON file between sessions

## Example Output

```
============================================================
Initializing Autonomous RDF AI Agent
============================================================
Loading model from: models/mistral-7b-instruct.Q4_K_M.gguf
Model loaded successfully!
Loaded RDF dataset from: data/dataset.ttl
Total triples: 15

Agent initialized successfully!
============================================================

============================================================
Starting Autonomous Agent Loop
============================================================

============================================================
Iteration 1/10
============================================================

[THOUGHT PHASE]
Thought: I should start by understanding the structure of this graph...

[ACTION PHASE]
Selected Action: inspect_statistics

[OBSERVATION PHASE]
Observation:
Graph Statistics:
  total_triples: 15
  total_subjects: 8
  total_predicates: 6
  total_objects: 12
  total_classes: 2
  total_properties: 3

[LEARNING PHASE]
Insight: The graph contains a small but structured knowledge base with 2 main classes and 3 properties connecting 8 entities.

...
```

## Customization

### Adding New Actions

Edit `agent/agent.py` and add to `available_actions`:

```python
self.available_actions = [
    'inspect_statistics',
    'list_classes',
    'your_new_action',  # Add here
]
```

Then implement the action in `_execute_action()` method.

### Adjusting LLM Parameters

Edit `agent/llm.py` or modify initialization in `agent/agent.py`:

```python
self.llm = LocalLLM(
    model_path=model_path,
    n_ctx=4096,        # Context window
    n_threads=4,       # CPU threads
    temperature=0.7,   # Sampling temperature
    max_tokens=512     # Max generation length
)
```

### Custom RDF Namespaces

Edit `agent/rdf_tools.py`:

```python
self.insights_namespace = Namespace("http://your-namespace.com/insights/")
```

## Troubleshooting

### Model Loading Issues

**Problem**: `Model file not found`
**Solution**: Ensure the model path is correct and the file exists

**Problem**: `llama-cpp-python` compilation fails
**Solution**: Install build tools:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
xcode-select --install
```

### Dataset Issues

**Problem**: `Error loading dataset`
**Solution**: Ensure your RDF file is valid Turtle format. Validate at http://www.easyrdf.org/converter

### Memory Issues

**Problem**: Out of memory during model loading
**Solution**: Use a smaller quantized model (Q3 or Q2 instead of Q4)

### Performance Issues

**Problem**: Slow inference
**Solution**: 
- Increase `n_threads` parameter
- Use GPU acceleration (requires llama-cpp-python with GPU support)
- Use smaller model or higher quantization

## Requirements

- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (16GB recommended for 7B models)
- **Disk**: 5GB for model + dataset
- **OS**: Linux, macOS, or Windows with WSL

## License

This project is open source. See LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Citation

If you use OntoTrain in your research, please cite:

```bibtex
@software{ontotrain2024,
  title={OntoTrain: Autonomous RDF AI Agent},
  author={OntoTrain Contributors},
  year={2024},
  url={https://github.com/MavrickRody/OntoTrain}
}
```

## Acknowledgments

- Built with [rdflib](https://github.com/RDFLib/rdflib)
- LLM inference via [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- Inspired by autonomous agent research and semantic web technologies

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions

---

**Happy exploring with OntoTrain! 🚂**