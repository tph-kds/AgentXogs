#!/usr/bin/env python3
"""
Log Fetching Skill - Retrieve raw logs from configured sources
"""

from __future__ import annotations
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from src.agentX.shared.utils import parse_time_range, load_config


def fetch_from_filesystem(source: Dict, time_range: str, filters: Dict) -> List[Dict]:
    """Fetch logs from filesystem"""
    logs = []
    log_path = Path(source.get("path", "/var/log"))
    
    # For demo purposes, return sample logs
    # In production, this would read actual log files
    sample_logs = [
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "raw_message": "ERROR: Database connection timeout after 3000ms",
            "source": "auth-service",
            "metadata": {
                "host": "prod-01",
                "file": str(log_path / "app.log")
            }
        },
        {
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z",
            "raw_message": "WARN: High memory usage detected: 85%",
            "source": "auth-service",
            "metadata": {
                "host": "prod-01",
                "file": str(log_path / "app.log")
            }
        }
    ]
    
    return sample_logs


def fetch_from_elasticsearch(source: Dict, time_range: str, filters: Dict) -> List[Dict]:
    """Fetch logs from Elasticsearch"""
    # In production, this would connect to actual Elasticsearch
    # For demo, return sample data
    sample_logs = [
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "raw_message": f"ERROR: Authentication failed for user",
            "source": source.get("index", "unknown"),
            "metadata": {
                "host": source.get("host", "es.example.com"),
                "index": source.get("index")
            }
        }
    ]
    
    return sample_logs


def run(input_data: Dict) -> Dict:
    """
    Main execution function for log fetching
    
    Args:
        input_data: {
            "sources": [...],
            "time_range": "24h",
            "severity_filter": "ERROR",
            "max_logs": 10000
        }
    
    Returns:
        {
            "logs": [...],
            "total_fetched": int,
            "time_range": str,
            "sources_queried": int
        }
    """
    sources = input_data.get("sources", [])
    time_range = input_data.get("time_range", "24h")
    severity_filter = input_data.get("severity_filter")
    max_logs = input_data.get("max_logs", 10000)
    
    all_logs = []
    sources_queried = 0
    
    for source in sources:
        source_type = source.get("type", "filesystem")
        
        try:
            if source_type == "filesystem":
                logs = fetch_from_filesystem(source, time_range, {"severity": severity_filter})
            elif source_type == "elasticsearch":
                logs = fetch_from_elasticsearch(source, time_range, {"severity": severity_filter})
            else:
                print(f"Warning: Unknown source type '{source_type}', skipping", file=sys.stderr)
                continue
            
            all_logs.extend(logs)
            sources_queried += 1
            
            # Respect max_logs limit
            if len(all_logs) >= max_logs:
                all_logs = all_logs[:max_logs]
                break
                
        except Exception as e:
            print(f"Error fetching from {source_type}: {e}", file=sys.stderr)
            continue
    
    return {
        "logs": all_logs,
        "total_fetched": len(all_logs),
        "time_range": time_range,
        "sources_queried": sources_queried,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def main():
    """CLI entry point"""
    try:
        input_data = json.load(sys.stdin)
        output = run(input_data)
        print(json.dumps(output, indent=2))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
