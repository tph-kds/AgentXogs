# !/usr/bin/env python3
"""
Script to discover log sources based on environment and service name.
"""

from __future__ import annotations
import sys
import json
from pathlib import Path
from typing import Dict, List

# Ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from src.agentX.shared.utils import *

def run(input: Dict) -> Dict:
    environment = input.get("environment", "production")
    service = input.get("service_name")

    sources = []

    if service:
        sources.append({
            "type": "elasticsearch",
            "index": f"{service}-*",
            "environment": environment
        })
    else:
        sources.append({
            "type": "filesystem",
            "path": "/var/log",
            "environment": environment
        })

    return {"sources": sources}


def main():
    input_data = json.load(open(0))
    output = run(input_data)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

    # Example usage:
    # uv run .agents/skills/logsource_discovery/scripts/run.py --input '{"environment": "staging", "service_name": "auth-service"}'
