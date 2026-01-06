@echo off
REM OntoTrain Launcher Script for Windows
REM Convenience script for running OntoTrain components

setlocal enabledelayedexpansion

echo ===================================================
echo     OntoTrain - RDF AI Agent Launcher
echo ===================================================
echo.

REM Get command
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=agent

if "%COMMAND%"=="agent" goto run_agent
if "%COMMAND%"=="chat" goto run_chat
if "%COMMAND%"=="create-sample" goto create_sample
if "%COMMAND%"=="help" goto show_help

echo ERROR: Unknown command: %COMMAND%
echo.
goto show_help

:run_agent
echo Running Autonomous Agent...
echo.
shift
python main.py %*
goto end

:run_chat
echo Launching Chat UI...
echo.
echo Make sure Ollama is running: ollama serve
echo.
streamlit run app.py
goto end

:create_sample
echo Creating Sample Dataset...
echo.
python main.py --create-sample-dataset
goto end

:show_help
echo OntoTrain - Autonomous RDF AI Agent Launcher
echo.
echo Usage: run.bat [command] [options]
echo.
echo Commands:
echo     agent              Run the autonomous agent (default)
echo     chat               Launch the interactive chat UI
echo     create-sample      Create a sample RDF dataset
echo     help               Show this help message
echo.
echo Agent Options:
echo     --model NAME       Ollama model to use (default: mistral)
echo     --dataset PATH     Path to RDF dataset (default: data/dataset.rdf)
echo     --iterations N     Max iterations (default: 10)
echo     --goal "TEXT"      Exploration goal
echo     --verbose          Enable verbose output
echo.
echo Examples:
echo     run.bat agent                                  Run agent with defaults
echo     run.bat agent --model llama2 --iterations 5    Custom configuration
echo     run.bat chat                                   Launch chat UI
echo     run.bat create-sample                          Create sample dataset
echo.
goto end

:end
endlocal
