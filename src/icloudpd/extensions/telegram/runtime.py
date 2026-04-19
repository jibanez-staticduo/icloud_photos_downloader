"""Telegram runtime extension that wraps the old TelegramBot.

This is a thin adapter that implements the RuntimeExtension contract.
The actual bot logic is still in src/icloudpd/telegram_bot.py for now.
"""

import logging
from typing import Any

from ...telegram_bot import TelegramBot
from ..contracts import RuntimeExtension


class TelegramRuntimeExtension(RuntimeExtension):
    """Runtime extension that manages Telegram bot lifecycle."""

    def __init__(
        self,
        token: str | None,
        chat_id: str | None,
        polling: bool,
        polling_interval: int,
        webhook_url: str | None,
        webhook_port: int,
    ) -> None:
        self.token = token
        self.chat_id = chat_id
        self.polling = polling
        self.polling_interval = polling_interval
        self.webhook_url = webhook_url
        self.webhook_port = webhook_port
        self._bot: TelegramBot | None = None
        self._logger: logging.Logger | None = None

    def start(self, logger: Any, global_config: Any, status_exchange: Any) -> None:
        """Start the Telegram bot if configured."""
        # Check if bot should be started (polling OR webhook, with token and chat_id)
        if not (self.polling or self.webhook_url):
            return
        if not self.token or not self.chat_id:
            return

        self._logger = logger
        self._bot = TelegramBot(
            logger=logger,
            token=self.token,
            chat_id=self.chat_id,
            status_exchange=status_exchange,
            polling_interval=self.polling_interval,
            webhook_url=self.webhook_url,
        )
        self._bot.start_polling()
        # Store bot reference in status_exchange for auth requests
        status_exchange.set_telegram_bot(self._bot)

    def stop(self) -> None:
        """Stop the Telegram bot gracefully."""
        # Telegram bot doesn't have a stop method yet, but we can set it to None
        if self._bot:
            self._bot = None

    def register_routes(self, app: Any, logger: Any, status_exchange: Any) -> None:
        """Register Telegram webhook route if webhook is configured."""
        if not self.webhook_url or not self._bot:
            return

        # Import here to avoid circular dependencies
        from .routes import register_telegram_routes

        register_telegram_routes(app, self._bot, logger)

    @property
    def bot(self) -> TelegramBot | None:
        """Get the Telegram bot instance."""
        return self._bot

    @property
    def is_configured(self) -> bool:
        """Check if Telegram is configured."""
        return bool(self.token and self.chat_id and (self.polling or self.webhook_url))
