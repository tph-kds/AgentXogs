#!/usr/bin/env python3
"""
Action Recommendations Skill - Generate actionable remediation steps
"""

from __future__ import annotations
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))


# Action templates for common anomaly types
ACTION_TEMPLATES = {
    "ERROR_RATE_SPIKE": {
        "investigation": [
            "Check recent deployments that might have introduced the regression",
            "Review application logs for the affected time period",
            "Verify database connection pool configuration",
            "Check for upstream service issues"
        ],
        "monitoring": [
            "Enable real-time error rate alerts",
            "Set up dashboard for error rate trends"
        ]
    },
    "NEW_ERROR_SIGNATURE": {
        "investigation": [
            "Search for this error signature in documentation",
            "Check if related code was recently modified",
            "Review error message for root cause hints"
        ],
        "alerting": [
            "Add alert rule for this new signature",
            "Configure notification to on-call team"
        ]
    },
    "LATENCY_SPIKE": {
        "investigation": [
            "Check database query performance",
            "Review network latency between services",
            "Analyze resource utilization (CPU, memory)"
        ],
        "optimization": [
            "Consider implementing caching layer",
            "Review and optimize slow queries",
            "Scale horizontally if needed"
        ]
    }
}


def generate_recommendation(anomaly: Dict, templates: Dict) -> Dict:
    """Generate recommendations for a single anomaly"""
    anomaly_type = anomaly.get("type", "UNKNOWN")
    severity = anomaly.get("severity", "medium")
    metrics = anomaly.get("metrics", {})
    evidence = anomaly.get("evidence", "")
    
    template = templates.get(anomaly_type, {
        "investigation": ["Investigate the anomaly further"],
        "monitoring": ["Set up monitoring for this metric"]
    })
    
    # Determine priority
    priority_scores = {"high": 3, "medium": 2, "low": 1}
    priority = severity if severity in priority_scores else "medium"
    
    # Generate category-specific recommendations
    recommendations = []
    
    for category, steps in template.items():
        for step in steps:
            recommendations.append({
                "category": category,
                "action": step,
                "rationale": f"Related to {anomaly_type}: {evidence[:100]}",
                "estimated_time": estimate_time(category)
            })
    
    return {
        "id": f"rec_{anomaly.get('id', 'unknown')}",
        "priority": priority,
        "related_anomaly": anomaly.get("id"),
        "anomaly_type": anomaly_type,
        "actions": recommendations[:4]  # Limit to 4 actions
    }


def estimate_time(category: str) -> str:
    """Estimate time for remediation category"""
    times = {
        "investigation": "15-30 minutes",
        "monitoring": "10 minutes",
        "alerting": "10 minutes",
        "optimization": "1-2 hours"
    }
    return times.get(category, "30 minutes")


def run(input_data: Dict) -> Dict:
    """
    Main execution function for recommendations
    
    Args:
        input_data: {
            "anomalies": [...],
            "hypotheses": [...],
            "templates": "config/action_templates.yaml"
        }
    
    Returns:
        {
            "recommendations": [...],
            "priority_summary": {...}
        }
    """
    anomalies = input_data.get("anomalies", [])
    hypotheses = input_data.get("hypotheses", [])
    template_file = input_data.get("templates", "config/action_templates.yaml")
    
    # Load templates
    templates = load_config(template_file)
    if templates is None:
        templates = ACTION_TEMPLATES
    
    all_recommendations = []
    
    for anomaly in anomalies:
        rec = generate_recommendation(anomaly, templates)
        all_recommendations.append(rec)
    
    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    all_recommendations.sort(key=lambda x: priority_order.get(x.get("priority"), 1))
    
    # Create priority summary
    priority_counts = {"high": 0, "medium": 0, "low": 0}
    for rec in all_recommendations:
        p = rec.get("priority", "medium")
        if p in priority_counts:
            priority_counts[p] += 1
    
    result = {
        "recommendations": all_recommendations,
        "total_recommendations": len(all_recommendations),
        "priority_summary": priority_counts,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Save recommendations
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "recommendations.json", "w") as f:
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
# echo '{"anomalies": [...]}' | uv run .agents/skills/recommend_actions/scripts/run.py
