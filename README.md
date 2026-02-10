# AgentXogs - Live Log Insight Agent Skills System

<p align="center">
  <img src="docs/assets/logo.svg" alt="AgentX Logo" width="200"/>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#quickstart">Quick Start</a> •
  <a href="#skills">Skills</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#development">Development</a>
</p>

---

## Overview

AgentX is a modular, intelligent agent system for automated log analysis, anomaly detection, and actionable insights generation. It transforms raw logs into meaningful intelligence using a pipeline of specialized skills.

Think of it as **"An SRE junior that reads logs all day and gives you useful insights."**

## ✨ Features

- 🔍 **Automated Log Discovery** - Identifies log sources across environments
- 📊 **Intelligent Parsing** - Normalizes diverse log formats into structured events
- 📈 **Pattern Recognition** - Aggregates logs to identify trends and metrics
- 🚨 **Anomaly Detection** - Detects spikes, new errors, and unusual behavior
- 🔬 **Root Cause Analysis** - Generates plausible hypotheses for detected issues
- 📝 **Actionable Summaries** - Produces clear, human-readable reports
- 🎯 **Smart Recommendations** - Suggests concrete next steps for operators

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AgentX Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│  1. Log Source Discovery → 2. Fetch Logs → 3. Parse Events     │
│         ↓                    ↓                    ↓              │
│  4. Aggregate Metrics → 5. Detect Anomalies → 6. Generate      │
│         ↓                    ↓                    ↓              │
│  7. Hypothesis → 8. Summary → 9. Recommend Actions             │
└─────────────────────────────────────────────────────────────────┘
```

### Pipeline Flow

```
discover → fetch → parse → aggregate → detect → hypothesize → summarize → recommend
```

### Project Structure

```
agentx-skills/
├── .agents/                      # Agent definitions and skills
│   ├── AGENTS.md                 # Agent orchestration guide
│   └── skills/
│       ├── logsource_discovery/  # Identify log sources
│       ├── fetch_logs/           # Retrieve logs
│       ├── parse_logs/           # Parse and normalize
│       ├── aggregate_logs/       # Compute metrics
│       ├── detect_anomalies/     # Find anomalies
│       ├── generate_summary/     # Create reports
│       ├── recommend_actions/    # Suggest fixes
│       └── high_hypothesis/      # Root cause analysis
├── src/agentX/                   # Core pipeline code
│   ├── config/                   # Configuration modules
│   ├── pipeline/                 # Pipeline orchestration
│   └── shared/                   # Shared utilities
├── docs/                         # Documentation (MDX)
├── metadata/                     # Sample data and configs
├── output/                       # Pipeline outputs
├── scripts/                      # Utility scripts
├── config.json                   # Main configuration
└── pyproject.toml               # Project metadata
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- uv (package manager)
- conda (optional, for environment management)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd agentx-skills

# Install dependencies
uv sync

# Activate environment
source ags_env/bin/activate  # or: conda activate ags_env/
```

### Run the Pipeline

```bash
# Run with default config
uv run src/agentX/pipeline/pipeline.py

# Or using the shell script
./scripts/pipeline.sh

# With custom config
uv run src/agentX/pipeline/pipeline.py --config custom_config.json
```

### Quick Example

```python
from src.agentX.pipeline import run_pipeline

result = run_pipeline({
    "time_range": "24h",
    "max_logs": 10000,
    "environment": "production"
})

print(f"Anomalies detected: {result['anomalies_detected']}")
```

## 🔧 Skills

### Core Skills (Required)

| Skill | Responsibility |
|-------|----------------|
| `logsource_discovery` | Identify where logs live |
| `fetch_logs` | Retrieve logs from sources |
| `parse_logs` | Normalize logs into structured events |
| `aggregate_logs` | Compute metrics and patterns |
| `detect_anomalies` | Identify abnormal behavior |
| `generate_summary` | Create human-readable reports |
| `recommend_actions` | Suggest next steps |

### Advanced Skills (Optional)

| Skill | Responsibility |
|-------|----------------|
| `high_hypothesis` | Explain possible root causes |

### Skill Structure

Each skill follows a consistent structure:

```
skills/{skill_name}/
├── SKILL.md              # Skill documentation
├── scripts/
│   └── run.py           # Skill implementation
└── config/              # Skill-specific configs (optional)
```

## ⚙️ Configuration

### Main Config (`config.json`)

```json
{
  "project": "agentx-logs",
  "time_range": "24h",
  "max_logs": 10000,
  "environment": "production",
  "log_sources_file": "src/agentX/config/log_sources.yaml",
  "log_patterns_file": "src/agentX/config/log_patterns.yaml",
  "baseline_metrics_file": "src/agentX/config/baseline_metrics.json",
  "anomaly_thresholds_file": "src/agentX/config/anomaly_thresholds.yaml",
  "output_dir": "output"
}
```

### Configuration Files

| File | Purpose |
|------|---------|
| `log_sources.yaml` | Define log source locations and access patterns |
| `log_patterns.yaml` | Regex patterns for log parsing |
| `baseline_metrics.json` | Historical metrics for comparison |
| `anomaly_thresholds.yaml` | Thresholds for anomaly detection |

## 📖 Usage Examples

### Example 1: Daily Health Check

```bash
# Analyze production logs for the last 24 hours
uv run src/agentX/pipeline/pipeline.py
```

**Output:**
- Executive summary of system health
- Key metrics and trends
- Detected anomalies with confidence levels
- Prioritized action recommendations

### Example 2: Incident Investigation

```json
{
  "time_range": "2h",
  "service": "auth-service",
  "focus": "errors"
}
```

### Example 3: Custom Pipeline

```python
from src.agentX.pipeline.pipeline import run_pipeline

# Run specific steps
result = run_pipeline({
    "time_range": "1h",
    "max_logs": 5000,
    "environment": "staging"
})
```

## 📊 Sample Data

The `metadata/` directory contains sample data for testing:

- `sample_logs.json` - Raw log entries
- `sample_parsed_events.json` - Parsed structured events
- `sample_metrics.json` - Aggregated metrics
- `config.json` - Sample configuration

## 🛡️ Constraints & Safety

AgentX is designed with explicit constraints:

- ❌ Does not automatically fix issues
- ❌ Does not deploy changes
- ❌ Does not replace full observability tools
- ✅ Highlights uncertainty when confidence is low
- ✅ Never hallucinates root causes without evidence
- ✅ All findings include confidence levels

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Quick Start](docs/pages/quickstart.mdx)
- [Architecture](docs/pages/concepts/architecture.mdx)
- [Skills Guide](docs/pages/concepts/skills.mdx)
- [Pipeline Concepts](docs/pages/concepts/pipeline.mdx)
- [Configuration](docs/pages/configuration/)
- [API Reference](docs/pages/api/)
- [Examples](docs/pages/examples/)

### Local Development

```bash
# Install Mintlify CLI
npm i -g mint

# Preview documentation locally
cd docs
mint dev
```

### Deployment

Documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch. The deployment workflow is defined in [`.github/workflows/docs-deploy.yml`](.github/workflows/docs-deploy.yml).

**Setup Steps:**

1. Enable GitHub Pages in your repository:
   - Go to **Settings** → **Pages**
   - Source: **GitHub Actions**

2. Push changes to the `docs/` directory or the workflow file to trigger deployment

3. View your deployed documentation at: `https://tph-kds.github.io/AgentXogs/`

## 🧩 Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src
```

### Adding a New Skill

1. Create skill directory: `.agents/skills/{skill_name}/`
2. Add `SKILL.md` with documentation
3. Create `scripts/run.py` with skill implementation
4. Update pipeline if needed
5. Add tests in `tests/`

### Code Style

```bash
# Format code
uv run black src/ tests/

# Lint
uv run ruff src/ tests/

# Type checking
uv run mypy src/
```

## 📦 Project Metadata

- **Name**: agentx-skills
- **Version**: 0.1.0
- **License**: Apache-2.0
- **Python**: 3.10+
- **Authors**: tph-kds <dev@example.com>

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ for better log analysis
</p>
