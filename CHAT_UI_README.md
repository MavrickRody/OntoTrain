# OntoTrain Chat UI - Interactive RDF Explorer

A Streamlit-based chat interface for exploring RDF knowledge graphs with natural language queries.

## Features

### 🎯 Core Capabilities
- **Natural Language Interface**: Ask questions about your RDF data in plain English
- **SPARQL Execution**: Run custom SPARQL queries directly from the chat
- **Pattern Discovery**: Automatically identify patterns and relationships
- **Data Validation**: Check graph quality and structural issues
- **Insights Tracking**: View and manage agent-generated insights
- **Multi-Format Export**: Export data in JSON-LD, N-Triples, and more

### 💬 Query Types Supported

1. **Statistics Queries**
   - "Show me statistics"
   - "How many triples are in the graph?"
   - "What's the count of classes?"

2. **Class & Property Exploration**
   - "List all classes"
   - "Show me the properties"
   - "What classes are defined?"

3. **SPARQL Queries**
   - Paste SPARQL queries in code blocks:
   ```sparql
   SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10
   ```

4. **Pattern Analysis**
   - "Find patterns in the data"
   - "What are the most frequent predicates?"

5. **Validation**
   - "Validate the graph"
   - "Check for issues"
   - "Are there any undefined classes?"

6. **Hierarchy Discovery**
   - "Find hierarchies"
   - "Show class hierarchies"

7. **Clustering**
   - "Find entity clusters"
   - "Show connected entities"

8. **General Questions**
   - Ask any question about the RDF data
   - The LLM will provide context-aware answers

## Getting Started

### Prerequisites
- Python 3.10+
- Ollama installed and running
- OntoTrain dependencies installed

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start Ollama:
```bash
ollama serve
```

3. Pull a model (if not already available):
```bash
ollama pull mistral
```

### Running the Chat UI

Launch the Streamlit application:

```bash
streamlit run app.py
```

Or use the shortcut:

```bash
python -m streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

## Using the Interface

### 1. Load Your Dataset

In the sidebar:
1. Select your RDF dataset file (.ttl, .rdf, .xml, .n3, .nt)
2. Choose an Ollama model (mistral, llama2, etc.)
3. Click **"Load Dataset"**

### 2. Start Chatting

Type natural language questions in the chat input:

**Example queries:**
- "Show me statistics about the graph"
- "List all classes in the dataset"
- "Find patterns in predicate usage"
- "What are the most connected entities?"

### 3. Run SPARQL Queries

Paste SPARQL queries in code blocks:

```sparql
SELECT ?class (COUNT(?instance) as ?count)
WHERE {
  ?instance a ?class .
}
GROUP BY ?class
ORDER BY DESC(?count)
LIMIT 10
```

### 4. View Insights

Click **"View All Insights"** in the sidebar to see all agent-generated insights with confidence scores.

### 5. Export Data

Use the export buttons in the sidebar:
- **Export to JSON-LD**: Structured RDF data
- **Export to N-Triples**: Simple triple format

## Features in Detail

### Dataset Management
- **Multi-format support**: Automatically detects Turtle, RDF/XML, N-Triples, N3
- **Real-time loading**: Dataset statistics displayed immediately
- **Error handling**: Clear feedback if dataset fails to load

### Chat Interface
- **Message history**: All queries and responses preserved
- **Markdown support**: Rich formatting in responses
- **Code blocks**: Syntax highlighting for SPARQL and RDF data
- **Streaming responses**: Real-time answer generation (for LLM queries)

### Sidebar Information
- **Dataset metrics**: Triples, classes, properties at a glance
- **Insight counter**: Track agent discoveries
- **Quick actions**: One-click export and validation

### Smart Query Processing
The system automatically detects query intent:
- Keywords trigger specific RDF operations
- Ambiguous queries route to the LLM
- SPARQL code blocks execute directly
- Natural language gets contextual answers

## Architecture

```
app.py
├── OntoTrainChatUI (Main Class)
│   ├── Session State Management
│   ├── RDFTools Integration
│   ├── LLM Integration  
│   ├── Memory Integration
│   └── Query Processing Pipeline
│       ├── Statistics Handler
│       ├── Class/Property Handler
│       ├── SPARQL Executor
│       ├── Pattern Analyzer
│       ├── Validation Engine
│       └── LLM Fallback
```

## Tips & Best Practices

### Performance
- Start with smaller datasets for faster response times
- Use LIMIT clauses in SPARQL queries
- Cache is automatically used for repeated queries

### Query Formulation
- Be specific in your questions
- Use keywords like "list", "show", "find", "count"
- For complex analysis, break into multiple queries

### Error Recovery
- If a query fails, try rephrasing
- Check dataset is loaded (sidebar shows stats)
- Verify Ollama is running for LLM queries

### Data Exploration Workflow
1. Start with statistics to understand dataset size
2. List classes and properties to see schema
3. Find patterns to identify interesting relationships
4. Validate to check data quality
5. Use SPARQL for specific deep dives

## Troubleshooting

### "Please load a dataset first"
- Click "Load Dataset" button in sidebar
- Ensure dataset file exists in data/ directory

### "LLM temporarily unavailable"
- Check Ollama is running: `ollama serve`
- Verify model is pulled: `ollama pull mistral`
- Check Ollama logs for errors

### SPARQL query errors
- Verify query syntax
- Check if predicates/classes exist in dataset
- Use LIMIT to prevent timeout on large results

### Blank results
- Dataset may not contain requested information
- Try broader queries first
- Use validation to check for structural issues

## Advanced Usage

### Custom SPARQL Templates
Create reusable query patterns:

```sparql
# Find all instances of a class
SELECT ?instance WHERE {
  ?instance a <http://your.ontology/Class> .
} LIMIT 100
```

### Combining Multiple Queries
1. Run statistics to get overview
2. List classes to identify targets
3. Run focused SPARQL on specific classes
4. Validate results

### Integration with Agent
- Run `python main.py` to generate insights
- Load the Chat UI to explore agent findings
- Use "show insights" to review discoveries
- Export insights as RDF for further analysis

## Keyboard Shortcuts

- **Enter**: Send message
- **Shift+Enter**: New line in input
- **Ctrl+K**: Clear chat (refresh page)

## Future Enhancements

Planned features:
- [ ] Graph visualization within chat
- [ ] Query history with rerun
- [ ] Saved query templates
- [ ] Multi-dataset comparison
- [ ] Real-time agent execution
- [ ] Interactive entity exploration
- [ ] Export chat transcript

## Contributing

To add new query handlers:

1. Add detection logic in `process_user_query()`
2. Implement handler method (e.g., `handle_xxx_query()`)
3. Update this README with example queries

## License

Same as OntoTrain main project.

## Support

For issues or questions:
- Check main README.md
- Review error messages in chat
- Check Ollama and Streamlit logs
- Verify dataset format compatibility
