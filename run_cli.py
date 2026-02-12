#!/usr/bin/env python3
"""
AgentX CLI Launcher - Run the AgentX interactive CLI

Usage:
    python run_cli.py                    # Show help
    python run_cli.py --help             # Show help
    python run_cli.py -i                 # Interactive mode
    python run_cli.py status             # Show system status
    python run_cli.py analyze            # Run log analysis
    python run_cli.py quickcheck         # Quick health check
    python run_cli.py discover           # Discover log sources
    python run_cli.py export --format json
    python run_cli.py --version

Or with uv (if installed):
    uv run run_cli.py --help
    uv run run_cli.py analyze

Or after pip install:
    agentx --help
"""

import sys
from pathlib import Path

# Ensure repo root is importable
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agentX.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
