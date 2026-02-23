from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import Any, Dict

def parse_interval(interval_str: str) -> float:
    """Parse interval string (e.g., '1m', '10m', '120m') to seconds."""
    match = re.match(r"^(\d+)([s|m|h])$", interval_str.lower())
    if not match:
        raise ValueError(f"Invalid interval format: {interval_str}. Use format like '1m', '10m', '120m'")

    value, unit = match.groups()
    value = int(value)
    
    # Range checks for safety/compatibility
    if unit == "s" and value < 10:
        raise ValueError("Interval must be at least 10 seconds")
    if unit == "m" and value > 120:
        raise ValueError("Interval must be at most 120 minutes")

    if unit == "s":
        return float(value)
    elif unit == "m":
        return float(value * 60)
    elif unit == "h":
        return float(value * 3600)
    
    raise ValueError(f"Invalid unit: {unit}")

def format_time_display(timestamp: Any) -> str:
    """Format timestamp for display."""
    if timestamp is None:
        return "N/A"
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        elif isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        else:
            return str(timestamp)
        return dt.strftime("%d/%m %H:%M:%SZ")
    except Exception:
        return str(timestamp)

def flatten_dict(data: Dict[str, Any], exclude_fields: set[str] | None = None) -> Dict[str, Any]:
    """Flatten nested JSON structure to a flat dictionary."""
    if exclude_fields is None:
        exclude_fields = set()

    flattened: Dict[str, Any] = {}

    def _flatten(obj: Any, prefix: str = "") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in exclude_fields:
                    continue
                new_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    _flatten(value, new_key)
                else:
                    flattened[new_key] = value
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
                if isinstance(item, (dict, list)):
                    _flatten(item, new_key)
                else:
                    flattened[new_key] = item
        else:
            if prefix:
                flattened[prefix] = obj
            else:
                flattened["value"] = obj

    _flatten(data)
    return flattened
