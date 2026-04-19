"""Telegram webhook route registration.

This moves the /telegram/webhook route out of the core server module.
"""

from flask import Flask, Response, make_response, request
from logging import Logger

from ...telegram_bot import TelegramBot


def register_telegram_routes(app: Flask, bot: TelegramBot, logger: Logger) -> None:
    """Register Telegram webhook routes on the Flask app."""
    
    @app.route("/telegram/webhook", methods=["POST"])
    def telegram_webhook() -> Response:
        """Handle incoming Telegram webhook updates."""
        if bot:
            try:
                update = request.get_json()
                if update:
                    bot.process_update(update)
                return make_response("Ok", 200)
            except Exception as e:
                logger.error(f"Error processing Telegram webhook: {e}")
                return make_response("Error", 500)
        return make_response("Telegram bot not configured", 404)
