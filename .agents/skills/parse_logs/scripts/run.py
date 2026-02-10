#!/usr/bin/env python3
"""
Log Parsing and Normalization Skill - Convert raw logs to structured events
"""

from __future__ import annotations
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from src.agentX.shared.utils import extract_error_signature, parse_timestamp


# Common log patterns
LOG_PATTERNS = {
    "standard": re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+"
        r"(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\s*:?\s+"
        r"(?P<message>.*)"
    ),
    "simple": re.compile(
        r"(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\s*:?\s+"
        r"(?P<message>.*)"
    ),
}


def extract_error_signature_from_message(message: str, level: str) -> str:
    """Extract error signature from log message"""
    if level not in ["ERROR", "FATAL", "CRITICAL"]:
        return "INFO"
    
    # Common error patterns
    if "timeout" in message.lower():
        return "TIMEOUT"
    if "connection" in message.lower() and ("refused" in message.lower() or "failed" in message.lower()):
        return "CONNECTION_ERROR"
    if "database" in message.lower() and "timeout" in message.lower():
        return "DB_TIMEOUT"
    if "auth" in message.lower() and "fail" in message.lower():
        return "AUTH_FAILED"
    if "rate limit" in message.lower():
        return "RATE_LIMIT"
    if "out of memory" in message.lower() or "oom" in message.lower():
        return "OOM"
    if "null pointer" in message.lower() or "nullpointerexception" in message.lower():
        return "NULL_POINTER"
    
    # Generic error
    return "GENERIC_ERROR"


def extract_metadata(message: str) -> Dict[str, Any]:
    """Extract metadata from log message"""
    metadata = {}
    
    # Extract latency
    latency_match = re.search(r"(\d+)\s*ms", message)
    if latency_match:
        metadata["latency_ms"] = int(latency_match.group(1))
    
    # Extract error codes
    error_code_match = re.search(r"E\d{4}", message)
    if error_code_match:
        metadata["error_code"] = error_code_match.group(0)
    
    # Extract percentages
    percent_match = re.search(r"(\d+)%", message)
    if percent_match:
        metadata["percentage"] = int(percent_match.group(1))
    
    return metadata


def parse_log_entry(log: Dict) -> Dict:
    """Parse a single log entry into normalized format"""
    raw_message = log.get("raw_message", "")
    source = log.get("source", "unknown")
    log_metadata = log.get("metadata", {})
    
    # Try to parse with patterns
    parsed = None
    for pattern_name, pattern in LOG_PATTERNS.items():
        match = pattern.match(raw_message)
        if match:
            parsed = match.groupdict()
            break
    
    if not parsed:
        # Fallback parsing
        parsed = {
            "timestamp": log.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "level": "INFO",
            "message": raw_message
        }
    
    # Normalize level
    level = parsed.get("level", "INFO").upper()
    if level == "WARNING":
        level = "WARN"
    
    # Extract signature
    signature = extract_error_signature_from_message(parsed["message"], level)
    
    # Extract metadata
    extracted_metadata = extract_metadata(parsed["message"])
    extracted_metadata.update(log_metadata)
    
    return {
        "timestamp": parsed.get("timestamp", log.get("timestamp")),
        "service": source,
        "level": level,
        "signature": signature,
        "message": parsed["message"],
        "metadata": extracted_metadata
    }


def run(input_data: Dict) -> Dict:
    """
    Main execution function for log parsing
    
    Args:
        input_data: {
            "logs": [...],
            "parsing_rules": "config/log_patterns.yaml"
        }
    
    Returns:
        {
            "events": [...],
            "parsed_count": int,
            "failed_count": int
        }
    """
    logs = input_data.get("logs", [])
    
    events = []
    failed = []
    
    for log in logs:
        try:
            event = parse_log_entry(log)
            events.append(event)
        except Exception as e:
            failed.append({
                "log": log,
                "error": str(e)
            })
    
    # Save failed parses if any
    if failed:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        with open(output_dir / "parsing_failures.json", "w") as f:
            json.dump(failed, f, indent=2)
    
    return {
        "events": events,
        "parsed_count": len(events),
        "failed_count": len(failed),
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
