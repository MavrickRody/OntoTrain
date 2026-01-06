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
- **ollama** - Local LLM inference via Ollama
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
│   ├── dataset.ttl    # RDF dataset (supports .ttl, .rdf, .xml, .n3, .nt)
│   └── agent_memory.json  # Agent memory persistence
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

### 4. Install and Start Ollama

Download and install Ollama from [https://ollama.ai](https://ollama.ai)

```bash
# For macOS/Linux - download from https://ollama.ai
# Or use package manager

# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull mistral

# Or pull other models:
# ollama pull llama2
# ollama pull codellama
```

**Available Models**:
- `mistral` - Mistral 7B (recommended)
- `llama2` - Llama 2 7B
- `codellama` - Code Llama
- `phi` - Microsoft Phi-2
- See full list: `ollama list` or [https://ollama.ai/library](https://ollama.ai/library)

### 5. Prepare Your RDF Dataset

**Option A**: Create a sample dataset

```bash
python main.py --create-sample-dataset
```

**Option B**: Use your own RDF dataset

The agent supports multiple RDF formats (auto-detected by file extension):
- Turtle (`.ttl`)
- RDF/XML (`.rdf`, `.xml`)
- N-Triples (`.nt`)
- N3 (`.n3`)

**Note**: If auto-detection fails, the agent automatically tries all supported formats as a fallback.

Example:
```bash
# For Turtle format
cp /path/to/your/ontology.ttl data/dataset.ttl

# For RDF/XML format
cp /path/to/your/ontology.rdf data/dataset.rdf
python main.py --dataset data/dataset.rdf
```

## Usage

### Basic Usage

```bash
# Make sure Ollama is running first
ollama serve  # In one terminal

# In another terminal, run the agent
python main.py
```

This will:
1. Connect to Ollama with the `mistral` model
2. Load the dataset from `data/dataset.ttl`
3. Run the autonomous agent for up to 10 iterations
4. Save insights back to the dataset
5. Persist memory to `data/agent_memory.json`
6. Generate comprehensive reports and visualizations

### Advanced Usage

```bash
# Use a different model
python main.py --model llama2

# Specify custom dataset
python main.py --model mistral --dataset data/my-data.ttl

# Run for 5 iterations
python main.py --iterations 5

# Enable verbose output
python main.py --verbose

# Set a specific exploration goal
python main.py --goal "Find all classes and their hierarchies"

# Custom memory file
python main.py --memory data/custom_memory.json

# Create sample dataset
python main.py --create-sample-dataset

# Combine options for advanced exploration
python main.py --model mistral --goal "Analyze entity relationships" --iterations 15 --verbose
```

### 🎨 Interactive Chat UI

OntoTrain includes a **Streamlit-based Chat UI** for interactive exploration:

```bash
# Launch the chat interface
streamlit run app.py
```

**Features:**
- 💬 **Natural language queries**: Ask questions about your RDF data
- 🔍 **SPARQL execution**: Run custom queries directly from chat
- 📊 **Interactive visualizations**: Real-time graph statistics
- 💡 **Insight viewer**: Browse agent-generated insights
- 📥 **Export options**: Download data in multiple formats
- 🤖 **LLM integration**: Get context-aware answers

**Example queries:**
- "Show me statistics"
- "List all classes"
- "Find patterns in the data"
- "Validate the graph"

See [CHAT_UI_README.md](CHAT_UI_README.md) for detailed documentation.

### Command-Line Options

```
--model NAME         Name of Ollama model (default: mistral)
--dataset PATH        Path to RDF dataset - supports .ttl, .rdf, .xml, .n3, .nt (default: data/dataset.ttl)
--memory PATH         Path to memory file (default: data/agent_memory.json)
--iterations N        Max iterations (default: 10)
--verbose            Enable verbose output
--goal TEXT          Exploration goal for the agent
--create-sample-dataset  Create sample RDF dataset and exit
```

### Output Files

After running the agent, you'll find these files in the `data/` directory:

- `agent_report.md` - Comprehensive markdown report with statistics, findings, and insights
- `graph_visualization.html` - Interactive HTML visualization of the graph
- `visualization_data.json` - Structured visualization data for custom tools
- `dataset_with_insights.json` - Graph exported in JSON-LD format
- `dataset_with_insights.nt` - Graph exported in N-Triples format
- `agent_memory.json` - Agent's memory and learning history
- Original dataset file with added insight triples

## How It Works

### Agent Loop

The agent follows a **Thought → Action → Observation → Learning** cycle:

1. **Thought**: LLM generates context-aware reasoning about what to explore next
2. **Action**: Agent selects an action based on the current goal
3. **Observation**: Action is executed, results are collected
4. **Learning**: LLM generates insights with confidence scores, persisted as RDF triples

### Available Actions

**Basic Analysis:**
- `inspect_statistics` - View graph statistics (triples, classes, properties)
- `list_classes` - List all RDF classes in the graph
- `list_properties` - List all RDF properties
- `summarize_graph` - Generate a human-readable summary

**Advanced Exploration:**
- `explore_entity` - Deep dive into specific entities with relationships
- `find_connected_entities` - Traverse graph to find related entities
- `find_clusters` - Identify groups of highly connected entities
- `find_hierarchies` - Detect hierarchical relationships (subClassOf, etc.)

**Querying:**
- `query_sparql` - Execute predefined SPARQL queries
- `custom_sparql_query` - Generate and execute custom SPARQL queries

**Pattern Detection:**
- `discover_patterns` - Find frequent predicates and usage patterns

**Quality Assurance:**
- `validate_graph` - Check for undefined classes, blank nodes, and issues

### Memory and Learning

- **Short-term memory**: Recent thoughts, actions, observations
- **Long-term memory**: Accumulated insights with confidence scores
- **Context awareness**: Remembers key findings across iterations
- **Action history**: Complete record of all actions taken
- **Persistence**: Memory and insights saved between sessions

### Advanced Features

**Goal-Oriented Exploration:**
- Set specific goals with `--goal` parameter
- Agent focuses exploration on achieving the goal
- Context builds incrementally across iterations

**Confidence Scoring:**
- Each insight receives a confidence score (0-1)
- Based on data quality and observation richness
- Persisted in RDF for transparency

**Visualizations:**
- HTML visualization report with graph structure
- JSON export for use with D3.js, Cytoscape, etc.
- Class hierarchy trees
- Statistics charts (class distribution, predicate usage)

**Performance Optimizations:**
- SPARQL query result caching
- Efficient graph traversal algorithms
- Progressive loading for large datasets

## Example Output

```
============================================================
Initializing Autonomous RDF AI Agent
============================================================
Connecting to Ollama with model: mistral
Model 'mistral' is available!
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
    model_name='mistral',  # Model name
    temperature=0.7,       # Sampling temperature
    max_tokens=512         # Max generation length
)
```

### Custom RDF Namespaces

Edit `agent/rdf_tools.py`:

```python
self.insights_namespace = Namespace("http://your-namespace.com/insights/")
```

## Troubleshooting

### Ollama Issues

**Problem**: `Ollama is not available`
**Solution**: Make sure Ollama is installed and running:
```bash
# Install from https://ollama.ai
# Then run:
ollama serve
```

**Problem**: `Model not found`
**Solution**: Pull the model first:
```bash
ollama pull mistral
# Or: ollama pull llama2
```

### Dataset Issues

**Problem**: `Error loading dataset`
**Solution**: 
- Ensure your RDF file is in a supported format (.ttl, .rdf, .xml, .n3, .nt)
- The agent auto-detects format from file extension and tries fallback formats if needed
- If the file extension doesn't match the content (e.g., RDF/XML file with .ttl extension), the agent will automatically try other formats
- Validate your RDF file at http://www.easyrdf.org/converter

**Problem**: `Warning: Could not verify Ollama model`
**Solution**: Make sure Ollama service is running with `ollama serve` before starting the agent

### Performance Issues

**Problem**: Slow inference
**Solution**: 
- Use a smaller model (e.g., `phi` instead of `mistral`)
- Ensure Ollama has adequate resources
- Check Ollama configuration for GPU settings

## Requirements

- **Python**: 3.10 or higher
- **Ollama**: Latest version from https://ollama.ai
- **RAM**: 8GB minimum (16GB recommended for larger models)
- **Disk**: Space for Ollama models (varies by model)
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
- LLM inference via [Ollama](https://ollama.ai)
- Inspired by autonomous agent research and semantic web technologies

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions

---

**Happy exploring with OntoTrain! 🚂**