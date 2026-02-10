#!/bin/bash
# AgentX Pipeline Runner
# Executes the complete log analysis pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Activate conda environment and venv, then run the pipeline
eval "$(conda shell.bash hook)"
conda activate ags_env/
source .venv/bin/activate

uv run src/agentX/pipeline/pipeline.py "$@"
