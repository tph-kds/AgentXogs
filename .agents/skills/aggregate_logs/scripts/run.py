#!/usr/bin/env python3
"""
Log Aggregation Skill - Transform normalized events into metrics and patterns
"""

from __future__ import annotations
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional

# Ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from src.agentX.shared.utils import parse_time_range


def compute_hourly_trends(events: List[Dict], time_range: str) -> List[Dict]:
    """Compute hourly trend data from events"""
    trends = []
    
    # Parse time range to get window
    window_minutes = parse_time_range(time_range)
    if window_minutes is None:
        window_minutes = 24 * 60  # Default 24 hours
    
    # Group events by hour
    hourly_events = defaultdict(list)
    for event in events:
        try:
            timestamp = event.get("timestamp", "")
            if timestamp:
                # Parse timestamp (simplified)
                hour_key = timestamp[:13] + ":00:00"
                hourly_events[hour_key].append(event)
        except Exception:
            continue
    
    # Create trend entries
    for hour in sorted(hourly_events.keys())[:24]:  # Max 24 hours
        hour_events = hourly_events[hour]
        error_count = sum(1 for e in hour_events if e.get("level") in ["ERROR", "FATAL", "CRITICAL"])
        trends.append({
            "hour": hour,
            "total_events": len(hour_events),
            "error_count": error_count,
            "error_rate": error_count / len(hour_events) if hour_events else 0
        })
    
    return trends


def compute_service_stats(events: List[Dict]) -> Dict[str, Dict]:
    """Compute statistics per service"""
    service_stats = defaultdict(lambda: {
        "total": 0,
        "errors": 0,
        "error_rate": 0.0,
        "p50_latency_ms": 0,
        "p95_latency_ms": 0,
        "p99_latency_ms": 0,
        "latencies": []
    })
    
    for event in events:
        service = event.get("service", "unknown")
        level = event.get("level", "INFO")
        latency = event.get("metadata", {}).get("latency_ms", 0)
        
        stats = service_stats[service]
        stats["total"] += 1
        if level in ["ERROR", "FATAL", "CRITICAL"]:
            stats["errors"] += 1
        if latency > 0:
            stats["latencies"].append(latency)
    
    # Compute final statistics
    for service, stats in service_stats.items():
        stats["error_rate"] = stats["errors"] / stats["total"] if stats["total"] > 0 else 0
        
        # Compute percentiles
        latencies = sorted(stats["latencies"])
        if latencies:
            n = len(latencies)
            stats["p50_latency_ms"] = latencies[int(n * 0.50)] if n > 0 else 0
            stats["p95_latency_ms"] = latencies[int(n * 0.95)] if n > 0 else 0
            stats["p99_latency_ms"] = latencies[int(n * 0.99)] if n > 0 else 0
        
        # Remove latencies list to reduce output size
        del stats["latencies"]
    
    return dict(service_stats)


def compute_top_signatures(events: List[Dict], limit: int = 10) -> List[Dict]:
    """Compute top error signatures by count"""
    signature_counts = defaultdict(int)
    signature_messages = {}
    
    for event in events:
        level = event.get("level", "INFO")
        if level in ["ERROR", "FATAL", "CRITICAL"]:
            signature = event.get("signature", "UNKNOWN")
            signature_counts[signature] += 1
            if signature not in signature_messages:
                signature_messages[signature] = event.get("message", "")
    
    total_errors = sum(signature_counts.values())
    
    # Sort by count
    sorted_signatures = sorted(signature_counts.items(), key=lambda x: x[1], reverse=True)
    
    result = []
    for signature, count in sorted_signatures[:limit]:
        percentage = (count / total_errors * 100) if total_errors > 0 else 0
        result.append({
            "signature": signature,
            "count": count,
            "percentage": round(percentage, 1),
            "example_message": signature_messages.get(signature, "")[:200]
        })
    
    return result


def compute_baseline_comparison(current_metrics: Dict, baseline_file: str = "config/baseline_metrics.json") -> Optional[Dict]:
    """Compare current metrics with historical baseline"""
    baseline_path = Path(baseline_file)
    
    if not baseline_path.exists():
        return None
    
    try:
        with open(baseline_path, 'r') as f:
            baseline = json.load(f)
        
        current_error_rate = current_metrics.get("error_rate", 0)
        baseline_error_rate = baseline.get("error_rate", 0)
        
        current_volume = current_metrics.get("total_events", 0)
        baseline_volume = baseline.get("total_events", 0)
        
        # Calculate changes
        error_rate_change = ((current_error_rate - baseline_error_rate) / baseline_error_rate * 100) if baseline_error_rate > 0 else 0
        volume_change = ((current_volume - baseline_volume) / baseline_volume * 100) if baseline_volume > 0 else 0
        
        return {
            "error_rate_change": f"{'+' if error_rate_change > 0 else ''}{round(error_rate_change, 1)}%",
            "volume_change": f"{'+' if volume_change > 0 else ''}{round(volume_change, 1)}%",
            "baseline_error_rate": baseline_error_rate,
            "baseline_total_events": baseline_volume
        }
    except Exception as e:
        print(f"Warning: Could not load baseline: {e}", file=sys.stderr)
        return None


def run(input_data: Dict) -> Dict:
    """
    Main execution function for log aggregation
    
    Args:
        input_data: {
            "events": [...],
            "baseline_file": "config/baseline_metrics.json",
            "aggregation_window": "1h"
        }
    
    Returns:
        {
            "total_events": int,
            "error_count": int,
            "error_rate": float,
            "time_range": str,
            "top_signatures": [...],
            "service_stats": {...},
            "hourly_trends": [...],
            "baseline_comparison": {...}
        }
    """
    events = input_data.get("events", [])
    baseline_file = input_data.get("baseline_file", "config/baseline_metrics.json")
    time_range = input_data.get("time_range", "24h")
    
    if not events:
        return {
            "total_events": 0,
            "error_count": 0,
            "error_rate": 0.0,
            "time_range": time_range,
            "top_signatures": [],
            "service_stats": {},
            "hourly_trends": [],
            "baseline_comparison": None
        }
    
    # Count total and errors
    total_events = len(events)
    error_count = sum(1 for e in events if e.get("level") in ["ERROR", "FATAL", "CRITICAL"])
    error_rate = error_count / total_events if total_events > 0 else 0
    
    # Compute metrics
    top_signatures = compute_top_signatures(events)
    service_stats = compute_service_stats(events)
    hourly_trends = compute_hourly_trends(events, time_range)
    
    # Current metrics for comparison
    current_metrics = {
        "total_events": total_events,
        "error_count": error_count,
        "error_rate": error_rate
    }
    
    baseline_comparison = compute_baseline_comparison(current_metrics, baseline_file)
    
    result = {
        "total_events": total_events,
        "error_count": error_count,
        "error_rate": round(error_rate, 4),
        "time_range": time_range,
        "top_signatures": top_signatures,
        "service_stats": service_stats,
        "hourly_trends": hourly_trends,
        "baseline_comparison": baseline_comparison,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Save metrics to output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "metrics.json", "w") as f:
        json.dump(result, f, indent=2)
    
    return result


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

# Example usage:
# cat events.json | uv run .agents/skills/aggregate_logs/scripts/run.py
# echo '{"events": [...], "time_range": "24h"}' | uv run .agents/skills/aggregate_logs/scripts/run.py
