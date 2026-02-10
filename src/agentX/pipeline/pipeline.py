#!/usr/bin/env python3
"""
AgentX Log Analysis Pipeline - End-to-end log processing pipeline.

Fetches logs -> Parses events -> Aggregates metrics -> Detects anomalies -> Generates summary.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Ensure repo root is importable BEFORE any other imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agentX.shared.utils import PipelineError, load_config, load_yaml_config


def run_skill(skill_path: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """Run a skill script via subprocess and return JSON result."""
    result = subprocess.run(
        ["uv", "run", skill_path],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    if result.returncode != 0:
        raise PipelineError(f"Skill {skill_path} failed: {result.stderr}")
    return json.loads(result.stdout)


def step_fetch_logs(sources: list[dict[str, Any]], time_range: str, max_logs: int) -> dict[str, Any]:
    """Step 1: Fetch logs from configured sources."""
    print("\n[1/5] Fetching logs...")
    input_data = {
        "sources": sources,
        "time_range": time_range,
        "max_logs": max_logs
    }
    result = run_skill(".agents/skills/fetch_logs/scripts/run.py", input_data)
    print(f"  ✓ Fetched {result.get('total_fetched', 0)} logs")
    return result


def step_parse_logs(logs: list[dict[str, Any]], patterns_file: str) -> dict[str, Any]:
    """Step 2: Parse and normalize log entries."""
    print("\n[2/5] Parsing logs...")
    input_data = {
        "logs": logs,
        "parsing_rules": patterns_file
    }
    result = run_skill(".agents/skills/parse_logs/scripts/run.py", input_data)
    print(f"  ✓ Parsed {result.get('parsed_count', 0)} events")
    return result


def step_aggregate_metrics(events: list[dict[str, Any]], time_range: str, baseline_file: str) -> dict[str, Any]:
    """Step 3: Aggregate events into metrics."""
    print("\n[3/5] Computing metrics...")
    input_data = {
        "events": events,
        "time_range": time_range,
        "baseline_file": baseline_file
    }
    result = run_skill(".agents/skills/aggregate_logs/scripts/run.py", input_data)
    error_rate = result.get("error_rate", 0) * 100
    print(f"  ✓ Processed {result.get('total_events', 0)} events, {error_rate:.1f}% error rate")
    return result


def step_detect_anomalies(metrics: dict[str, Any], thresholds_file: str) -> dict[str, Any]:
    """Step 4: Detect anomalies in metrics."""
    print("\n[4/5] Detecting anomalies...")
    input_data = {
        "metrics": metrics,
        "thresholds": thresholds_file
    }
    result = run_skill(".agents/skills/detect_anomalies/scripts/run.py", input_data)
    count = result.get("total_anomalies", 0)
    print(f"  ✓ Found {count} anomaly/anomalies")
    return result


def step_generate_summary(
    metrics: dict[str, Any],
    anomalies: list[dict[str, Any]],
    hypotheses: list[dict[str, Any]],
    time_range: str,
    environment: str
) -> dict[str, Any]:
    """Step 5: Generate summary report."""
    print("\n[5/5] Generating summary...")
    input_data = {
        "metrics": metrics,
        "anomalies": anomalies,
        "hypotheses": hypotheses,
        "time_range": time_range,
        "environment": environment
    }
    result = run_skill(".agents/skills/generate_summary/scripts/run.py", input_data)
    print(f"  ✓ Summary written to output/summary.md")
    return result


def run_pipeline(config: dict[str, Any]) -> dict[str, Any]:
    """Execute the complete log analysis pipeline."""
    time_range = config.get("time_range", "24h")
    max_logs = config.get("max_logs", 10000)
    environment = config.get("environment", "production")

    log_sources = load_yaml_config(config.get("log_sources_file", "src/agentX/config/log_sources.yaml"))
    if log_sources is None:
        log_sources = {"sources": []}
    sources = log_sources.get("sources", [])

    patterns_file = config.get("log_patterns_file", "src/agentX/config/log_patterns.yaml")
    baseline_file = config.get("baseline_metrics_file", "src/agentX/config/baseline_metrics.json")
    thresholds_file = config.get("anomaly_thresholds_file", "src/agentX/config/anomaly_thresholds.yaml")

    fetch_result = step_fetch_logs(sources, time_range, max_logs)
    logs = fetch_result.get("logs", [])
    if not logs:
        print("\n⚠ No logs fetched. Aborting.")
        return {"status": "aborted", "reason": "no_logs"}

    parse_result = step_parse_logs(logs, patterns_file)
    events = parse_result.get("events", [])
    if not events:
        print("\n⚠ No events parsed. Aborting.")
        return {"status": "aborted", "reason": "no_events"}

    metrics = step_aggregate_metrics(events, time_range, baseline_file)

    anomaly_result = step_detect_anomalies(metrics, thresholds_file)
    anomalies = anomaly_result.get("anomalies", [])

    print("\n[H] Generating hypotheses...")
    if anomalies:
        hypothesis_result = run_skill(".agents/skills/high_hypothesis/scripts/run.py", {
            "anomalies": anomalies,
            "metrics": metrics,
            "context": {}
        })
        hypotheses = hypothesis_result.get("hypotheses", [])
        print(f"  ✓ Generated {len(hypotheses)} hypotheses")
    else:
        hypotheses = []
        print("  ✓ No anomalies to analyze")

    summary_result = step_generate_summary(metrics, anomalies, hypotheses, time_range, environment)

    return {
        "status": "success",
        "logs_fetched": len(logs),
        "events_parsed": len(events),
        "anomalies_detected": len(anomalies),
        "metrics": metrics
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AgentX Log Analysis Pipeline")
    parser.add_argument("--config", default="config.json", help="Config file path")
    return parser.parse_args(argv or sys.argv[1:])


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        config = load_config(Path(args.config))
    except FileNotFoundError:
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON in config: {exc}", file=sys.stderr)
        return 1

    if config is None:
        print(f"Error: Config file not found or is empty: {args.config}", file=sys.stderr)
        return 1

    print("\n" + "=" * 50)
    print("AgentX Log Analysis Pipeline")
    print("=" * 50)

    try:
        result = run_pipeline(config)
    except PipelineError as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1

    print("\n" + "=" * 50)
    if result.get("status") == "success":
        print("Pipeline completed successfully!")
        print(f"  Logs: {result.get('logs_fetched', 0)}")
        print(f"  Events: {result.get('events_parsed', 0)}")
        print(f"  Anomalies: {result.get('anomalies_detected', 0)}")
        return 0
    else:
        print(f"Pipeline aborted: {result.get('reason', 'unknown')}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
