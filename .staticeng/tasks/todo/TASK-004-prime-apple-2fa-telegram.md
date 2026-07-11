---
id: TASK-004
title: Prime Apple 2FA challenge before Telegram code request
complexity: standard
track: implementation
slice: core
status: todo
assigned_to: developer
handoff_from: product_manager
scr: SCR-001
parent: TASK-003
discussion: DISCUSSION-001
---

# Task: Prime Apple 2FA Challenge Before Telegram Code Request

## Context
After deploying TASK-002/TASK-003, `/auth` reaches the live container, forces a fresh login, and reaches `Two-factor authentication is required (2fa)`, but the user does not receive the trusted-device popup on iPhone.

The user clarified that there is no usable manual workaround for their account/device flow. In their known-good flow, icloudpd must correctly request Apple 2FA so the popup appears and provides the code.

Investigation found the Telegram MFA path calls `telegram_bot.request_auth_code()` and waits for a code, but unlike the console 2FA path, it does not call `icloud.get_trusted_phone_numbers()` first. The console path's call loads the Apple HSA2 auth widget via `GET /appleauth/auth`, which appears to be the challenge priming step before code validation.

## Classification
- complexity: standard
- track: implementation
- slice: core

## Scope
- Update Telegram MFA flow to prime Apple 2FA/trusted-device challenge before asking the user for the code in Telegram.
- Prefer a small safe change in `request_2fa_telegram()`.
- Do not auto-send SMS challenges unless explicitly requested; the desired flow is trusted-device popup, not SMS.
- Add tests that prove the priming call occurs before Telegram asks for the code.

## Acceptance Criteria
- AC-1: `request_2fa_telegram()` triggers the same Apple HSA2 priming path used by console 2FA before sending the Telegram code request.
- AC-2: If the priming call fails, behavior is explicit and safe: either logs a warning and continues to ask for the code, or fails clearly without hiding the cause.
- AC-3: Restart handling from TASK-002 remains intact while waiting for MFA.
- AC-4: Focused tests cover priming order, priming failure behavior, and restart compatibility.
- AC-5: Evidence packet exists at `.staticeng/evidences/TASK-004-prime-apple-2fa-telegram/` with `SUMMARY.md` and logs.

## Expected Evidence
- Focused pytest logs.
- Code references showing where Apple 2FA is primed.
- Evidence summary mapping AC-1 through AC-5.

## Constraints
- Repository changes only for implementation; no Docker mutation in this task.
- Do not log or expose secrets, cookies, credentials, or MFA codes.
- Preserve TASK-002 behavior and tests.

## Handoff
[Agent Message] From: product_manager To: developer
Implement the missing Apple 2FA priming in the Telegram MFA path. The user's iPhone popup does not appear because Telegram flow reaches `requires_2fa` but appears not to trigger the same Apple HSA2 challenge priming that console 2FA does. Add focused tests and evidence. Do not deploy in this task.
