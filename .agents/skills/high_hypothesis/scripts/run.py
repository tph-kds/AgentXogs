#!/usr/bin/env python3
"""
Hypothesis Generation Skill - Generate plausible root cause hypotheses
"""

from __future__ import annotations
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from src.agentX.shared.utils import load_config


def generate_hypothesis_for_anomaly(anomaly: Dict, metrics: Dict, context: Dict) -> List[Dict]:
    """Generate hypotheses for a single anomaly"""
    anomaly_type = anomaly.get("type", "UNKNOWN")
    evidence = anomaly.get("evidence", "")
    metrics_data = anomaly.get("metrics", {})
    
    hypotheses = []
    
    # Generate type-specific hypotheses
    if anomaly_type == "ERROR_RATE_SPIKE":
        hypotheses.extend([
            {
                "id": f"hyp_{anomaly.get('id')}_1",
                "anomaly_id": anomaly.get("id"),
                "hypothesis": "Recent code deployment may have introduced regression",
                "confidence": 0.75,
                "evidence": [
                    "Deployment timestamps often correlate with error spikes",
                    "Check deployment logs for the affected time period"
                ],
                "uncertainty_factors": [
                    "Correlation does not imply causation",
                    "Other factors may be involved"
                ],
                "suggested_validation": [
                    "Review deployment changelog",
                    "Check deployment metrics",
                    "Compare with staging environment"
                ]
            },
            {
                "id": f"hyp_{anomaly.get('id')}_2",
                "anomaly_id": anomaly.get("id"),
                "hypothesis": "Downstream service degradation may be causing cascading failures",
                "confidence": 0.60,
                "evidence": [
                    "Upstream dependencies can cause cascading errors",
                    "Check upstream service health"
                ],
                "uncertainty_factors": [
                    "No direct evidence of upstream issues",
                    "May require additional investigation"
                ],
                "suggested_validation": [
                    "Check upstream service logs",
                    "Review upstream service metrics",
                    "Contact upstream service owners"
                ]
            }
        ])
    
    elif anomaly_type == "NEW_ERROR_SIGNATURE":
        hypotheses.extend([
            {
                "id": f"hyp_{anomaly.get('id')}_1",
                "anomaly_id": anomaly.get("id"),
                "hypothesis": "New error signature indicates a code change or configuration issue",
                "confidence": 0.70,
                "evidence": [
                    "Error signature is new to the system",
                    "May indicate recent changes"
                ],
                "uncertainty_factors": [
                    "Error may have been present but undetected",
                    "Log parsing may have changed"
                ],
                "suggested_validation": [
                    "Search code history for related changes",
                    "Review recent configuration updates"
                ]
            }
        ])
    
    elif anomaly_type == "LATENCY_SPIKE":
        service = metrics_data.get("service", "unknown")
        hypotheses.extend([
            {
                "id": f"hyp_{anomaly.get('id')}_1",
                "anomaly_id": anomaly.get("id"),
                "hypothesis": f"Database query performance degradation affecting {service}",
                "confidence": 0.65,
                "evidence": [
                    f"{service} depends on database",
                    "Latency spike suggests query or connection issues"
                ],
                "uncertainty_factors": [
                    "No direct database metrics available",
                    "May be network-related"
                ],
                "suggested_validation": [
                    "Review slow query logs",
                    "Check database connection pool metrics"
                ]
            }
        ])
    
    else:
        # Generic hypothesis
        hypotheses.append({
            "id": f"hyp_{anomaly.get('id')}_1",
            "anomaly_id": anomaly.get("id"),
            "hypothesis": "System anomaly detected requiring further investigation",
            "confidence": 0.50,
            "evidence": [evidence],
            "uncertainty_factors": ["Insufficient data for confident diagnosis"],
            "suggested_validation": ["Collect more diagnostic information"]
        })
    
    return hypotheses


def run(input_data: Dict) -> Dict:
    """
    Main execution function for hypothesis generation
    
    Args:
        input_data: {
            "anomalies": [...],
            "metrics": {...},
            "context": {
                "recent_deployments": [...],
                "dependencies": [...]
            }
        }
    
    Returns:
        {
            "hypotheses": [...],
            "total_hypotheses": int
        }
    """
    anomalies = input_data.get("anomalies", [])
    metrics = input_data.get("metrics", {})
    context = input_data.get("context", {})
    
    all_hypotheses = []
    
    for anomaly in anomalies:
        hypotheses = generate_hypothesis_for_anomaly(anomaly, metrics, context)
        all_hypotheses.extend(hypotheses)
    
    result = {
        "hypotheses": all_hypotheses,
        "total_hypotheses": len(all_hypotheses),
        "confidence_note": "These are plausible explanations, not confirmed root causes",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Save hypotheses
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "hypotheses.json", "w") as f:
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
# echo '{"anomalies": [...], "metrics": {...}}' | uv run .agents/skills/high_hypothesis/scripts/run.py
