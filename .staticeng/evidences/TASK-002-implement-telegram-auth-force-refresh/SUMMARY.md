# TASK-002 Evidence Summary

## Scope
- Implemented Telegram `/auth` as an immediate fresh-auth trigger.
- Did not edit deployment configuration under `/volume2/docker/icloudpd`.
- Did not restart or mutate Docker services.

## Acceptance Criteria
- AC-1: Covered by `test_auth_command_schedules_immediate_auth_without_next_sync_message`; `/auth` sets `progress.resume`, requests auth mode, and no longer mentions `next synchronization`.
- AC-2: Covered by `test_auth_command_clears_stale_mfa_wait_and_requests_fresh_auth`, `test_auth_request_resets_restartable_mfa_states`, `test_auth_request_does_not_reset_checking_mfa`, `test_telegram_mfa_wait_loop_exits_cleanly_on_restart_request`, and `test_telegram_mfa_restart_during_failed_check_leaves_retry_safe_state`; `/auth` uses an explicit restart signal, clears restartable stale MFA wait states, does not reset `CHECKING_MFA` before verification resolves, and makes restart paths retry-safe.
- AC-3: Covered by `test_telegram_mfa_code_is_not_logged_in_plaintext`; code handling no longer logs the six-digit MFA value.
- AC-4: Focused automated tests added in `tests/test_telegram_auth.py`.
- AC-5: Evidence packet created at `.staticeng/evidences/TASK-002-implement-telegram-auth-force-refresh/` with logs under `.staticeng/evidences/TASK-002-implement-telegram-auth-force-refresh/logs/`.

## Critic Follow-up Coverage
- Explicit restart/cancel signal: `StatusExchange` now tracks `_auth_restart_requested` separately from generic status.
- Telegram MFA wait loop: `request_2fa_telegram()` detects restart requests and raises `TelegramAuthRestartRequested` for the caller retry path.
- `CHECKING_MFA` safety: `request_auth_mode()` does not reset `CHECKING_MFA`, preserving in-flight successful verification.
- Critic Review 2: failed verification with restart now deliberately transitions `CHECKING_MFA` back to `NO_INPUT_NEEDED` before raising `TelegramAuthRestartRequested`; successful verification still completes and clears restart intent.
- Active sync honesty: `/auth` reports a queued fresh auth attempt when another user/sync is currently processing outside MFA wait.
- Bot-local wait flag: `/auth` still clears `_waiting_for_auth_code`, and the shared restart signal drives the auth loop outcome.

## Verification
- PASS: `/tmp/opencode/icloudpd-task-002-venv/bin/python -m pytest tests/test_telegram_auth.py`
  - Log: `.staticeng/evidences/TASK-002-implement-telegram-auth-force-refresh/logs/pytest-test-telegram-auth.log`
- FAIL: `/tmp/opencode/icloudpd-task-002-venv/bin/python -m pytest tests/test_telegram_auth.py tests/test_authentication.py -q`
  - Log: `.staticeng/evidences/TASK-002-implement-telegram-auth-force-refresh/logs/pytest-focused-auth.log`
  - Result: all 10 TASK-002 tests passed; 5 existing `tests/test_authentication.py` assertions failed because expected `Authenticating...` output is absent in this branch's current CLI/log behavior.

## Changed Code References
- `src/icloudpd/extensions/telegram/controller.py`: `/auth` response now describes a fresh immediate auth attempt; MFA code logs are redacted.
- `src/icloudpd/status.py`: `request_auth_mode()` now sets an explicit auth restart signal and only resets restartable stale MFA states.
- `src/icloudpd/authentication.py`: Telegram MFA wait loop handles restart requests deliberately via `TelegramAuthRestartRequested`, including retry-safe cleanup after failed `CHECKING_MFA` verification.
- `src/icloudpd/base.py`: Telegram auth restart exceptions continue through the retry path without generic MFA corruption.
- `tests/test_telegram_auth.py`: focused regression coverage for immediate scheduling, stale MFA refresh, and redacted MFA logging.
