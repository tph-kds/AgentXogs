# Sample Data Files

This directory contains sample data for testing the Live Logs Insights pipeline.

## Files

| File | Description | Pipeline Stage |
|------|-------------|----------------|
| `sample_logs.json` | Raw log entries | fetch_logs → parse_logs |
| `sample_parsed_events.json` | Structured log events | aggregate_logs → detect_anomalies |
| `sample_metrics.json` | Aggregated metrics | detect_anomalies → summary → recommend |

## Usage

### Activate Environment

```bash
conda activate ags_env
source .venv/bin/activate
```

### Run Full Pipeline with Sample Logs

```bash
# Extract logs and run through pipeline
cat metadata/sample_logs.json | jq '.logs' | \
  uv run .agents/skills/parse_logs/scripts/run.py | \
  jq '{events: .events}' | \
  uv run .agents/skills/aggregate_logs/scripts/run.py | \
  uv run .agents/skills/detect_anomalies/scripts/run.py
```

### Run Individual Skills

```bash
# Parse logs
cat metadata/sample_logs.json | jq '.logs' | \
  uv run .agents/skills/parse_logs/scripts/run.py > /tmp/parsed_events.json

# Aggregate metrics
cat /tmp/parsed_events.json | \
  uv run .agents/skills/aggregate_logs/scripts/run.py > /tmp/metrics.json

# Detect anomalies
cat /tmp/metrics.json | \
  uv run .agents/skills/detect_anomalies/scripts/run.py

# Generate summary
cat /tmp/metrics.json | \
  uv run .agents/skills/generate_summary/scripts/run.py
```

### Full Pipeline with Sample Data

```bash
# Run the complete end-to-end pipeline with sample input
echo '{
  "time_range": "1h",
  "environment": "production",
  "service_name": "auth-service",
  "severity_filter": "ERROR"
}' | uv run .agents/skills/livelogs_insights/scripts/run.py
```

## Sample Data Overview

The sample logs simulate:
- **auth-service** in production
- **15 log events** over 1 hour
- **60% error rate** (intentionally high to trigger anomaly detection)
- **Key error signatures**: DB_TIMEOUT, AUTH_FAILED, RATE_LIMIT, OOM

## Expected Output

After running the pipeline, check:
- `output/insights/summary.md` - Human-readable report
- `output/insights/anomalies.json` - Detected anomalies
- `output/insights/recommendations.json` - Action items
- `output/insights/metrics.json` - Aggregated metrics
