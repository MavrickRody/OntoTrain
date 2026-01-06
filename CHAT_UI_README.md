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

## 🆕 Enhanced Features (v2.0)

### 📊 Graph Visualization Within Chat
- **Interactive Charts**: View real-time statistics, class distributions, and property usage
- **Multiple Views**: Statistics, class distribution pie charts, and property usage bar charts
- **Inline Display**: Visualizations appear directly in the chat interface
- **Plotly Integration**: Interactive, zoomable visualizations

**Usage:**
- Type: "visualize the graph" or "show me visualization"
- Click "🎨 Show Graph Viz" in sidebar

### 📜 Query History with Rerun
- **Automatic Tracking**: All SPARQL queries are automatically saved
- **Quick Rerun**: Rerun any previous query with one click
- **Timestamp Logging**: Track when queries were executed
- **Last Query Shortcut**: Quickly rerun your last query

**Usage:**
- View history: Click "📋 View History" in sidebar
- Rerun last: Click "🔄 Rerun Last" in sidebar
- Rerun specific: Click "Rerun" button next to any query in history

### 💾 Saved Query Templates
- **Pre-built Templates**: 6 ready-to-use SPARQL query templates
- **Custom Templates**: Save your own frequently-used queries
- **One-Click Execution**: Run templates directly from the interface
- **Template Management**: Add, view, and organize your query templates

**Default Templates:**
1. All Triples (sample)
2. All Classes
3. All Properties
4. Class Instances
5. Property Usage Count
6. Subjects with Most Properties

**Usage:**
- View templates: Click "📝 Manage Templates" in sidebar
- Add template: Use the "➕ Add New Template" form
- Run template: Click "Use" button next to any template

### 🔄 Multi-Dataset Comparison
- **Multiple Datasets**: Load and switch between different RDF datasets
- **Dataset Info**: View statistics for each loaded dataset
- **Easy Switching**: Select from dropdown in sidebar
- **Format Support**: Turtle, RDF/XML, N-Triples, N3

**Usage:**
- Select dataset from dropdown in sidebar
- Click "🔄 Load Dataset" to switch
- Compare insights across different datasets

### 🤖 Real-time Agent Execution
- **In-Chat Execution**: Run the autonomous agent directly from the UI
- **Progress Tracking**: See real-time progress updates
- **Limited Iterations**: Configured for 3 iterations for quick results
- **Insight Generation**: New insights appear in sidebar immediately

**Usage:**
- Click "▶️ Run Agent" in sidebar
- Watch progress bar for execution status
- Check "Agent Insights" section for results

### 🔍 Interactive Entity Exploration
- **Deep Dive**: Explore specific entities interactively
- **Outgoing Relations**: See all properties where entity is subject
- **Incoming Relations**: See all triples where entity is object
- **Tabbed Interface**: Organized view of relationships

**Usage:**
- Type: "explore entity: http://example.org/entity1"
- View relationships in expandable sections
- Navigate between outgoing and incoming relations

### 📄 Export Chat Transcript
- **Full Conversation Export**: Save entire chat history to Markdown
- **Timestamped**: Includes date, time, and dataset information
- **Downloadable**: Get a file to share or archive
- **Formatted**: Clean Markdown format with role headers

**Usage:**
- Click "📄 Export Chat Transcript" in sidebar
- File saved to `data/chat_exports/`
- Download button appears for immediate download

## 🎯 Quick Start Examples

### Example 1: Comprehensive Exploration
```
1. "Show me statistics"
2. "visualize the graph"
3. "Find patterns"
4. "List all classes"
5. "validate the graph"
```

### Example 2: Using Templates
```
1. Click "📝 Manage Templates" in sidebar
2. Click "Use" next to "All Classes" template
3. View results
4. Save a custom template for future use
```

### Example 3: Entity Exploration
```
1. "List all classes" (to get entity URIs)
2. "explore entity: http://data.europa.eu/949/Balise"
3. View outgoing and incoming relationships
```

### Example 4: Agent-Driven Analysis
```
1. Click "▶️ Run Agent" in sidebar
2. Wait for completion (3 iterations)
3. Click "📋 View All Insights" in sidebar
4. Review agent discoveries
```

## 🎨 UI Components

### Sidebar Sections
1. **Configuration**: Dataset and model selection
2. **Dataset Info**: Real-time statistics
3. **Query History**: Recent queries with rerun
4. **Query Templates**: Saved SPARQL templates
5. **Agent Insights**: Generated insights
6. **Visualization**: Graph viz trigger
7. **Export**: Data and transcript export
8. **Agent Control**: Real-time agent execution

### Chat Interface
- **Message History**: Scrollable conversation
- **User Messages**: Blue background, right-aligned
- **Assistant Messages**: Gray background, left-aligned
- **Inline Visualizations**: Charts and graphs within chat
- **Code Blocks**: Syntax-highlighted SPARQL queries

## 🚀 Advanced Usage

### Custom SPARQL with Templates
1. Create a complex query
2. Test it in chat: \`\`\`sparql ... \`\`\`
3. If useful, save as template
4. Reuse across sessions

### Query History Navigation
- Browse last 20 queries
- Filter by type
- Rerun with modifications
- Export history with chat transcript

### Multi-Dataset Workflow
1. Load Dataset A → Analyze
2. Save findings and queries
3. Load Dataset B → Compare
4. Export comparison results

### Visualization Export
1. Generate visualization in chat
2. Export chat transcript (includes viz data)
3. OR run `python main.py` for HTML viz
4. Share interactive reports

## 💡 Tips & Tricks

1. **Quick Stats**: Type "stats" for instant overview
2. **Template Library**: Build a personal library of useful queries
3. **History Search**: Use query history to avoid retyping
4. **Agent + Chat**: Run agent first, then explore insights in chat
5. **Export Everything**: Transcript + Data + Insights for complete record
6. **Visualization First**: Start with visualization to understand structure
7. **Templates for Efficiency**: Save time with pre-built queries

## 🐛 Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check model availability: `ollama list`
- Pull model if needed: `ollama pull mistral`

### Dataset Loading Errors
- Check file path exists
- Verify RDF format (ttl, rdf, xml, n3, nt)
- Look for parsing errors in output

### Visualization Not Showing
- Ensure dataset is loaded
- Try clicking "🎨 Show Graph Viz" again
- Check browser console for errors

### Query History Empty
- Run a SPARQL query first
- History only tracks SPARQL queries
- Check `data/saved_queries.json`

## 📊 Output Files

The enhanced chat UI generates:
- `data/chat_exports/chat_transcript_*.md` - Conversation exports
- `data/saved_queries.json` - Query templates
- `data/agent_memory.json` - Insights and learning
- `data/export_*.json` - Exported RDF data
- `data/export_*.nt` - N-Triples exports

## 🔗 Integration with Main Agent

The chat UI complements the main CLI agent:

**CLI Agent (`python main.py`):**
- Long-running autonomous exploration
- Full visualization generation
- Comprehensive reports
- Batch processing

**Chat UI (`streamlit run app.py`):**
- Interactive exploration
- Quick queries and insights
- Real-time feedback
- User-guided analysis

**Best Practice:** Run CLI agent first for deep analysis, then use Chat UI for interactive exploration of findings.

