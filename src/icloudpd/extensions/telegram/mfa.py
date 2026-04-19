"""Telegram MFA handler for authentication flow.

This wraps the old request_2fa_telegram function and implements the MFAHandler contract.
"""

import logging
from typing import Any

from ...authentication import request_2fa_telegram
from ..contracts import MFAHandler


class TelegramMFAHandler(MFAHandler):
    """MFA handler that uses Telegram for 2FA codes."""

    def __init__(self, telegram_bot: Any = None) -> None:
        self._telegram_bot = telegram_bot

    def set_telegram_bot(self, bot: Any) -> None:
        """Set the Telegram bot instance."""
        self._telegram_bot = bot

    def handle(self, icloud: Any, logger: Any, status_exchange: Any) -> None:
        """Handle MFA authentication via Telegram."""
        request_2fa_telegram(icloud, logger, status_exchange, self._telegram_bot)
