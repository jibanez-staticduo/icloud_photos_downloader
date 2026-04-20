"""Telemetry module for fork-specific debug/logging events.

This replaces direct writes to /app/src/.cursor/debug.log with a proper abstraction.
"""

import json
import os
import time
from typing import Any

from .contracts import TelemetrySink


class FileTelemetrySink:
    """Telemetry sink that writes to a file (default: /app/src/.cursor/debug.log)."""

    def __init__(self, filepath: str | None = None) -> None:
        self.filepath = filepath or "/app/src/.cursor/debug.log"

    def _ensure_dir(self) -> None:
        """Ensure the directory for the telemetry file exists."""
        dirpath = os.path.dirname(self.filepath)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

    def emit(self, event: str, **data: Any) -> None:
        """Emit a telemetry event as JSON."""
        try:
            self._ensure_dir()
            payload = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "H0",
                "location": event,
                "data": data,
                "timestamp": int(time.time() * 1000),
            }
            with open(self.filepath, "a", encoding="utf8") as f:
                f.write(json.dumps(payload) + "\n")
        except Exception:
            # Silently fail - telemetry should never break the main flow
            pass


# Global telemetry sink instance (can be replaced in tests)
_telemetry_sink: TelemetrySink | None = None


def get_telemetry_sink() -> TelemetrySink | None:
    """Get the current telemetry sink."""
    return _telemetry_sink


def set_telemetry_sink(sink: TelemetrySink | None) -> None:
    """Set the telemetry sink (or None to disable)."""
    global _telemetry_sink
    _telemetry_sink = sink


def emit(event: str, **data: Any) -> None:
    """Emit a telemetry event using the configured sink."""
    sink = get_telemetry_sink()
    if sink:
        sink.emit(event, **data)
