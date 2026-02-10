#!/usr/bin/env python3
"""
Anomaly Detection Skill - Detect abnormal patterns in log metrics
"""

from __future__ import annotations
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from src.agentX.shared.utils import load_config


# Default anomaly thresholds
DEFAULT_THRESHOLDS = {
    "error_rate_spike": {
        "threshold": 2.0,
        "severity": "high",
        "min_absolute_rate": 0.01
    },
    "error_count_spike": {
        "threshold": 3.0,
        "severity": "high",
        "min_absolute_count": 10
    },
    "new_error_signature": {
        "min_occurrences": 5,
        "severity": "medium"
    },
    "latency_spike": {
        "threshold_ms": 3000,
        "severity": "medium"
    }
}


def load_thresholds(threshold_file: str = "config/anomaly_thresholds.yaml") -> Dict:
    """Load anomaly detection thresholds from config"""
    thresholds = load_config(threshold_file)
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    else:
        for key, value in DEFAULT_THRESHOLDS.items():
            if key not in thresholds:
                thresholds[key] = value
    return thresholds


def detect_error_spikes(metrics: Dict, thresholds: Dict) -> List[Dict]:
    """Detect error rate spikes compared to baseline"""
    anomalies = []
    baseline = metrics.get("baseline_comparison", {})
    error_rate = metrics.get("error_rate", 0)
    error_count = metrics.get("error_count", 0)
    
    error_rate_change_str = baseline.get("error_rate_change", "0%")
    try:
        error_rate_change = float(error_rate_change_str.replace("%", "").replace("+", ""))
    except ValueError:
        error_rate_change = 0
    
    spike_config = thresholds.get("error_rate_spike", {})
    if error_rate_change >= spike_config.get("threshold", 2.0) * 100 and error_rate >= spike_config.get("min_absolute_rate", 0.01):
        anomalies.append({
            "id": f"anom_err_spike_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "type": "ERROR_RATE_SPIKE",
            "severity": spike_config.get("severity", "high"),
            "confidence": min(0.95, 0.5 + (error_rate_change / 200)),
            "evidence": f"Error rate increased {error_rate_change_str} vs baseline ({error_rate*100:.1f}%)",
            "metrics": {
                "current_error_rate": error_rate,
                "baseline_error_rate": baseline.get("baseline_error_rate", 0),
                "change_factor": error_rate_change / 100 + 1 if error_rate_change > 0 else 1
            },
            "time_detected": datetime.utcnow().isoformat() + "Z"
        })
    return anomalies


def detect_new_error_signatures(metrics: Dict, thresholds: Dict) -> List[Dict]:
    """Detect new error signatures"""
    anomalies = []
    top_signatures = metrics.get("top_signatures", [])
    new_config = thresholds.get("new_error_signature", {})
    min_occurrences = new_config.get("min_occurrences", 5)
    
    for sig in top_signatures:
        sig_name = sig.get("signature", "")
        count = sig.get("count", 0)
        if count >= min_occurrences and sig_name not in ["GENERIC_ERROR"]:
            anomalies.append({
                "id": f"anom_new_sig_{sig_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "type": "NEW_ERROR_SIGNATURE",
                "severity": new_config.get("severity", "medium"),
                "confidence": min(0.90, 0.6 + (count / 100)),
                "evidence": f"Error signature '{sig_name}' detected with {count} occurrences",
                "metrics": {"signature": sig_name, "count": count, "percentage": sig.get("percentage", 0)},
                "time_detected": datetime.utcnow().isoformat() + "Z"
            })
    return anomalies


def detect_latency_issues(metrics: Dict, thresholds: Dict) -> List[Dict]:
    """Detect unusual latency patterns"""
    anomalies = []
    service_stats = metrics.get("service_stats", {})
    latency_config = thresholds.get("latency_spike", {})
    threshold_ms = latency_config.get("threshold_ms", 3000)
    
    for service, stats in service_stats.items():
        p95 = stats.get("p95_latency_ms", 0)
        if p95 >= threshold_ms:
            anomalies.append({
                "id": f"anom_latency_{service}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "type": "LATENCY_SPIKE",
                "severity": latency_config.get("severity", "medium"),
                "confidence": min(0.85, 0.5 + (p95 / threshold_ms / 2)),
                "evidence": f"P95 latency for {service} is {p95}ms (threshold: {threshold_ms}ms)",
                "metrics": {"service": service, "p95_latency_ms": p95, "p99_latency_ms": stats.get("p99_latency_ms", 0)},
                "time_detected": datetime.utcnow().isoformat() + "Z"
            })
    return anomalies


def run(input_data: Dict) -> Dict:
    """
    Main execution function for anomaly detection
    
    Args:
        input_data: {
            "metrics": {...},
            "thresholds": "config/anomaly_thresholds.yaml",
            "baseline": {...}
        }
    
    Returns:
        {
            "anomalies": [...],
            "total_anomalies": int,
            "detection_time": str
        }
    """
    metrics = input_data.get("metrics", {})
    threshold_file = input_data.get("thresholds", "config/anomaly_thresholds.yaml")
    
    thresholds = load_thresholds(threshold_file)
    
    all_anomalies = []
    all_anomalies.extend(detect_error_spikes(metrics, thresholds))
    all_anomalies.extend(detect_new_error_signatures(metrics, thresholds))
    all_anomalies.extend(detect_latency_issues(metrics, thresholds))
    
    result = {
        "anomalies": all_anomalies,
        "total_anomalies": len(all_anomalies),
        "detection_time": datetime.utcnow().isoformat() + "Z"
    }
    
    # Save anomalies
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "anomalies.json", "w") as f:
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
# echo '{"metrics": {...}}' | uv run .agents/skills/detect_anomalies/scripts/run.py
