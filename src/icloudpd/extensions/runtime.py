"""Runtime extension manager that coordinates all extensions.

This is the main entry point for extension lifecycle management.
"""

import logging
from typing import Any, Sequence

from .contracts import RuntimeExtension, MFAHandler, SyncPolicy, TelemetrySink
from .telemetry import get_telemetry_sink, set_telemetry_sink, FileTelemetrySink


class ExtensionRuntime:
    """Manages the lifecycle of all extensions."""

    def __init__(
        self,
        extensions: Sequence[RuntimeExtension] | None = None,
        mfa_handlers: dict | None = None,
        sync_policy: SyncPolicy | None = None,
        telemetry_sink: TelemetrySink | None = None,
    ) -> None:
        self._extensions = list(extensions or [])
        self._mfa_handlers = mfa_handlers or {}
        self._sync_policy = sync_policy
        self._telemetry_sink = telemetry_sink

        # Set telemetry sink if provided
        if telemetry_sink:
            set_telemetry_sink(telemetry_sink)

    def start(self, logger: Any, global_config: Any, status_exchange: Any) -> None:
        """Start all runtime extensions."""
        for ext in self._extensions:
            try:
                ext.start(logger, global_config, status_exchange)
            except Exception as e:
                logger.error(f"Failed to start extension {ext}: {e}")

    def stop(self) -> None:
        """Stop all runtime extensions."""
        for ext in self._extensions:
            try:
                ext.stop()
            except Exception as e:
                # Log but don't fail on stop errors
                logging.getLogger(__name__).error(f"Failed to stop extension {ext}: {e}")

    def register_routes(self, app: Any, logger: Any, status_exchange: Any) -> None:
        """Register routes from all extensions."""
        for ext in self._extensions:
            try:
                ext.register_routes(app, logger, status_exchange)
            except Exception as e:
                logger.error(f"Failed to register routes for extension {ext}: {e}")

    def get_mfa_handler(self, provider: Any) -> MFAHandler | None:
        """Get MFA handler for the given provider."""
        return self._mfa_handlers.get(provider)

    @property
    def sync_policy(self) -> SyncPolicy | None:
        """Get the sync policy."""
        return self._sync_policy

    @property
    def telemetry_sink(self) -> TelemetrySink | None:
        """Get the telemetry sink."""
        return self._telemetry_sink


def build_extension_runtime(
    global_config: Any, logger: logging.Logger | None = None
) -> ExtensionRuntime:
    """
    Build the extension runtime from global config.
    
    This is the main factory function that creates all extensions
    based on the configuration.
    """
    from .contracts import RuntimeExtension
    from .extensions.telegram.runtime import TelegramRuntimeExtension
    from .extensions.telegram.mfa import TelegramMFAHandler
    from .extensions.sync_policy import IncrementalSyncPolicy
    from .extensions.telemetry import FileTelemetrySink

    # Build telemetry sink
    telemetry_sink = FileTelemetrySink()

    # Build Telegram extension if configured
    telegram_ext: RuntimeExtension | None = None
    mfa_handlers: dict = {}

    if global_config.telegram_token and global_config.telegram_chat_id:
        telegram_ext = TelegramRuntimeExtension(
            token=global_config.telegram_token,
            chat_id=global_config.telegram_chat_id,
            polling=global_config.telegram_polling,
            polling_interval=global_config.telegram_polling_interval,
            webhook_url=global_config.telegram_webhook_url,
            webhook_port=global_config.telegram_webhook_port,
        )
        # Register Telegram MFA handler
        from icloudpd.mfa_provider import MFAProvider
        mfa_handlers[MFAProvider.TELEGRAM] = TelegramMFAHandler()

    # Build sync policy
    sync_policy = IncrementalSyncPolicy()

    # Build runtime with all extensions
    extensions = [ext for ext in [telegram_ext] if ext is not None]

    return ExtensionRuntime(
        extensions=extensions,
        mfa_handlers=mfa_handlers,
        sync_policy=sync_policy,
        telemetry_sink=telemetry_sink,
    )


# Convenience alias
build = build_extension_runtime
