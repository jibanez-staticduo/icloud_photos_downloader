import logging
import threading
import time
from unittest import mock

import pytest

from icloudpd.authentication import TelegramAuthRestartRequested, request_2fa_telegram
from icloudpd.extensions.telegram.controller import TelegramBot
from icloudpd.status import Status, StatusExchange


def build_bot(status_exchange: StatusExchange) -> TelegramBot:
    bot = TelegramBot(
        logger=logging.getLogger("test.telegram"),
        token="token",
        chat_id="123",
        status_exchange=status_exchange,
    )
    bot.send_message = mock.Mock(return_value=True)  # type: ignore[method-assign]
    return bot


def test_auth_command_schedules_immediate_auth_without_next_sync_message() -> None:
    status_exchange = StatusExchange()
    bot = build_bot(status_exchange)

    bot.process_message({"text": "/auth"})

    bot.send_message.assert_called_once()
    response = bot.send_message.call_args.args[0]
    assert "next synchronization" not in response
    assert "fresh authentication attempt now" in response
    assert status_exchange.get_progress().resume is True
    assert status_exchange.get_progress().cancel is False
    assert status_exchange.consume_auth_mode_request() is True
    assert bot._waiting_for_auth_code is False


def test_auth_command_clears_stale_mfa_wait_and_requests_fresh_auth() -> None:
    status_exchange = StatusExchange()
    assert status_exchange.replace_status(Status.NO_INPUT_NEEDED, Status.NEED_MFA)
    bot = build_bot(status_exchange)
    bot._waiting_for_auth_code = True

    bot.process_message({"text": "/auth"})

    assert status_exchange.get_status() == Status.NO_INPUT_NEEDED
    assert status_exchange.consume_auth_mode_request() is True
    assert status_exchange.get_progress().resume is True
    assert bot._waiting_for_auth_code is False


@pytest.mark.parametrize("status", [Status.NEED_MFA, Status.SUPPLIED_MFA])
def test_auth_request_resets_restartable_mfa_states(status: Status) -> None:
    status_exchange = StatusExchange()
    assert status_exchange.replace_status(Status.NO_INPUT_NEEDED, Status.NEED_MFA)
    if status == Status.SUPPLIED_MFA:
        assert status_exchange.set_payload("654321")

    status_exchange.request_auth_mode()

    assert status_exchange.get_status() == Status.NO_INPUT_NEEDED
    assert status_exchange.get_payload() is None
    assert status_exchange.auth_restart_requested() is True


def test_auth_request_does_not_reset_checking_mfa() -> None:
    status_exchange = StatusExchange()
    assert status_exchange.replace_status(Status.NO_INPUT_NEEDED, Status.NEED_MFA)
    assert status_exchange.set_payload("654321")
    assert status_exchange.replace_status(Status.SUPPLIED_MFA, Status.CHECKING_MFA)

    status_exchange.request_auth_mode()

    assert status_exchange.get_status() == Status.CHECKING_MFA
    assert status_exchange.get_payload() == "654321"
    assert status_exchange.auth_restart_requested() is True


def test_auth_command_reports_queued_when_sync_is_processing() -> None:
    status_exchange = StatusExchange()
    status_exchange.set_current_user("user@example.com")
    bot = build_bot(status_exchange)

    bot.process_message({"text": "/auth"})

    response = bot.send_message.call_args.args[0]
    assert "queued" in response
    assert status_exchange.get_progress().resume is True
    assert status_exchange.consume_auth_mode_request() is True


def test_telegram_mfa_code_is_not_logged_in_plaintext(caplog: object) -> None:
    status_exchange = StatusExchange()
    assert status_exchange.replace_status(Status.NO_INPUT_NEEDED, Status.NEED_MFA)
    bot = build_bot(status_exchange)
    bot._waiting_for_auth_code = True

    with caplog.at_level(logging.INFO, logger="test.telegram"):  # type: ignore[attr-defined]
        bot.process_message({"text": "123456"})

    assert "123456" not in caplog.text  # type: ignore[attr-defined]
    assert status_exchange.get_payload() == "123456"


def test_telegram_mfa_triggers_push_before_requesting_code() -> None:
    status_exchange = StatusExchange()
    bot = build_bot(status_exchange)
    icloud = mock.Mock()
    calls: list[str] = []

    icloud.trigger_push_notification.side_effect = lambda: calls.append("push") or True
    bot.request_auth_code = mock.Mock(  # type: ignore[method-assign]
        side_effect=lambda _username: calls.append("telegram")
        or status_exchange.request_auth_mode()
    )

    with pytest.raises(TelegramAuthRestartRequested):
        request_2fa_telegram(icloud, logging.getLogger("test.telegram"), status_exchange, bot)

    assert calls == ["push", "telegram"]
    icloud.send_2fa_code_sms.assert_not_called()


def test_telegram_mfa_continues_when_push_trigger_fails(caplog: object) -> None:
    status_exchange = StatusExchange()
    bot = build_bot(status_exchange)
    icloud = mock.Mock()
    calls: list[str] = []

    def fail_push() -> bool:
        calls.append("push")
        raise RuntimeError("apple auth widget unavailable")

    icloud.trigger_push_notification.side_effect = fail_push
    bot.request_auth_code = mock.Mock(  # type: ignore[method-assign]
        side_effect=lambda _username: calls.append("telegram")
        or status_exchange.request_auth_mode()
    )

    with caplog.at_level(logging.WARNING, logger="test.telegram"):  # type: ignore[attr-defined]
        with pytest.raises(TelegramAuthRestartRequested):
            request_2fa_telegram(icloud, logging.getLogger("test.telegram"), status_exchange, bot)

    assert calls == ["push", "telegram"]
    assert "Unable to trigger Apple two-factor push" in caplog.text  # type: ignore[attr-defined]


def test_telegram_mfa_retries_push_before_reprompting_after_invalid_code() -> None:
    status_exchange = StatusExchange()
    bot = build_bot(status_exchange)
    icloud = mock.Mock()
    calls: list[str] = []

    icloud.trigger_push_notification.side_effect = lambda: calls.append("push") or True
    icloud.validate_2fa_code.side_effect = [False, True]

    def request_code(_username: str) -> None:
        calls.append("telegram")
        status_exchange.set_payload("654321")

    bot.request_auth_code = mock.Mock(side_effect=request_code)  # type: ignore[method-assign]

    request_2fa_telegram(icloud, logging.getLogger("test.telegram"), status_exchange, bot)

    assert calls == ["push", "telegram", "push", "telegram"]
    assert icloud.validate_2fa_code.call_count == 2
    bot.send_message.assert_any_call("Authentication completed successfully")


def test_telegram_mfa_reprompts_when_retry_push_fails(caplog: object) -> None:
    status_exchange = StatusExchange()
    bot = build_bot(status_exchange)
    icloud = mock.Mock()
    calls: list[str] = []

    def trigger_push() -> bool:
        calls.append("push")
        if calls.count("push") == 2:
            raise RuntimeError("apple retry push unavailable")
        return True

    icloud.trigger_push_notification.side_effect = trigger_push
    icloud.validate_2fa_code.side_effect = [False, True]

    def request_code(_username: str) -> None:
        calls.append("telegram")
        status_exchange.set_payload("654321")

    bot.request_auth_code = mock.Mock(side_effect=request_code)  # type: ignore[method-assign]

    with caplog.at_level(logging.WARNING, logger="test.telegram"):  # type: ignore[attr-defined]
        request_2fa_telegram(icloud, logging.getLogger("test.telegram"), status_exchange, bot)

    assert calls == ["push", "telegram", "push", "telegram"]
    assert "Unable to trigger Apple two-factor push" in caplog.text  # type: ignore[attr-defined]
    bot.send_message.assert_any_call("Authentication completed successfully")


def test_telegram_mfa_wait_loop_exits_cleanly_on_restart_request() -> None:
    status_exchange = StatusExchange()
    bot = build_bot(status_exchange)
    icloud = mock.Mock()

    result: dict[str, BaseException] = {}

    def wait_for_mfa() -> None:
        try:
            request_2fa_telegram(icloud, logging.getLogger("test.telegram"), status_exchange, bot)
        except BaseException as exc:  # noqa: BLE001 - asserted below
            result["error"] = exc

    thread = threading.Thread(target=wait_for_mfa)
    thread.start()
    deadline = time.time() + 2
    while status_exchange.get_status() != Status.NEED_MFA and time.time() < deadline:
        time.sleep(0.01)

    status_exchange.request_auth_mode()
    thread.join(timeout=2)

    assert not thread.is_alive()
    assert isinstance(result.get("error"), TelegramAuthRestartRequested)
    assert status_exchange.get_status() == Status.NO_INPUT_NEEDED
    assert status_exchange.consume_auth_mode_request() is True


def test_telegram_mfa_restart_during_failed_check_leaves_retry_safe_state() -> None:
    status_exchange = StatusExchange()
    bot = build_bot(status_exchange)
    icloud = mock.Mock()

    def fail_after_restart_request(code: str) -> bool:
        assert code == "654321"
        status_exchange.request_auth_mode()
        return False

    icloud.validate_2fa_code.side_effect = fail_after_restart_request
    bot.request_auth_code = mock.Mock(  # type: ignore[method-assign]
        side_effect=lambda _username: status_exchange.set_payload("654321")
    )

    with pytest.raises(TelegramAuthRestartRequested):
        request_2fa_telegram(icloud, logging.getLogger("test.telegram"), status_exchange, bot)

    assert status_exchange.get_status() == Status.NO_INPUT_NEEDED
    assert status_exchange.replace_status(Status.NO_INPUT_NEEDED, Status.NEED_MFA)


def test_telegram_mfa_restart_during_successful_check_does_not_invalidate_success() -> None:
    status_exchange = StatusExchange()
    bot = build_bot(status_exchange)
    icloud = mock.Mock()

    def succeed_after_restart_request(code: str) -> bool:
        assert code == "654321"
        status_exchange.request_auth_mode()
        return True

    icloud.validate_2fa_code.side_effect = succeed_after_restart_request
    bot.request_auth_code = mock.Mock(  # type: ignore[method-assign]
        side_effect=lambda _username: status_exchange.set_payload("654321")
    )

    request_2fa_telegram(icloud, logging.getLogger("test.telegram"), status_exchange, bot)

    assert status_exchange.get_status() == Status.NO_INPUT_NEEDED
    assert status_exchange.auth_restart_requested() is False
    bot.send_message.assert_any_call("Authentication completed successfully")
