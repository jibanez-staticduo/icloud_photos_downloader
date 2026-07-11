# TASK-004 Evidence Summary

## Scope
- Added Apple HSA2 priming to the Telegram MFA path before sending the Telegram code request.
- Preserved the existing TASK-002 Telegram `/auth` restart signal and retry-safe MFA handling.
- Did not auto-send SMS challenges, mutate Docker, deploy, or log MFA codes/secrets.

## Acceptance Criteria
- AC-1: `request_2fa_telegram()` now calls `icloud.get_trusted_phone_numbers()` before `telegram_bot.request_auth_code(username)`.
- AC-2: Priming failures are explicit and safe: the exception is logged as a warning and the Telegram MFA prompt continues, so auth recovery is not hidden by a transient priming failure.
- AC-3: TASK-002 restart handling remains intact; the wait loop still raises `TelegramAuthRestartRequested` on `/auth` restart and resets retry-safe status where needed.
- AC-4: Focused coverage in `tests/test_telegram_auth.py` verifies priming order, priming failure behavior, no SMS auto-send, and restart compatibility.
- AC-5: Evidence packet is in `.staticeng/evidences/TASK-004-prime-apple-2fa-telegram/` with logs under `.staticeng/evidences/TASK-004-prime-apple-2fa-telegram/logs/`.

## Verification
- PASS: `/tmp/opencode/icloudpd-task-002-venv/bin/python -m pytest tests/test_telegram_auth.py`
  - Log: `.staticeng/evidences/TASK-004-prime-apple-2fa-telegram/logs/pytest-test-telegram-auth.log`
- NOTE: Running the same command with system Python failed before collection because the system environment lacks dependency `srp`; the task venv used for TASK-002 has the project test dependencies installed.

## Changed Code References
- `src/icloudpd/authentication.py`: Telegram MFA primes Apple trusted-phone/HSA2 path via `get_trusted_phone_numbers()` before requesting the Telegram code, with warning-and-continue failure handling.
- `tests/test_telegram_auth.py`: Added focused tests for priming order/no-SMS behavior and explicit warning/continuation on priming failure, while existing restart tests remain passing.
