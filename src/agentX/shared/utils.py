"""
Shared utilities for AgentX pipeline.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


class PipelineError(RuntimeError):
    """Raised when a pipeline step fails."""


def run_command(cmd: list[str]) -> None:
    """Run a subprocess command and raise with readable context on failure."""
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        raise PipelineError(f"Required executable not found: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise PipelineError(f"Command failed ({exc.returncode}): {' '.join(cmd)}") from exc


def load_config(config_path: Path | str | None = None) -> dict[str, Any]:
    """Load config file (JSON or YAML) from the repo root."""
    import yaml
    
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent.parent / "config.json"
    elif isinstance(config_path, str):
        config_path = Path(config_path)
    
    if not config_path.exists():
        return None
    
    try:
        if config_path.suffix in [".yaml", ".yml"]:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        else:
            # Try JSON first, fallback to YAML
            try:
                return json.loads(config_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                with open(config_path, "r") as f:
                    return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config {config_path}: {e}", file=sys.stderr)
        return None


def load_yaml_config(config_path: Path | str) -> dict[str, Any] | None:
    """Load YAML configuration file."""
    import yaml
    if isinstance(config_path, str):
        config_path = Path(config_path)
    if not config_path.exists():
        return None
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config {config_path}: {e}", file=sys.stderr)
        return None


def parse_time_range(time_range: str) -> int | None:
    """
    Parse time range string to minutes.
    Examples: "24h" -> 1440, "1h" -> 60, "30m" -> 30
    """
    if not time_range:
        return None

    pattern = r"(\d+)\s*(h|m|d|w)"
    match = re.match(pattern, time_range.strip().lower())

    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "h":
        return value * 60
    elif unit == "m":
        return value
    elif unit == "d":
        return value * 24 * 60
    elif unit == "w":
        return value * 7 * 24 * 60

    return None


def extract_error_signature(message: str) -> str:
    """Extract error signature from log message."""
    message_lower = message.lower()

    signatures = {
        "TIMEOUT": ["timeout", "timed out"],
        "CONNECTION_REFUSED": ["connection refused", "connection reset"],
        "DB_TIMEOUT": ["database timeout", "db timeout"],
        "AUTH_FAILED": ["authentication failed", "auth failed", "unauthorized"],
        "RATE_LIMIT": ["rate limit", "too many requests"],
        "OOM": ["out of memory", "oom", "memory error"],
        "NULL_POINTER": ["null pointer", "nullpointer", "npe"],
        "VALIDATION_ERROR": ["validation", "invalid input", "bad request"],
        "FORBIDDEN": ["forbidden", "access denied", "permission denied"],
        "NOT_FOUND": ["not found", "404", "missing resource"]
    }

    for sig, keywords in signatures.items():
        for keyword in keywords:
            if keyword in message_lower:
                return sig

    return "GENERIC_ERROR"


def parse_timestamp(timestamp_str: str):
    """Parse various timestamp formats to datetime."""
    from datetime import datetime
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%d/%b/%Y:%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue

    return None


def clamp(value: float, low: float, high: float) -> float:
    """Clamp a value to a range."""
    return max(low, min(value, high))


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide two numbers."""
    try:
        return a / b if b != 0 else default
    except (TypeError, ZeroDivisionError):
        return default


def percent_change(old_val: float, new_val: float) -> float:
    """Calculate percentage change."""
    if old_val == 0:
        return 0.0
    return ((new_val - old_val) / old_val) * 100
