"""Contracts/interfaces for extension points.

These define the minimal seams between core and extensions.
"""

from typing import Protocol, Any


class TelemetrySink(Protocol):
    """Sink for telemetry/debug events."""

    def emit(self, event: str, **data: Any) -> None:
        """Emit a telemetry event with optional data."""
        ...


class RuntimeExtension(Protocol):
    """Extension that can be started/stopped alongside the main runtime."""

    def start(self, logger: Any, global_config: Any, status_exchange: Any) -> None:
        """Start the extension (e.g., Telegram bot, webhook server)."""
        ...

    def stop(self) -> None:
        """Stop the extension gracefully."""
        ...

    def register_routes(self, app: Any, logger: Any, status_exchange: Any) -> None:
        """Register additional Flask routes on the web server."""
        ...


class MFAHandler(Protocol):
    """Handler for MFA authentication flow."""

    def handle(self, icloud: Any, logger: Any, status_exchange: Any) -> None:
        """Handle MFA authentication for the given iCloud session."""
        ...


class SyncPolicy(Protocol):
    """Policy for determining sync behavior (full vs incremental)."""

    def prepare_albums(
        self, albums: Any, file_cache: Any, status_exchange: Any, logger: Any
    ) -> bool:
        """Prepare albums for sync. Returns True if incremental sync is active."""
        ...

    def on_item_seen(self, item: Any) -> None:
        """Called when a photo item is processed."""
        ...

    def finalize(
        self, file_cache: Any, status_exchange: Any, user_config: Any, logger: Any
    ) -> None:
        """Finalize sync and persist state (e.g., last sync date)."""
        ...
