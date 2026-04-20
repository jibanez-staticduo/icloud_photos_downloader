"""Telegram extension module."""

from icloudpd.extensions.telegram.controller import TelegramBot
from icloudpd.extensions.telegram.mfa import TelegramMFAHandler
from icloudpd.extensions.telegram.routes import register_telegram_routes
from icloudpd.extensions.telegram.runtime import TelegramRuntimeExtension

__all__ = [
    "TelegramBot",
    "TelegramMFAHandler",
    "register_telegram_routes",
    "TelegramRuntimeExtension",
]
