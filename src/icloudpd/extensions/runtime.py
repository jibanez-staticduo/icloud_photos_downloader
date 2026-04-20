"""Runtime extension manager that coordinates all extensions."""

import logging
from typing import Any, Callable, Sequence

from flask import Flask

from icloudpd.extensions.contracts import MFAHandler, RuntimeExtension, SyncPolicy, TelemetrySink
from icloudpd.extensions.telemetry import FileTelemetrySink, set_telemetry_sink


class ExtensionRuntime:
    """Manages the lifecycle of all extensions."""

    def __init__(
        self,
        extensions: Sequence[RuntimeExtension] | None = None,
        mfa_handlers: dict[Any, MFAHandler] | None = None,
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

        telegram_bot = self.telegram_bot
        if telegram_bot is not None:
            for handler in self._mfa_handlers.values():
                if hasattr(handler, "set_telegram_bot"):
                    handler.set_telegram_bot(telegram_bot)

    def stop(self) -> None:
        """Stop all runtime extensions."""
        for ext in self._extensions:
            try:
                ext.stop()
            except Exception as e:
                # Log but don't fail on stop errors
                logging.getLogger(__name__).error(f"Failed to stop extension {ext}: {e}")

    @property
    def mfa_handlers(self) -> dict[Any, MFAHandler]:
        """Expose configured MFA handlers."""
        return self._mfa_handlers

    @property
    def extensions(self) -> Sequence[RuntimeExtension]:
        """Expose configured runtime extensions."""
        return tuple(self._extensions)

    @property
    def telegram_bot(self) -> Any:
        """Return the first extension bot, if available."""
        for ext in self._extensions:
            bot = getattr(ext, "bot", None)
            if bot is not None:
                return bot
        return None

    def extra_route_registrars(self) -> list[Callable[[Flask, Any, Any], None]]:
        """Build registrars for extensions that actually need web routes."""
        registrars: list[Callable[[Flask, Any, Any], None]] = []
        for ext in self._extensions:
            if not getattr(ext, "needs_web_routes", False):
                continue

            def registrar(app: Flask, status_exchange: Any, logger: Any, extension: Any = ext) -> None:
                extension.register_routes(app, logger, status_exchange)

            registrars.append(registrar)
        return registrars

    def web_server_port(self, default: int = 8080) -> int:
        """Return the preferred web server port for enabled route extensions."""
        for ext in self._extensions:
            if getattr(ext, "needs_web_routes", False):
                return getattr(ext, "webhook_port", default)
        return default

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
    from icloudpd.extensions.sync_policy import IncrementalSyncPolicy
    from icloudpd.extensions.telegram.mfa import TelegramMFAHandler
    from icloudpd.extensions.telegram.runtime import TelegramRuntimeExtension

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
        # Register Telegram MFA handler (will be updated with bot reference in start())
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
