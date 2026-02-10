# Live Log Insight Agent

An intelligent agent system for automated log analysis, anomaly detection, and actionable insights generation.

## Overview

This agent analyzes system and application logs to detect anomalies, extract patterns, and generate actionable summaries for operators and developers. It operates as a modular pipeline of specialized skills that work together to transform raw logs into meaningful insights.

## Core Capabilities

- **Automated Log Discovery**: Identifies log sources across environments
- **Intelligent Parsing**: Normalizes diverse log formats into structured events
- **Pattern Recognition**: Aggregates logs to identify trends and metrics
- **Anomaly Detection**: Detects spikes, new errors, and unusual behavior
- **Root Cause Analysis**: Generates plausible hypotheses for detected issues
- **Actionable Summaries**: Produces clear, human-readable reports
- **Smart Recommendations**: Suggests concrete next steps for operators

## When to Activate This Agent

The agent should be activated when:
- User requests log analysis or system health insights
- Daily/weekly operational summaries are needed
- Investigating incidents, spikes, or unusual behavior
- Monitoring production or staging systems
- Troubleshooting application errors

## Agent Workflow

The agent follows a sequential pipeline:

```
1. Log Source Discovery → Identify where logs live
2. Log Fetching → Retrieve raw logs
3. Log Parsing → Normalize into structured events
4. Log Aggregation → Compute metrics and patterns
5. Anomaly Detection → Identify abnormal behavior
6. Hypothesis Generation → Explain possible causes
7. Summary Generation → Create human-readable report
8. Action Recommendations → Suggest next steps
```

## Available Skills

### Core Skills (Required)
- `logsource_discovery` - Identify log storage locations
- `fetch_logs` - Retrieve logs from sources
- `parse_logs` - Normalize log formats
- `aggregate_logs` - Compute metrics and patterns
- `detect_anomalies` - Identify abnormal behavior
- `generate_summary` - Create readable summaries
- `recommend_actions` - Suggest next steps

### Advanced Skills (Optional)
- `high_hypothesis` - Generate root cause hypotheses

## Usage Examples

### Example 1: Daily Health Check
```
User: "Analyze today's production logs"

Agent:
1. Discovers production log sources
2. Fetches last 24h of logs
3. Parses and normalizes events
4. Aggregates metrics
5. Detects anomalies
6. Generates summary
7. Recommends actions

Output: Daily health report with anomalies and recommendations
```

### Example 2: Incident Investigation
```
User: "What happened with auth-service between 2pm and 3pm?"

Agent:
1. Discovers auth-service logs
2. Fetches logs for specified time window
3. Parses events
4. Aggregates error patterns
5. Detects spikes and new errors
6. Generates hypothesis
7. Provides investigation steps

Output: Incident analysis with timeline and root cause hypotheses
```

### Example 3: Service-Specific Analysis
```
User: "Check for errors in the payment service"

Agent:
1. Discovers payment service logs
2. Fetches recent logs
3. Parses and filters for errors
4. Aggregates error types
5. Detects patterns
6. Summarizes findings
7. Recommends fixes

Output: Error analysis with prioritized recommendations
```

## Configuration

The agent uses configuration from:
- `config/log_sources.yaml` - Log source definitions
- `config/anomaly_thresholds.yaml` - Detection thresholds
- `config/baseline_metrics.json` - Historical baselines

## Constraints

- Does not automatically fix issues
- Does not deploy changes
- Does not replace full observability tools
- Highlights uncertainty when confidence is low
- Never hallucinates root causes without evidence

## Mental Model

**The agent is not always reading logs.**

Instead, the agent:
1. Detects when log analysis is needed
2. Activates the appropriate skills
3. Runs the analysis pipeline
4. Interprets results
5. Summarizes findings
6. Recommends actions

Think of it as: **"An SRE junior that reads logs all day and gives you useful insights."**

## Output Format

The agent produces structured outputs including:
- Executive summary
- Key metrics and trends
- Detected anomalies with confidence levels
- Root cause hypotheses (when applicable)
- Prioritized action recommendations
- Supporting evidence and data

## Trust and Reliability

- All findings include confidence levels
- Uncertainty is explicitly communicated
- Hypotheses are clearly marked as possibilities, not facts
- Evidence is always provided for claims
- Missing data is acknowledged, never invented
