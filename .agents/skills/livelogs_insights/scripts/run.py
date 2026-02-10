#!/usr/bin/env python3
"""
Live Logs Insights Orchestrator Skill - End-to-end log analysis pipeline
"""

from __future__ import annotations
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))


def log_step(step_name: str, message: str):
    """Log a pipeline step with timestamp"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{step_name}] {message}", file=sys.stderr)


def run_pipeline_step(skill_path: str, input_data: Dict) -> Dict:
    """Run a single skill step and return output"""
    result = subprocess.run(
        ["uv", "run", skill_path],
        input=json.dumps(input_data),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Step failed: {result.stderr}")
    return json.loads(result.stdout)


def run(input_data: Dict) -> Dict:
    """
    Main execution function for the complete log analysis pipeline
    """
    time_range = input_data.get("time_range", "24h")
    environment = input_data.get("environment", "production")
    service_name = input_data.get("service_name")
    severity_filter = input_data.get("severity_filter", "ERROR")
    
    log_step("START", f"Starting pipeline for {environment}/{service_name} ({time_range})")
    
    output_dir = Path("output/insights")
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    
    # Step 1: Log Source Discovery
    log_step("1/8", "Discovering log sources...")
    try:
        sources_result = run_pipeline_step(
            ".agents/skills/logsource_discovery/scripts/run.py",
            {"environment": environment, "service_name": service_name, "time_range": time_range}
        )
        results["sources"] = sources_result.get("sources", [])
    except Exception as e:
        log_step("1/8", f"Discovery failed: {e}")
        results["sources"] = [{"type": "filesystem", "path": "/var/log", "environment": environment}]
    
    # Step 2: Fetch Logs
    log_step("2/8", "Fetching logs...")
    try:
        fetch_result = run_pipeline_step(
            ".agents/skills/fetch_logs/scripts/run.py",
            {"sources": results["sources"], "time_range": time_range, "severity_filter": severity_filter}
        )
        results["logs"] = fetch_result.get("logs", [])
        results["total_logs"] = fetch_result.get("total_fetched", 0)
    except Exception as e:
        log_step("2/8", f"Fetch failed: {e}")
        results["logs"] = []
        results["total_logs"] = 0
    
    # Step 3: Parse Logs
    log_step("3/8", "Parsing logs...")
    try:
        parse_result = run_pipeline_step(
            ".agents/skills/parse_logs/scripts/run.py",
            {"logs": results["logs"]}
        )
        results["events"] = parse_result.get("events", [])
    except Exception as e:
        log_step("3/8", f"Parse failed: {e}")
        results["events"] = []
    
    # Step 4: Aggregate Logs
    log_step("4/8", "Aggregating metrics...")
    try:
        metrics_result = run_pipeline_step(
            ".agents/skills/aggregate_logs/scripts/run.py",
            {"events": results["events"], "time_range": time_range}
        )
        results["metrics"] = metrics_result
    except Exception as e:
        log_step("4/8", f"Aggregation failed: {e}")
        results["metrics"] = {"total_events": 0, "error_count": 0, "error_rate": 0, "top_signatures": []}
    
    # Step 5: Detect Anomalies
    log_step("5/8", "Detecting anomalies...")
    try:
        anomaly_result = run_pipeline_step(
            ".agents/skills/detect_anomalies/scripts/run.py",
            {"metrics": results["metrics"]}
        )
        results["anomalies"] = anomaly_result.get("anomalies", [])
    except Exception as e:
        log_step("5/8", f"Detection failed: {e}")
        results["anomalies"] = []
    
    # Step 6: Generate Hypotheses (optional)
    log_step("6/8", "Generating hypotheses...")
    try:
        if results["anomalies"]:
            hypothesis_result = run_pipeline_step(
                ".agents/skills/high_hypothesis/scripts/run.py",
                {"anomalies": results["anomalies"], "metrics": results["metrics"]}
            )
            results["hypotheses"] = hypothesis_result.get("hypotheses", [])
        else:
            results["hypotheses"] = []
    except Exception as e:
        log_step("6/8", f"Hypothesis generation failed: {e}")
        results["hypotheses"] = []
    
    # Step 7: Generate Summary
    log_step("7/8", "Generating summary...")
    try:
        summary_result = run_pipeline_step(
            ".agents/skills/generate_summary/scripts/run.py",
            {
                "metrics": results["metrics"],
                "anomalies": results["anomalies"],
                "hypotheses": results["hypotheses"],
                "time_range": time_range,
                "environment": environment
            }
        )
        results["summary"] = summary_result.get("summary", "")
    except Exception as e:
        log_step("7/8", f"Summary generation failed: {e}")
        results["summary"] = "# No summary available"
    
    # Step 8: Generate Recommendations
    log_step("8/8", "Generating recommendations...")
    try:
        rec_result = run_pipeline_step(
            ".agents/skills/recommend_actions/scripts/run.py",
            {"anomalies": results["anomalies"], "hypotheses": results["hypotheses"]}
        )
        results["recommendations"] = rec_result.get("recommendations", [])
    except Exception as e:
        log_step("8/8", f"Recommendation generation failed: {e}")
        results["recommendations"] = []
    
    # Save all outputs
    output_files = {}
    for filename, data in [
        ("summary.md", results.get("summary", "")),
        ("anomalies.json", results.get("anomalies", [])),
        ("recommendations.json", results.get("recommendations", [])),
        ("metrics.json", results.get("metrics", {}))
    ]:
        filepath = output_dir / filename
        if isinstance(data, str):
            filepath.write_text(data)
        else:
            filepath.write_text(json.dumps(data, indent=2))
        output_files[filename] = str(filepath)
    
    log_step("DONE", f"Pipeline complete. Outputs: {list(output_files.keys())}")
    
    return {
        "summary": results["summary"],
        "metrics": results["metrics"],
        "anomalies": results["anomalies"],
        "recommendations": results["recommendations"],
        "output_files": output_files
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

# Example usage:
# echo '{"environment": "production", "service_name": "auth-service"}' | uv run .agents/skills/livelogs_insights/scripts/run.py
