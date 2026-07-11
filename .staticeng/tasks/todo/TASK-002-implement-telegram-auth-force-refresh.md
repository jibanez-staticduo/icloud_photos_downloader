---
id: TASK-002
title: Implement Telegram /auth force refresh behavior
complexity: standard
track: implementation
slice: core
status: todo
assigned_to: developer
handoff_from: product_manager
scr: SCR-001
parent: TASK-001
discussion: DISCUSSION-001
---

# Task: Implement Telegram /auth Force Refresh Behavior

## Context
The user sends `/auth` with the slash and expects the service to authenticate immediately because they do not have the six-digit Apple MFA code. Current behavior can reply `Authentication will be attempted on the next synchronization` and, if an MFA wait is already active, repeated `/auth` does not create a fresh Apple device prompt.

The product requirement is now explicit: `/auth` must be a force-new-auth action. If the user sends `/auth`, the service should interrupt/replace stale MFA wait state and trigger authentication immediately enough to produce a fresh Apple prompt when possible.

## Classification
- complexity: standard
- track: implementation
- slice: core

## Scope
- Update Telegram `/auth` handling and supporting status/auth orchestration as needed.
- Prefer the smallest safe change that makes `/auth` force a fresh auth attempt from idle or stale MFA-wait states.
- Update tests or add focused tests for the behavior.
- Preserve existing `/sync`, `/syncall`, `/stop`, `/status`, and six-digit code behavior except where necessary for `/auth` force refresh.

## Acceptance Criteria
- AC-1: Sending `/auth` while idle triggers immediate auth scheduling and the Telegram response no longer claims it will wait for the next synchronization.
- AC-2: Sending `/auth` while status is `NEED_MFA` or otherwise waiting for a previous code forces a fresh auth attempt rather than only waiting for the stale code.
- AC-3: The implementation avoids logging the six-digit MFA code in plaintext.
- AC-4: Focused automated tests cover `/auth` response/scheduling and the stale-MFA force refresh path.
- AC-5: Evidence packet exists at `.staticeng/evidences/TASK-002-implement-telegram-auth-force-refresh/` with `SUMMARY.md` and logs.

## Expected Evidence
- `.staticeng/evidences/TASK-002-implement-telegram-auth-force-refresh/SUMMARY.md` mapping AC-1 through AC-5 to verification.
- Test command logs under `.staticeng/evidences/TASK-002-implement-telegram-auth-force-refresh/logs/`.
- Code references for changed behavior.

## Constraints
- Do not edit `/volume2/docker/icloudpd` deployment config in this task.
- Do not restart or mutate Docker services in this implementation task unless PMA explicitly approves deployment.
- Do not expose or log secrets, Telegram tokens, Apple credentials, cookies, or MFA codes.
- Preserve user-approved existing repo changes; do not revert unrelated work.

## Handoff
[Agent Message] From: product_manager To: developer
Implement the approved SCR-001 behavior for `/auth` as a force-new-auth action. The user is explicitly sending `/auth` because they do not have the Apple code, so avoid UX that merely asks for an existing code. Make the smallest safe code/test changes, create the evidence packet, and return the shared output contract: Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, Recommended Next Step.

# Review History

## Critic Review 1 - Closure blocked
[Agent Message] From: critic To: product_manager

Findings blocking closure:
- High: `/auth` during `CHECKING_MFA` can invalidate a successful login and force an unexpected second auth cycle because `request_auth_mode()` resets `CHECKING_MFA` while the authenticator may still validate the code successfully.
- High: `/auth` is not guaranteed to force a fresh auth attempt immediately while a normal sync is already running; the current change may only queue the request until current processing returns.
- Medium: stale-MFA reset relies on making the active MFA loop fail with a generic status error instead of a deliberate cancellation/restart signal.
- Medium: Telegram bot-local `_waiting_for_auth_code` can diverge from shared auth state under concurrent `/auth` and `request_auth_code()` updates.
- Medium: tests only cover flags and do not exercise the real Telegram MFA wait loop or race-sensitive states.

Required follow-up:
- Add an explicit auth restart/cancel signal or equivalent deliberate state handling rather than resetting all MFA states blindly.
- Make `request_2fa_telegram()` detect user-requested auth restart cleanly and exit for retry without treating it as an unexpected MFA failure.
- Avoid resetting `CHECKING_MFA` in a way that can invalidate successful verification.
- Clarify behavior while an active photo sync is running: either actually interrupt/cancel safely or send an honest queued response.
- Add tests for `NEED_MFA`, `SUPPLIED_MFA`, `CHECKING_MFA`, and the restart path in the Telegram MFA loop.

## Critic Review 2 - Closure still blocked
[Agent Message] From: critic To: product_manager

Findings blocking closure:
- Blocker: `/auth` during `CHECKING_MFA` can leave auth state stuck and prevent any fresh prompt. `request_auth_mode()` intentionally does not reset `CHECKING_MFA`, and `request_2fa_telegram()` can raise `TelegramAuthRestartRequested` from `CHECKING_MFA` without transitioning back to `NO_INPUT_NEEDED`. The next retry then fails the initial `NO_INPUT_NEEDED -> NEED_MFA` transition and can loop instead of producing a fresh auth prompt.
- Blocking test gap: the current `CHECKING_MFA` test codifies preservation of `CHECKING_MFA` but does not test the retry path after a restart request during verification.

Required follow-up:
- Ensure restart during `CHECKING_MFA` cannot leave shared status stuck. Either defer restart until verification completes, or when raising a restart exception from `CHECKING_MFA`, intentionally move to a retry-safe state without invalidating an already-successful verification.
- Add regression coverage for `/auth` during `CHECKING_MFA` followed by the next retry attempt.

## Critic Review 3 - Auth closure accepted
[Agent Message] From: critic To: product_manager

No blocking findings remain for the auth-focused implementation. The reviewed paths match the intended behavior:
- `/auth` while idle or stale MFA-waiting schedules a fresh auth attempt.
- `/auth` during active non-auth processing gives honest queued messaging.
- `CHECKING_MFA` successful validation completes, while failed validation with restart transitions to a retry-safe state.
- Plaintext MFA code logging has been removed from Telegram handling.

Residual risks:
- Live Apple prompt behavior still requires deployment/runtime verification.
- Broader authentication tests have pre-existing failures unrelated to TASK-002; focused TASK-002 tests pass in the developer environment.

# Post Implementation Task Updates

## Product Manager: Post Implementation Expectations
- TASK-002 implementation is auth-review accepted but not deployed.
- Do not claim the running `/volume2/docker/icloudpd` service is fixed until a deployment/restart task updates the image/container and live `/auth` behavior is verified.
- Next PMA action should be an explicit deployment authorization request or a deployment task if the user approves service mutation.
