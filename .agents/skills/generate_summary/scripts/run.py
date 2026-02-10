#!/usr/bin/env python3
"""
Summary Generation Skill - Create human-readable log analysis reports
"""

from __future__ import annotations
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))


SUMMARY_TEMPLATE = """# System Log Summary – {environment}
**Time Range**: Last {time_range}
**Generated**: {generated_at}

## Executive Summary
{summary_icon} **{anomaly_count} {anomaly_word} detected**{anomaly_note}

## Key Metrics
- **Total Events**: {total_events:,}
- **Error Rate**: {error_rate:.1f}% ({baseline_comparison})
- **Errors**: {error_count:,}

## Detected Anomalies
{anomalies_section}

## Service Breakdown
{service_section}

## Top Error Signatures
{top_signatures_section}
"""


def format_severity_icon(severity: str) -> str:
    """Get icon for severity level"""
    icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    return icons.get(severity.lower(), "⚪")


def format_anomaly_count(count: int) -> str:
    """Format anomaly count with appropriate word"""
    if count == 0:
        return "no anomalies"
    elif count == 1:
        return "1 anomaly"
    else:
        return f"{count} anomalies"


def generate_executive_summary(metrics: Dict, anomalies: List[Dict]) -> str:
    """Generate executive summary text"""
    error_rate = metrics.get("error_rate", 0) * 100
    baseline = metrics.get("baseline_comparison", {})
    baseline_str = baseline.get("error_rate_change", "0%")
    
    if not anomalies:
        return f"System is healthy. Error rate is {error_rate:.1f}% ({baseline_str} from baseline)."
    
    high_count = sum(1 for a in anomalies if a.get("severity") == "high")
    medium_count = sum(1 for a in anomalies if a.get("severity") == "medium")
    
    parts = []
    if high_count > 0:
        parts.append(f"{high_count} high-severity issue(s)")
    if medium_count > 0:
        parts.append(f"{medium_count} medium-severity issue(s)")
    
    return f"Issues detected: {', '.join(parts)}. Error rate: {error_rate:.1f}% ({baseline_str})"


def generate_anomalies_section(anomalies: List[Dict]) -> str:
    """Generate the anomalies section of the summary"""
    if not anomalies:
        return "No anomalies detected. System appears healthy."
    
    sections = []
    for i, anomaly in enumerate(anomalies, 1):
        severity = anomaly.get("severity", "unknown")
        icon = format_severity_icon(severity)
        anomaly_type = anomaly.get("type", "Unknown")
        evidence = anomaly.get("evidence", "No evidence provided")
        confidence = anomaly.get("confidence", 0) * 100
        
        sections.append(f"""### {icon} {severity.upper()}: {anomaly_type}
- **Confidence**: {confidence:.0f}%
- **Evidence**: {evidence}
""")
    
    return "\n".join(sections)


def generate_service_section(metrics: Dict) -> str:
    """Generate service breakdown section"""
    service_stats = metrics.get("service_stats", {})
    
    if not service_stats:
        return "No service data available."
    
    sections = []
    for service, stats in service_stats.items():
        error_rate = stats.get("error_rate", 0) * 100
        p95 = stats.get("p95_latency_ms", 0)
        errors = stats.get("errors", 0)
        total = stats.get("total", 0)
        
        sections.append(f"""### {service}
- **Total**: {total:,} events
- **Errors**: {errors:,} ({error_rate:.1f}%)
- **P95 Latency**: {p95}ms
""")
    
    return "\n".join(sections)


def generate_top_signatures_section(metrics: Dict) -> str:
    """Generate top error signatures section"""
    top_signatures = metrics.get("top_signatures", [])
    
    if not top_signatures:
        return "No error signatures detected."
    
    lines = []
    for i, sig in enumerate(top_signatures, 1):
        sig_name = sig.get("signature", "Unknown")
        count = sig.get("count", 0)
        percentage = sig.get("percentage", 0)
        lines.append(f"{i}. **{sig_name}** - {count} occurrences ({percentage:.1f}%)")
    
    return "\n".join(lines)


def run(input_data: Dict) -> Dict:
    """
    Main execution function for summary generation
    
    Args:
        input_data: {
            "metrics": {...},
            "anomalies": [...],
            "hypotheses": [...],
            "time_range": "24h",
            "environment": "production"
        }
    
    Returns:
        {
            "summary": str,
            "metrics_summary": {...}
        }
    """
    metrics = input_data.get("metrics", {})
    anomalies = input_data.get("anomalies", [])
    hypotheses = input_data.get("hypotheses", [])
    time_range = input_data.get("time_range", "24h")
    environment = input_data.get("environment", "production")
    
    # Generate sections
    executive_summary = generate_executive_summary(metrics, anomalies)
    anomalies_section = generate_anomalies_section(anomalies)
    service_section = generate_service_section(metrics)
    signatures_section = generate_top_signatures_section(metrics)
    
    # Add hypotheses if available
    hypotheses_section = ""
    if hypotheses:
        hypotheses_lines = ["## Possible Explanations"]
        for i, hyp in enumerate(hypotheses, 1):
            conf = hyp.get("confidence", 0) * 100
            text = hyp.get("hypothesis", "")
            evidence = hyp.get("evidence", [])
            hypotheses_lines.append(f"\n💡 **Hypothesis {i}** (Confidence: {conf:.0f}%)\n{text}")
            if evidence:
                hypotheses_lines.append("- " + "\n- ".join(evidence[:3]))
        hypotheses_section = "\n".join(hypotheses_lines)
    
    # Fill template
    summary = SUMMARY_TEMPLATE.format(
        environment=environment,
        time_range=time_range,
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        summary_icon="✅" if not anomalies else "⚠️",
        anomaly_count=len(anomalies),
        anomaly_word="anomalies" if len(anomalies) != 1 else "anomaly",
        anomaly_note="" if not anomalies else " requiring attention",
        total_events=metrics.get("total_events", 0),
        error_rate=(metrics.get("error_rate", 0) * 100),
        baseline_comparison=metrics.get("baseline_comparison", {}).get("error_rate_change", "0%"),
        error_count=metrics.get("error_count", 0),
        anomalies_section=anomalies_section,
        service_section=service_section,
        top_signatures_section=signatures_section
    )
    
    # Append hypotheses if present
    if hypotheses_section:
        summary += "\n" + hypotheses_section
    
    result = {
        "summary": summary,
        "metrics_summary": {
            "total_events": metrics.get("total_events", 0),
            "error_count": metrics.get("error_count", 0),
            "error_rate": metrics.get("error_rate", 0),
            "anomaly_count": len(anomalies)
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Save summary
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "summary.md", "w") as f:
        f.write(summary)
    
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
# echo '{"metrics": {...}, "anomalies": [...]}' | uv run .agents/skills/generate_summary/scripts/run.py
