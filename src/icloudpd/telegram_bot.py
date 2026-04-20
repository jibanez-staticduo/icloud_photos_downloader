"""Telegram bot integration for icloudpd to handle sync commands.

This module has been moved to extensions/telegram/controller.py.
This file is kept for backward compatibility only.
"""

from .extensions.telegram.controller import TelegramBot

__all__ = ["TelegramBot"]
