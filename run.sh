#!/bin/bash
# OntoTrain Launcher Script
# Convenience script for running OntoTrain components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Function to check if Ollama is running
check_ollama() {
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_color $YELLOW "⚠️  Warning: Ollama doesn't seem to be running."
        print_color $YELLOW "   Start Ollama with: ollama serve"
        return 1
    else
        print_color $GREEN "✓ Ollama is running"
        return 0
    fi
}

# Function to show usage
show_usage() {
    cat << EOF
OntoTrain - Autonomous RDF AI Agent Launcher

Usage: ./run.sh [command] [options]

Commands:
    agent              Run the autonomous agent (default)
    chat               Launch the interactive chat UI
    create-sample      Create a sample RDF dataset
    help               Show this help message

Agent Options:
    --model NAME       Ollama model to use (default: mistral)
    --dataset PATH     Path to RDF dataset (default: data/dataset.rdf)
    --iterations N     Max iterations (default: 10)
    --goal "TEXT"      Exploration goal
    --verbose          Enable verbose output

Examples:
    ./run.sh agent                                    # Run agent with defaults
    ./run.sh agent --model llama2 --iterations 5      # Custom configuration
    ./run.sh chat                                     # Launch chat UI
    ./run.sh create-sample                            # Create sample dataset

EOF
}

# Main script logic
main() {
    print_color $BLUE "═══════════════════════════════════════════════════"
    print_color $BLUE "    🚂 OntoTrain - RDF AI Agent Launcher"
    print_color $BLUE "═══════════════════════════════════════════════════"
    echo

    # Get command
    COMMAND="${1:-agent}"
    if [ $# -gt 0 ]; then
        shift
    fi

    case "$COMMAND" in
        agent)
            check_ollama || true
            print_color $GREEN "▶ Running Autonomous Agent..."
            echo
            python main.py "$@"
            ;;
        
        chat)
            check_ollama || true
            print_color $GREEN "▶ Launching Chat UI..."
            echo
            streamlit run app.py
            ;;
        
        create-sample)
            print_color $GREEN "▶ Creating Sample Dataset..."
            echo
            python main.py --create-sample-dataset
            ;;
        
        help)
            show_usage
            ;;
        
        *)
            print_color $RED "❌ Unknown command: $COMMAND"
            echo
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
