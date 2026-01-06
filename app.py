#!/usr/bin/env python3
"""
OntoTrain Chat UI - Interactive Streamlit interface for RDF exploration.

Provides a chat-based interface to interact with RDF data and agent insights.
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from agent.rdf_tools import RDFTools
from agent.llm import LocalLLM
from agent.memory import AgentMemory
from agent.visualizations import RDFVisualizer


# Page configuration
st.set_page_config(
    page_title="OntoTrain - RDF Explorer",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
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
""", unsafe_allow_html=True)


class OntoTrainChatUI:
    """Interactive chat interface for RDF exploration."""
    
    def __init__(self):
        """Initialize the chat UI."""
        self.initialize_session_state()
        self.load_configuration()
    
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
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def load_configuration(self):
        """Load default configuration."""
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.default_dataset = "data/dataset.rdf"
        self.memory_file = "data/agent_memory.json"
        self.default_model = "mistral"
    
    def render_sidebar(self):
        """Render the sidebar with configuration options."""
        st.sidebar.markdown("## 🚂 OntoTrain Configuration")
        
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
        
        # Insights section
        st.sidebar.markdown("### 💡 Agent Insights")
        if st.session_state.memory:
            insights = st.session_state.memory.get_all_insights()
            st.sidebar.metric("Total Insights", len(insights))
            
            if st.sidebar.button("📋 View All Insights", use_container_width=True):
                self.show_insights_modal()
        
        # Export options
        st.sidebar.markdown("### 📥 Export")
        if st.sidebar.button("💾 Export to JSON-LD", use_container_width=True):
            self.export_data("json-ld")
        if st.sidebar.button("💾 Export to N-Triples", use_container_width=True):
            self.export_data("nt")
    
    def load_dataset(self, dataset_path: str, model_name: str):
        """Load the RDF dataset and initialize components."""
        try:
            with st.spinner("Loading dataset and initializing LLM..."):
                # Initialize RDF Tools
                st.session_state.rdf_tools = RDFTools(dataset_path)
                st.session_state.current_dataset = dataset_path
                
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
        """Display all agent insights in an expandable section."""
        if st.session_state.memory:
            insights = st.session_state.memory.get_all_insights()
            
            for idx, insight in enumerate(insights, 1):
                with st.expander(f"Insight {idx}: {insight.get('insight', 'N/A')[:50]}..."):
                    st.markdown(f"**Insight:** {insight.get('insight', 'N/A')}")
                    st.markdown(f"**Confidence:** {insight.get('confidence', 0):.2f}")
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
            import re
            match = re.search(r'```sparql\s*(.*?)\s*```', query, re.DOTALL | re.IGNORECASE)
            if match:
                sparql_query = match.group(1).strip()
                return self.execute_sparql(sparql_query)
        
        return "💡 **How to run SPARQL queries:**\n\nProvide your SPARQL query in a code block:\n\n```sparql\nSELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10\n```"
    
    def execute_sparql(self, sparql_query: str) -> str:
        """Execute a SPARQL query."""
        try:
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
        return "📊 **Visualization Options:**\n\n" \
               "1. Check the sidebar for basic statistics\n" \
               "2. Use the export functions to generate detailed reports\n" \
               "3. View `data/graph_visualization.html` for interactive visualizations\n" \
               "4. Check `data/agent_report.md` for comprehensive analysis\n\n" \
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
            return f"💭 I can help you explore the RDF graph! Try asking about:\n\n" \
                   f"- Statistics and metrics\n" \
                   f"- Classes and properties\n" \
                   f"- Running SPARQL queries\n" \
                   f"- Finding patterns\n" \
                   f"- Validating the graph\n\n" \
                   f"(LLM temporarily unavailable: {e})"
    
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
