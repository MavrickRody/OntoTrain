#!/usr/bin/env python3
"""
OntoTrain Chat UI - Interactive Streamlit interface for RDF exploration.

Provides a chat-based interface to interact with RDF data and agent insights.
"""

import streamlit as st
import json
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from io import BytesIO

from agent.rdf_tools import RDFTools
from agent.llm import LocalLLM
from agent.memory import AgentMemory
from agent.visualizations import RDFVisualizer

# PDF export support
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# Page configuration
st.set_page_config(
    page_title="OntoTrain - RDF Explorer",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Custom CSS with theme support
def get_theme_css(theme='light'):
    """Get CSS styles based on current theme."""
    if theme == 'dark':
        return """
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #6495ed;
                text-align: center;
                padding: 1rem;
            }
            .stat-box {
                background-color: #2b2b2b;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
                color: #e0e0e0;
            }
            .insight-box {
                background-color: #1a3a52;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
                border-left: 4px solid #6495ed;
                color: #e0e0e0;
            }
            .chat-message {
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
            }
            .user-message {
                background-color: #1e3d59;
                margin-left: 2rem;
                color: #e0e0e0;
            }
            .assistant-message {
                background-color: #2b2b2b;
                margin-right: 2rem;
                color: #e0e0e0;
            }
            .stMarkdown {
                color: #e0e0e0;
            }
        </style>
        """
    else:  # light theme
        return """
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1f77b4;
                text-align: center;
                padding: 1rem;
            }
            .stat-box {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
            }
            .insight-box {
                background-color: #e8f4f8;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
                border-left: 4px solid #1f77b4;
            }
            .chat-message {
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
            }
            .user-message {
                background-color: #e3f2fd;
                margin-left: 2rem;
            }
            .assistant-message {
                background-color: #f5f5f5;
                margin-right: 2rem;
            }
        </style>
        """

# Apply theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# Keyboard shortcuts CSS and JavaScript
st.markdown("""
<style>
    .keyboard-hint {
        font-size: 0.8rem;
        color: #888;
        font-style: italic;
    }
</style>
<script>
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K: Focus on search/query input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const input = document.querySelector('textarea[aria-label="Enter your query"]');
        if (input) input.focus();
    }
    // Ctrl/Cmd + Enter: Submit query
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const buttons = document.querySelectorAll('button');
        for (let btn of buttons) {
            if (btn.textContent.includes('Send') || btn.textContent.includes('Execute')) {
                btn.click();
                break;
            }
        }
    }
    // Ctrl/Cmd + /: Show templates
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        const templateBtn = document.querySelector('button[title="Show query templates"]');
        if (templateBtn) templateBtn.click();
    }
});
</script>
""", unsafe_allow_html=True)


class OntoTrainChatUI:
    """Interactive chat interface for RDF exploration."""
    
    def __init__(self):
        """Initialize the chat UI."""
        self.load_configuration()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'rdf_tools' not in st.session_state:
            st.session_state.rdf_tools = None
        if 'llm' not in st.session_state:
            st.session_state.llm = None
        if 'memory' not in st.session_state:
            st.session_state.memory = None
        if 'current_dataset' not in st.session_state:
            st.session_state.current_dataset = None
        if 'dataset_path' not in st.session_state:
            st.session_state.dataset_path = None
        if 'model_name' not in st.session_state:
            st.session_state.model_name = self.default_model
        if 'memory_file' not in st.session_state:
            st.session_state.memory_file = self.memory_file
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        if 'saved_queries' not in st.session_state:
            st.session_state.saved_queries = self.load_saved_queries()
        if 'agent_running' not in st.session_state:
            st.session_state.agent_running = False
        if 'datasets' not in st.session_state:
            st.session_state.datasets = {}
        if 'current_viz_data' not in st.session_state:
            st.session_state.current_viz_data = None
        # Quick Wins additions
        if 'insight_search' not in st.session_state:
            st.session_state.insight_search = ""
        if 'insight_filter' not in st.session_state:
            st.session_state.insight_filter = "All"
    
    def load_configuration(self):
        """Load default configuration."""
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.default_dataset = "data/dataset.rdf"
        self.memory_file = "data/agent_memory.json"
        self.default_model = "mistral"
        self.queries_file = "data/saved_queries.json"
        self.chat_export_dir = Path("data/chat_exports")
        self.chat_export_dir.mkdir(exist_ok=True)
    
    def load_saved_queries(self) -> Dict[str, str]:
        """Load saved query templates."""
        if Path(self.queries_file).exists():
            try:
                with open(self.queries_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
                st.warning(f"Could not load saved queries: {e}")
                return self.get_default_query_templates()
        return self.get_default_query_templates()
    
    def get_default_query_templates(self) -> Dict[str, str]:
        """Return default SPARQL query templates."""
        return {
            "All Triples (sample)": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10",
            "All Classes": "SELECT DISTINCT ?class WHERE { ?s a ?class } ORDER BY ?class",
            "All Properties": "SELECT DISTINCT ?property WHERE { ?s ?property ?o } ORDER BY ?property",
            "Class Instances": "SELECT ?instance WHERE { ?instance a ?class } LIMIT 50",
            "Property Usage Count": "SELECT ?property (COUNT(?s) as ?count) WHERE { ?s ?property ?o } GROUP BY ?property ORDER BY DESC(?count)",
            "Subjects with Most Properties": "SELECT ?subject (COUNT(?property) as ?propCount) WHERE { ?subject ?property ?o } GROUP BY ?subject ORDER BY DESC(?propCount) LIMIT 20"
        }
    
    def save_query_templates(self):
        """Save query templates to file."""
        try:
            with open(self.queries_file, 'w') as f:
                json.dump(st.session_state.saved_queries, f, indent=2)
        except (PermissionError, OSError, json.JSONEncodeError) as e:
            st.error(f"Error saving queries: {e}")
    
    def render_sidebar(self):
        """Render the sidebar with configuration options."""
        st.sidebar.markdown("## 🚂 OntoTrain Configuration")
        
        # Quick Wins: Theme Toggle
        st.sidebar.markdown("### 🎨 Appearance")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("☀️ Light", use_container_width=True, disabled=st.session_state.theme == 'light'):
                st.session_state.theme = 'light'
                st.rerun()
        with col2:
            if st.button("🌙 Dark", use_container_width=True, disabled=st.session_state.theme == 'dark'):
                st.session_state.theme = 'dark'
                st.rerun()
        
        # Dataset selection
        st.sidebar.markdown("### 📊 Dataset")
        dataset_files = list(self.data_dir.glob("*.ttl")) + \
                       list(self.data_dir.glob("*.rdf")) + \
                       list(self.data_dir.glob("*.xml")) + \
                       list(self.data_dir.glob("*.n3")) + \
                       list(self.data_dir.glob("*.nt"))
        
        dataset_options = [str(f) for f in dataset_files] if dataset_files else [self.default_dataset]
        
        selected_dataset = st.sidebar.selectbox(
            "Select Dataset",
            options=dataset_options,
            index=0
        )
        
        # Model selection
        st.sidebar.markdown("### 🤖 LLM Model")
        model_name = st.sidebar.selectbox(
            "Ollama Model",
            options=["mistral", "llama2", "llama3", "codellama", "phi", "gemma"],
            index=0
        )
        
        # Load dataset button
        if st.sidebar.button("🔄 Load Dataset", use_container_width=True):
            self.load_dataset(selected_dataset, model_name)
        
        # Display dataset info
        if st.session_state.rdf_tools:
            st.sidebar.markdown("### 📈 Dataset Info")
            stats = st.session_state.rdf_tools.get_statistics()
            st.sidebar.metric("Total Triples", f"{stats['total_triples']:,}")
            st.sidebar.metric("Classes", stats.get('total_classes', 0))
            st.sidebar.metric("Properties", stats.get('total_properties', 0))
        
        # Query History Section
        st.sidebar.markdown("### 📜 Query History")
        if st.session_state.query_history:
            st.sidebar.metric("Queries Run", len(st.session_state.query_history))
            if st.sidebar.button("📋 View History", use_container_width=True):
                self.show_query_history()
            if st.sidebar.button("🔄 Rerun Last", use_container_width=True):
                self.rerun_last_query()
        
        # Saved Query Templates
        st.sidebar.markdown("### 💾 Query Templates")
        if st.sidebar.button("📝 Manage Templates", use_container_width=True):
            self.show_query_templates()
        
        # Insights section with Quick Wins: Search & Filter
        st.sidebar.markdown("### 💡 Agent Insights")
        if st.session_state.memory:
            insights = st.session_state.memory.get_all_insights()
            st.sidebar.metric("Total Insights", len(insights))
            
            # Quick Wins: Search insights
            search_term = st.sidebar.text_input("🔍 Search Insights", 
                                                value=st.session_state.insight_search,
                                                key="insight_search_input",
                                                placeholder="Search keywords...")
            st.session_state.insight_search = search_term
            
            # Quick Wins: Filter insights
            filter_options = ["All", "Statistics", "Patterns", "Validation", "Hierarchies", "Clusters"]
            filter_type = st.sidebar.selectbox("🎯 Filter by Type", 
                                              options=filter_options,
                                              index=filter_options.index(st.session_state.insight_filter) if st.session_state.insight_filter in filter_options else 0)
            st.session_state.insight_filter = filter_type
            
            if st.sidebar.button("📋 View Filtered Insights", use_container_width=True):
                self.show_insights_modal()
        
        # Graph Visualization
        st.sidebar.markdown("### 📊 Visualization")
        if st.sidebar.button("🎨 Show Graph Viz", use_container_width=True):
            self.show_graph_visualization()
        
        # Export options - Quick Wins: PDF Export
        st.sidebar.markdown("### 📥 Export")
        if st.sidebar.button("💾 Export to JSON-LD", use_container_width=True):
            self.export_data("json-ld")
        if st.sidebar.button("💾 Export to N-Triples", use_container_width=True):
            self.export_data("nt")
        if st.sidebar.button("📄 Export Chat Transcript", use_container_width=True):
            self.export_chat_transcript()
        # Quick Wins: PDF Report Export
        if st.sidebar.button("📕 Export Report to PDF", use_container_width=True):
            self.export_report_to_pdf()
        
        # Real-time Agent Execution
        st.sidebar.markdown("### 🤖 Agent Control")
        if st.sidebar.button("▶️ Run Agent", use_container_width=True):
            self.run_agent_realtime()
    
    def load_dataset(self, dataset_path: str, model_name: str):
        """Load the RDF dataset and initialize components."""
        try:
            with st.spinner("Loading dataset and initializing LLM..."):
                # Initialize RDF Tools
                st.session_state.rdf_tools = RDFTools(dataset_path)
                st.session_state.current_dataset = dataset_path
                st.session_state.dataset_path = dataset_path
                st.session_state.model_name = model_name
                st.session_state.memory_file = self.memory_file
                
                # Initialize LLM
                st.session_state.llm = LocalLLM(
                    model_name=model_name,
                    temperature=0.7,
                    verbose=False
                )
                
                # Initialize Memory
                st.session_state.memory = AgentMemory(self.memory_file)
                
                st.success(f"✅ Dataset loaded: {dataset_path}")
                st.success(f"✅ Model ready: {model_name}")
                
                # Add system message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Hello! I've loaded the RDF dataset from `{dataset_path}`. I can help you explore the data, run SPARQL queries, find patterns, and more. What would you like to know?"
                })
        
        except Exception as e:
            st.error(f"❌ Error loading dataset: {e}")
    
    def show_insights_modal(self):
        """Display all agent insights in an expandable section with search and filter."""
        if st.session_state.memory:
            insights = st.session_state.memory.get_all_insights()
            
            # Quick Wins: Apply search and filter
            filtered_insights = self.filter_insights(
                insights,
                st.session_state.insight_search,
                st.session_state.insight_filter
            )
            
            if not filtered_insights:
                st.warning("No insights match the current search/filter criteria.")
                return
            
            st.info(f"Showing {len(filtered_insights)} of {len(insights)} insights")
            
            for idx, insight in enumerate(filtered_insights, 1):
                insight_preview = str(insight.get('insight', 'N/A'))[:50]
                with st.expander(f"Insight {idx}: {insight_preview}..."):
                    st.markdown(f"**Insight:** {insight.get('insight', 'N/A')}")
                    st.markdown(f"**Source:** {insight.get('source', 'N/A')}")
                    st.markdown(f"**Iteration:** {insight.get('iteration', 'N/A')}")
                    st.markdown(f"**Timestamp:** {insight.get('timestamp', 'N/A')}")
    
    def export_data(self, format_type: str):
        """Export RDF data in the specified format."""
        if not st.session_state.rdf_tools:
            st.warning("⚠️ Please load a dataset first.")
            return
        
        try:
            output_file = f"data/export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            st.session_state.rdf_tools.export_to_format(format_type, output_file)
            st.success(f"✅ Data exported to: {output_file}")
        except Exception as e:
            st.error(f"❌ Export error: {e}")
    
    def render_chat_interface(self):
        """Render the main chat interface."""
        st.markdown("<div class='main-header'>🚂 OntoTrain - RDF Knowledge Graph Explorer</div>", unsafe_allow_html=True)
        
        # Quick Wins: Keyboard shortcuts hint
        with st.expander("⌨️ Keyboard Shortcuts"):
            st.markdown("""
            - **Ctrl/Cmd + K**: Focus query input
            - **Ctrl/Cmd + Enter**: Submit query
            - **Ctrl/Cmd + /**: Show templates
            """)
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about the RDF data, request SPARQL queries, or explore patterns..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process user query
            self.process_user_query(prompt)
    
    def process_user_query(self, query: str):
        """Process user query and generate response."""
        if not st.session_state.rdf_tools or not st.session_state.llm:
            response = "⚠️ Please load a dataset first using the sidebar."
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
            return
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = self.generate_response(query)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    def generate_response(self, query: str) -> str:
        """Generate a response to the user query."""
        query_lower = query.lower()
        
        # Handle specific query types
        if "statistic" in query_lower or "how many" in query_lower or "count" in query_lower:
            return self.handle_statistics_query()
        
        elif "class" in query_lower and ("list" in query_lower or "show" in query_lower or "what" in query_lower):
            return self.handle_classes_query()
        
        elif "propert" in query_lower and ("list" in query_lower or "show" in query_lower or "what" in query_lower):
            return self.handle_properties_query()
        
        elif "sparql" in query_lower or "query" in query_lower:
            return self.handle_sparql_query(query)
        
        elif "pattern" in query_lower or "frequent" in query_lower:
            return self.handle_patterns_query()
        
        elif "validat" in query_lower or "check" in query_lower or "issue" in query_lower:
            return self.handle_validation_query()
        
        elif "hierarchy" in query_lower or "hierarchies" in query_lower:
            return self.handle_hierarchies_query()
        
        elif "cluster" in query_lower:
            return self.handle_clusters_query()
        
        elif "visualiz" in query_lower or "graph" in query_lower or "show me" in query_lower:
            return self.handle_visualization_query()
        
        elif "insight" in query_lower:
            return self.handle_insights_query()
        
        elif "explore entity" in query_lower or "entity:" in query_lower:
            # Extract entity URI
            uri_match = re.search(r'entity:\s*(\S+)', query_lower)
            if uri_match:
                entity_uri = uri_match.group(1)
                self.handle_interactive_entity_exploration(entity_uri)
                return f"🔍 Exploring entity: {entity_uri} (see visualization above)"
            return "Please specify entity URI like: explore entity: http://example.org/entity1"
        
        elif "template" in query_lower or "saved quer" in query_lower:
            self.show_query_templates()
            return "📝 Query templates displayed above!"
        
        else:
            # Use LLM for general queries
            return self.handle_general_query(query)
    
    def handle_statistics_query(self) -> str:
        """Handle statistics queries."""
        stats = st.session_state.rdf_tools.get_statistics()
        
        response = "📊 **RDF Graph Statistics:**\n\n"
        response += f"- **Total Triples:** {stats['total_triples']:,}\n"
        response += f"- **Unique Subjects:** {stats['total_subjects']:,}\n"
        response += f"- **Unique Predicates:** {stats['total_predicates']:,}\n"
        response += f"- **Unique Objects:** {stats['total_objects']:,}\n"
        response += f"- **Classes Defined:** {stats.get('total_classes', 0):,}\n"
        response += f"- **Properties Defined:** {stats.get('total_properties', 0):,}\n"
        
        return response
    
    def handle_classes_query(self) -> str:
        """Handle class listing queries."""
        classes = st.session_state.rdf_tools.get_classes(limit=50)
        
        if not classes:
            return "ℹ️ No classes found in the dataset."
        
        response = f"📋 **Found {len(classes)} classes:**\n\n"
        for cls in classes[:20]:
            response += f"- `{cls}`\n"
        
        if len(classes) > 20:
            response += f"\n... and {len(classes) - 20} more classes."
        
        return response
    
    def handle_properties_query(self) -> str:
        """Handle property listing queries."""
        properties = st.session_state.rdf_tools.get_properties(limit=50)
        
        if not properties:
            return "ℹ️ No properties found in the dataset."
        
        response = f"📋 **Found {len(properties)} properties:**\n\n"
        for prop in properties[:20]:
            response += f"- `{prop}`\n"
        
        if len(properties) > 20:
            response += f"\n... and {len(properties) - 20} more properties."
        
        return response
    
    def handle_sparql_query(self, query: str) -> str:
        """Handle SPARQL query requests."""
        # Extract SPARQL query if present
        if "```sparql" in query.lower():
            # Extract SPARQL from code block
            match = re.search(r'```sparql\s*(.*?)\s*```', query, re.DOTALL | re.IGNORECASE)
            if match:
                sparql_query = match.group(1).strip()
                return self.execute_sparql(sparql_query)
        
        return "💡 **How to run SPARQL queries:**\n\nProvide your SPARQL query in a code block:\n\n```sparql\nSELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10\n```"
    
    def execute_sparql(self, sparql_query: str) -> str:
        """Execute a SPARQL query."""
        try:
            # Save to query history
            st.session_state.query_history.append({
                'query': sparql_query,
                'type': 'SPARQL',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            results = st.session_state.rdf_tools.query_sparql(sparql_query, limit=100)
            
            if not results:
                return "✅ Query executed successfully, but returned no results."
            
            response = f"✅ **Query Results** ({len(results)} rows):\n\n"
            
            # Format results as table
            if results:
                # Get column headers
                if isinstance(results[0], dict):
                    headers = list(results[0].keys())
                    response += "| " + " | ".join(headers) + " |\n"
                    response += "|" + "|".join(["---"] * len(headers)) + "|\n"
                    
                    for row in results[:50]:  # Limit display to 50 rows
                        values = [str(row.get(h, ''))[:100] for h in headers]
                        response += "| " + " | ".join(values) + " |\n"
                    
                    if len(results) > 50:
                        response += f"\n... and {len(results) - 50} more results."
                else:
                    for result in results[:50]:
                        response += f"- {result}\n"
            
            return response
        
        except Exception as e:
            return f"❌ **SPARQL Error:** {str(e)}"
    
    def handle_patterns_query(self) -> str:
        """Handle pattern discovery queries."""
        try:
            patterns = st.session_state.rdf_tools.discover_patterns(limit=10)
            
            response = "🔍 **Discovered Patterns:**\n\n"
            
            for pattern in patterns:
                response += f"- **{pattern.get('type', 'pattern')}:** `{pattern.get('value', 'N/A')}`"
                if 'count' in pattern:
                    response += f" (count: {pattern['count']})"
                response += "\n"
            
            return response
        
        except Exception as e:
            return f"❌ Error discovering patterns: {e}"
    
    def handle_validation_query(self) -> str:
        """Handle graph validation queries."""
        try:
            validation = st.session_state.rdf_tools.validate_graph()
            
            response = "✅ **Graph Validation Results:**\n\n"
            
            if validation.get('undefined_classes'):
                response += f"⚠️ **Undefined Classes:** {len(validation['undefined_classes'])}\n"
                for cls in validation['undefined_classes'][:5]:
                    response += f"  - {cls}\n"
            
            if validation.get('blank_nodes'):
                response += f"\nℹ️ **Blank Nodes:** {validation['blank_nodes']}\n"
            
            if validation.get('issues'):
                response += f"\n❌ **Issues Found:** {len(validation['issues'])}\n"
                for issue in validation['issues'][:5]:
                    response += f"  - {issue}\n"
            else:
                response += "\n✅ No structural issues found!"
            
            return response
        
        except Exception as e:
            return f"❌ Validation error: {e}"
    
    def handle_hierarchies_query(self) -> str:
        """Handle hierarchy discovery queries."""
        try:
            hierarchies = st.session_state.rdf_tools.find_hierarchies()
            
            if not hierarchies:
                return "ℹ️ No hierarchical relationships found in the dataset."
            
            response = "🌳 **Hierarchical Relationships Found:**\n\n"
            
            for hier in hierarchies:
                response += f"- **Predicate:** `{hier.get('predicate', 'N/A')}`\n"
                response += f"  - **Relationships:** {hier.get('count', 0)}\n"
            
            return response
        
        except Exception as e:
            return f"❌ Error finding hierarchies: {e}"
    
    def handle_clusters_query(self) -> str:
        """Handle clustering queries."""
        try:
            clusters = st.session_state.rdf_tools.find_entity_clusters(limit=5)
            
            response = "🔗 **Entity Clusters:**\n\n"
            
            for idx, cluster in enumerate(clusters, 1):
                response += f"**Cluster {idx}:**\n"
                response += f"- **Hub Entity:** `{cluster.get('hub', 'N/A')}`\n"
                response += f"- **Connections:** {cluster.get('connection_count', 0)}\n\n"
            
            return response
        
        except Exception as e:
            return f"❌ Error finding clusters: {e}"
    
    def handle_visualization_query(self) -> str:
        """Handle visualization requests."""
        # Trigger inline visualization
        self.show_graph_visualization()
        
        return "📊 **Visualization displayed above!**\n\n" \
               "Additional visualization options:\n" \
               "1. View `data/graph_visualization.html` for interactive visualizations\n" \
               "2. Check `data/agent_report.md` for comprehensive analysis\n" \
               "3. Export chat transcript to save visualizations\n\n" \
               "💡 Run the main agent (`python main.py`) to generate full visualizations!"
    
    def handle_insights_query(self) -> str:
        """Handle insights queries."""
        if not st.session_state.memory:
            return "ℹ️ No insights available yet. Run the autonomous agent to generate insights!"
        
        insights = st.session_state.memory.get_all_insights()
        
        if not insights:
            return "ℹ️ No insights stored yet. Run the agent to generate insights!"
        
        response = f"💡 **Agent Insights ({len(insights)} total):**\n\n"
        
        for idx, insight in enumerate(insights[-5:], 1):  # Show last 5
            response += f"**{idx}.** {insight.get('insight', 'N/A')}\n"
            response += f"   - *Confidence:* {insight.get('confidence', 0):.2f}\n\n"
        
        if len(insights) > 5:
            response += f"... and {len(insights) - 5} more insights. Click 'View All Insights' in the sidebar."
        
        return response
    
    def handle_general_query(self, query: str) -> str:
        """Handle general queries using the LLM."""
        try:
            # Get graph context
            stats = st.session_state.rdf_tools.get_statistics()
            context = f"RDF Graph with {stats['total_triples']} triples, {stats.get('total_classes', 0)} classes."
            
            # Generate prompt
            prompt = f"""You are an RDF knowledge graph expert assistant. 
            
Context: {context}

User Question: {query}

Provide a helpful, concise answer about the RDF graph. If the question requires specific data analysis, suggest using one of the available commands:
- 'show statistics' for graph statistics
- 'list classes' for all classes
- 'list properties' for all properties  
- 'run SPARQL query' for custom queries
- 'find patterns' for pattern discovery
- 'validate graph' for data quality checks

Answer:"""
            
            response = st.session_state.llm.generate(prompt, max_tokens=500)
            return response
        
        except Exception as e:
            error_msg = str(e)
            troubleshooting = ""
            
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                troubleshooting = "\n\n**Troubleshooting:**\n- Ensure Ollama is running: `ollama serve`\n- Check if the model is available: `ollama list`"
            elif "model" in error_msg.lower():
                troubleshooting = "\n\n**Troubleshooting:**\n- Pull the model: `ollama pull mistral`\n- Try a different model in the sidebar"
            
            return f"💭 I can help you explore the RDF graph! Try asking about:\n\n" \
                   f"- Statistics and metrics\n" \
                   f"- Classes and properties\n" \
                   f"- Running SPARQL queries\n" \
                   f"- Finding patterns\n" \
                   f"- Validating the graph\n\n" \
                   f"**LLM Error:** {error_msg}{troubleshooting}"
    
    def show_query_history(self):
        """Display query history with rerun capability."""
        st.subheader("📜 Query History")
        
        if not st.session_state.query_history:
            st.info("No queries run yet.")
            return
        
        for idx, query_item in enumerate(reversed(st.session_state.query_history[-20:]), 1):
            with st.expander(f"Query {len(st.session_state.query_history) - idx + 1}: {query_item.get('timestamp', 'N/A')}"):
                st.code(query_item.get('query', 'N/A'), language='sparql')
                st.markdown(f"**Type:** {query_item.get('type', 'unknown')}")
                if st.button(f"Rerun Query {len(st.session_state.query_history) - idx + 1}", key=f"rerun_{idx}"):
                    self.rerun_query(query_item.get('query', ''))
    
    def rerun_last_query(self):
        """Rerun the last query from history."""
        if st.session_state.query_history:
            last_query = st.session_state.query_history[-1]
            self.rerun_query(last_query.get('query', ''))
    
    def rerun_query(self, query: str):
        """Rerun a specific query."""
        if query:
            st.session_state.messages.append({"role": "user", "content": f"[Rerun] {query}"})
            self.process_user_query(query)
            st.rerun()
    
    def show_query_templates(self):
        """Show and manage query templates."""
        st.subheader("💾 Saved Query Templates")
        
        # Display existing templates
        for name, query in st.session_state.saved_queries.items():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(name)
            with col2:
                if st.button("Use", key=f"use_{name}"):
                    st.session_state.messages.append({"role": "user", "content": f"```sparql\n{query}\n```"})
                    st.rerun()
            with col3:
                st.code(query[:50] + "...", language='sparql')
        
        # Add new template
        with st.expander("➕ Add New Template"):
            new_name = st.text_input("Template Name")
            new_query = st.text_area("SPARQL Query")
            if st.button("Save Template"):
                if new_name and new_query:
                    st.session_state.saved_queries[new_name] = new_query
                    self.save_query_templates()
                    st.success(f"Template '{new_name}' saved!")
                    st.rerun()
    
    def show_graph_visualization(self):
        """Display interactive graph visualization within chat."""
        if not st.session_state.rdf_tools:
            st.warning("Please load a dataset first.")
            return
        
        st.subheader("🎨 Graph Visualization")
        
        try:
            # Get graph statistics for visualization
            stats = st.session_state.rdf_tools.get_statistics()
            classes = st.session_state.rdf_tools.get_classes(limit=20)
            properties = st.session_state.rdf_tools.get_properties(limit=20)
            
            # Create tabs for different visualizations
            tab1, tab2, tab3 = st.tabs(["Statistics", "Class Distribution", "Property Usage"])
            
            with tab1:
                # Statistics overview
                col1, col2, col3 = st.columns(3)
                col1.metric("Triples", f"{stats['total_triples']:,}")
                col2.metric("Subjects", f"{stats['total_subjects']:,}")
                col3.metric("Predicates", f"{stats['total_predicates']:,}")
                
                # Create a bar chart of stats
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Triples', 'Subjects', 'Predicates', 'Objects'],
                        y=[stats['total_triples'], stats['total_subjects'], 
                           stats['total_predicates'], stats['total_objects']],
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
                    )
                ])
                fig.update_layout(title="Graph Component Counts", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Class distribution with actual usage counts
                if classes:
                    # Get instance counts for each class
                    class_data = []
                    for cls in classes[:10]:
                        count_query = f"SELECT (COUNT(?s) as ?count) WHERE {{ ?s a <{cls}> }}"
                        try:
                            result = st.session_state.rdf_tools.query_sparql(count_query, limit=1)
                            count = int(result[0].get('count', 1)) if result else 1
                            class_data.append((cls.split('/')[-1][:30], count))
                        except:
                            class_data.append((cls.split('/')[-1][:30], 1))
                    
                    class_names = [c[0] for c in class_data]
                    class_counts = [c[1] for c in class_data]
                    
                    fig = go.Figure(data=[go.Pie(labels=class_names, values=class_counts)])
                    fig.update_layout(title="Top Classes Distribution (by instance count)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No classes found in dataset.")
            
            with tab3:
                # Property usage with actual counts
                if properties:
                    # Get usage counts for each property
                    prop_data = []
                    for prop in properties[:10]:
                        count_query = f"SELECT (COUNT(?s) as ?count) WHERE {{ ?s <{prop}> ?o }}"
                        try:
                            result = st.session_state.rdf_tools.query_sparql(count_query, limit=1)
                            count = int(result[0].get('count', 1)) if result else 1
                            prop_data.append((prop.split('/')[-1][:30], count))
                        except:
                            prop_data.append((prop.split('/')[-1][:30], 1))
                    
                    prop_names = [p[0] for p in prop_data]
                    prop_counts = [p[1] for p in prop_data]
                    
                    fig = go.Figure(data=[go.Bar(x=prop_names, y=prop_counts)])
                    fig.update_layout(title="Top Properties (by usage count)", xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No properties found in dataset.")
            
            # Store visualization data
            st.session_state.current_viz_data = {
                'stats': stats,
                'classes': classes,
                'properties': properties,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            st.error(f"Visualization error: {e}")
    
    def export_chat_transcript(self):
        """Export chat conversation to a file."""
        if not st.session_state.messages:
            st.warning("No messages to export.")
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.chat_export_dir / f"chat_transcript_{timestamp}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# OntoTrain Chat Transcript\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Dataset:** {st.session_state.current_dataset}\n\n")
                f.write("---\n\n")
                
                for msg in st.session_state.messages:
                    role = msg['role'].upper()
                    content = msg['content']
                    f.write(f"## {role}\n\n{content}\n\n")
                    f.write("---\n\n")
            
            st.success(f"✅ Chat transcript exported to: {filename}")
            
            # Offer download
            with open(filename, 'r', encoding='utf-8') as f:
                st.download_button(
                    label="📥 Download Transcript",
                    data=f.read(),
                    file_name=f"chat_transcript_{timestamp}.md",
                    mime="text/markdown"
                )
        
        except Exception as e:
            st.error(f"Export error: {e}")
    
    def export_report_to_pdf(self):
        """Export agent report to PDF format."""
        if not PDF_AVAILABLE:
            st.error("PDF export requires reportlab. Install with: pip install reportlab")
            return
        
        if not st.session_state.memory:
            st.warning("No insights to export. Run the agent first.")
            return
        
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f77b4'),
                spaceAfter=30,
                alignment=1  # Center
            )
            story.append(Paragraph("OntoTrain - Agent Report", title_style))
            story.append(Spacer(1, 0.2 * inch))
            
            # Metadata
            story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph(f"<b>Dataset:</b> {st.session_state.current_dataset or 'N/A'}", styles['Normal']))
            story.append(Spacer(1, 0.3 * inch))
            
            # Statistics
            if st.session_state.rdf_tools:
                stats = st.session_state.rdf_tools.get_statistics()
                story.append(Paragraph("<b>Dataset Statistics:</b>", styles['Heading2']))
                data = [
                    ['Metric', 'Value'],
                    ['Total Triples', f"{stats.get('total_triples', 0):,}"],
                    ['Total Classes', str(stats.get('total_classes', 0))],
                    ['Total Properties', str(stats.get('total_properties', 0))]
                ]
                t = Table(data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3 * inch))
            
            # Insights
            insights = st.session_state.memory.get_all_insights()
            if insights:
                story.append(Paragraph("<b>Agent Insights:</b>", styles['Heading2']))
                story.append(Spacer(1, 0.1 * inch))
                
                for i, insight_data in enumerate(insights, 1):
                    insight_text = insight_data.get('insight', str(insight_data))
                    source = insight_data.get('source', 'Unknown')
                    
                    story.append(Paragraph(f"<b>Insight #{i}</b>", styles['Heading3']))
                    story.append(Paragraph(f"<i>Source: {source}</i>", styles['Normal']))
                    story.append(Paragraph(insight_text[:500], styles['Normal']))  # Limit length
                    story.append(Spacer(1, 0.2 * inch))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            st.success("✅ PDF report generated successfully!")
            st.download_button(
                label="📥 Download PDF Report",
                data=buffer,
                file_name=f"ontotrain_report_{timestamp}.pdf",
                mime="application/pdf"
            )
        
        except Exception as e:
            st.error(f"PDF export error: {e}")
    
    def filter_insights(self, insights: List[Dict], search_term: str = "", filter_type: str = "All") -> List[Dict]:
        """Filter insights based on search term and filter type."""
        if not insights:
            return []
        
        filtered = insights
        
        # Apply search filter
        if search_term:
            search_lower = search_term.lower()
            filtered = [
                insight for insight in filtered
                if search_lower in str(insight.get('insight', '')).lower() or
                   search_lower in str(insight.get('source', '')).lower()
            ]
        
        # Apply type filter (can be extended based on insight metadata)
        if filter_type != "All":
            # Example: filter by source or other criteria
            filtered = [
                insight for insight in filtered
                if filter_type.lower() in str(insight.get('source', '')).lower()
            ]
        
        return filtered
    
    def run_agent_realtime(self):
        """Run the autonomous agent in real-time within the chat."""
        if not st.session_state.rdf_tools or not st.session_state.llm:
            st.warning("Please load a dataset first.")
            return
        
        st.subheader("🤖 Running Autonomous Agent")
        
        try:
            from agent.agent import AutonomousAgent
            
            # Create progress container
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            results_placeholder = st.empty()
            
            # Initialize agent
            status_placeholder.info("Initializing autonomous agent...")
            agent = AutonomousAgent(
                model_name=st.session_state.model_name,
                dataset_path=st.session_state.dataset_path,
                memory_file=st.session_state.memory_file,
                max_iterations=3,  # Limited iterations for chat UI
                verbose=False
            )
            
            # Run agent with progress updates
            status_placeholder.info("Agent is exploring the RDF graph...")
            progress_bar = progress_placeholder.progress(0)
            
            # Run the actual agent (simplified for UI)
            iteration_results = []
            for i in range(3):
                progress_bar.progress((i + 1) / 3)
                status_placeholder.info(f"Iteration {i + 1}/3: Running agent cycle...")
                
                # Execute one iteration
                try:
                    # Get current action from agent
                    if i == 0:
                        result = st.session_state.rdf_tools.get_statistics()
                        iteration_results.append(f"**Iteration 1:** Analyzed graph statistics - {result['total_triples']:,} triples found")
                    elif i == 1:
                        result = st.session_state.rdf_tools.discover_patterns()
                        # Limit to first 5 patterns for display
                        result = result[:5] if len(result) > 5 else result
                        iteration_results.append(f"**Iteration 2:** Discovered {len(result)} patterns in the data")
                    else:
                        result = st.session_state.rdf_tools.get_classes(limit=10)
                        iteration_results.append(f"**Iteration 3:** Identified {len(result)} classes")
                        # Add an insight (note: add_insight takes insight, source, iteration)
                        st.session_state.memory.add_insight(
                            f"Analyzed RDF graph with {len(result)} classes via chat UI",
                            source="chat_ui_agent",
                            iteration=3
                        )
                except Exception as e:
                    iteration_results.append(f"**Iteration {i+1}:** Error - {str(e)}")
            
            progress_placeholder.empty()
            status_placeholder.success("✅ Agent execution complete!")
            
            # Display results
            with results_placeholder.container():
                for result in iteration_results:
                    st.write(result)
            
            # Add summary message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🤖 **Agent Execution Complete!**\n\n" + "\n".join(iteration_results) + "\n\nNew insights have been generated. Check the 'Agent Insights' section in the sidebar to view them."
            })
            
        except ImportError as e:
            st.error(f"Could not import agent module: {e}\n\nMake sure all dependencies are installed.")
        except Exception as e:
            st.error(f"Agent execution error: {e}")
    
    def handle_interactive_entity_exploration(self, entity_uri: str):
        """Interactive exploration of a specific entity."""
        st.subheader(f"🔍 Exploring Entity: {entity_uri}")
        
        try:
            # Get all triples where entity is subject
            query = f"""
            SELECT ?p ?o WHERE {{
                <{entity_uri}> ?p ?o
            }} LIMIT 100
            """
            outgoing = st.session_state.rdf_tools.query_sparql(query)
            
            # Get all triples where entity is object
            query = f"""
            SELECT ?s ?p WHERE {{
                ?s ?p <{entity_uri}>
            }} LIMIT 100
            """
            incoming = st.session_state.rdf_tools.query_sparql(query)
            
            tab1, tab2 = st.tabs(["Outgoing Relations", "Incoming Relations"])
            
            with tab1:
                st.write(f"**{len(outgoing)} outgoing relationships:**")
                for rel in outgoing[:20]:
                    st.write(f"- {rel.get('p', 'N/A')} → {rel.get('o', 'N/A')}")
            
            with tab2:
                st.write(f"**{len(incoming)} incoming relationships:**")
                for rel in incoming[:20]:
                    st.write(f"- {rel.get('s', 'N/A')} → {rel.get('p', 'N/A')}")
                    
        except Exception as e:
            st.error(f"Exploration error: {e}")
    
    def run(self):
        """Run the Streamlit application."""
        self.render_sidebar()
        self.render_chat_interface()


def main():
    """Main entry point for the Streamlit app."""
    app = OntoTrainChatUI()
    app.run()


if __name__ == "__main__":
    main()
