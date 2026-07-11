---
id: TASK-001
title: Investigate Telegram /auth immediate authentication
complexity: standard
track: investigation
slice: core
status: todo
assigned_to: tech_lead
handoff_from: product_manager
scr: SCR-001
parent: null
discussion: DISCUSSION-001
---

# Task: Investigate Telegram /auth Immediate Authentication

## Context
The user reports that the Docker deployment at `/volume2/docker/icloudpd` is not authenticating: the Apple MFA prompt/code request is not reaching their mobile/Telegram flow. They explicitly require Telegram `/auth` to authenticate immediately instead of waiting for the next scheduled authentication/synchronization.

Known facts from memory and current inspection:
- Stack path: `/volume2/docker/icloudpd`.
- Compose file: `/volume2/docker/icloudpd/docker-compose.yaml`.
- Image default: `docker.staticduo.com/icloudpd:latest`.
- Telegram integration is configured by `.env`; do not report token values.
- Compose has `notification_type=Telegram`, `telegram_polling=true`, `telegram_webhook_url`, `telegram_webhook_port=48080`, and `mfa_provider=telegram`.
- Storage maps `/volume1/Photos:/icloud` and `/volume1/icloudpd-quarantine:/quarantine`.
- Worktree contains user-approved existing changes in the repo; do not revert them.

## Classification
- complexity: standard
- track: investigation
- slice: core

## Acceptance Criteria
- AC-1: Inspect Docker compose, effective container environment, container status/health, and recent logs while redacting secrets.
- AC-2: Determine whether Telegram command ingress is using polling, webhook, or both, and whether commands are reaching the container.
- AC-3: Trace current `/auth` handling in the repository code or deployed image behavior enough to explain whether it triggers auth immediately.
- AC-4: Identify the root cause or most likely failure mode for missing MFA prompt delivery.
- AC-5: Recommend the smallest safe next step: config-only fix, code fix, deploy/restart action, or explicit user approval for cookie/keyring cleanup.

## Expected Evidence
- Commands inspected and concise sanitized outputs.
- File/code references for `/auth`, Telegram command handling, MFA provider, and sync scheduling.
- Clear answer on whether implementation is needed.

## Constraints
- Do not expose Telegram token, Apple ID password, cookies, or other secrets.
- Do not make code/config changes in this investigation task.
- Do not run destructive Docker or filesystem commands.
- Avoid broad recursive searches under `/volume1`; inspect explicit paths only.

## Handoff
[Agent Message] From: product_manager To: tech_lead
Please investigate why `/auth` is not causing immediate Apple authentication for the deployed icloudpd service and why the MFA prompt is not reaching Telegram/mobile. Use this task file and SCR-001 as the scope. Return Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, and Recommended Next Step. Do not modify code or deployment config yet.

# Investigation Result

## Tech Lead Handoff
[Agent Message] From: tech_lead To: product_manager

Summary: The deployed container is running and healthy. Telegram command ingress is working via webhook. Current deployed behavior does make `/auth` immediate: logs show `/auth` received, wait loop broken, fresh login forced, Apple 2FA reached, and a Telegram MFA code request emitted within seconds. The likely remaining blocker is Apple credential/session state or Telegram message delivery confirmation, not waiting for the next sync interval.

Key evidence:
- Container `icloudpd` is healthy and started at `2026-05-29T07:43:16Z`.
- Runtime command includes `--watch-with-interval 900`, Telegram webhook options, and `--mfa-provider telegram`.
- Logs show webhook mode active: `Webhook configured successfully` and `Telegram bot using webhooks`.
- Logs show `/auth` immediate flow: `/auth command received`, `Sync requested, breaking wait loop`, `forcing a fresh login flow`, `Two-factor authentication is required`, and `Requested authentication code via Telegram`.
- Code path maps `/auth` to `progress.resume = True`, `request_auth_mode()`, wait-loop break, fresh auth, then Telegram MFA request.

AC coverage:
- AC-1: Covered by read-only compose, container, effective env, health, command, listener, and log inspection with secrets redacted.
- AC-2: Covered; webhook is used in practice and commands reach the container.
- AC-3: Covered; `/auth` triggers immediate auth in current deployed behavior.
- AC-4: Covered; likely blocker is Apple credential/session or Telegram delivery after the service emits the MFA request. Earlier logs also showed Apple `-20101` invalid email/password before the later 2FA path.
- AC-5: Covered; next step is user confirmation of the Telegram prompt/code or a focused Telegram delivery check if no message arrived.

Open risks:
- The investigation did not verify Telegram API delivery success beyond the service logging that it requested the code.
- Current code appears to log the six-digit Telegram code in the Telegram controller; future hardening should remove that.
- `/auth` forces fresh auth by clearing session files at runtime; do not do separate cookie/keyring cleanup without explicit approval.

Recommended next step: Ask the user whether the latest `/auth` produced a Telegram MFA prompt. If not, run a focused Telegram delivery/webhook check. If Apple returns `-20101` again, request explicit approval to inspect/update credential storage/keyring.

# Post Investigation Task Updates

## Product Manager: Post Investigation Expectations
- No implementation task should be opened yet unless Telegram delivery fails after a fresh `/auth` or Apple credential/keyring recovery is approved.
- Keep SCR-001 proposed until the user confirms whether immediate `/auth` behavior is acceptable in the live deployment.

# Reopen History

## Reopen 1 - User reports deferred auth message
The user reports that when they write `auth` in Telegram, nothing arrives on the iPhone and Telegram responds: `Authentication will be attempted on the next synchronization`. This conflicts with the investigation result that a slash command `/auth` broke the wait loop immediately. Same-scope discrepancy: determine whether the deployed command path treats bare `auth` differently from `/auth`, whether Telegram command registration/user usage is normalizing incorrectly, or whether an older handler/image is still answering.

Additional acceptance criteria for reopen:
- AC-R1: Compare behavior for bare `auth` versus slash `/auth` in the deployed code and logs.
- AC-R2: Identify the source of the exact message `Authentication will be attempted on the next synchronization`.
- AC-R3: Recommend a minimal fix so the user's Telegram command triggers immediate authentication in the form they are using, or provide exact required command syntax if no code change is needed.

## Reopen 1 Result
[Agent Message] From: tech_lead To: product_manager

Summary: The repository handler recognizes exact `/auth`, not bare `auth`. The exact response `Authentication will be attempted on the next synchronization` is emitted by the `/auth` handler itself. Recent logs show `/auth` was received, but because the service was already waiting for a Telegram MFA code from the 09:43 auth attempt, repeated `/auth` only sent the misleading deferred message and did not create a new Apple/iPhone prompt.

Additional findings:
- `src/icloudpd/extensions/telegram/controller.py` handles `text == "/auth"`; no bare `auth` branch exists.
- The misleading response is emitted before the wait loop/authenticator actually reaches Apple MFA.
- In idle state, `/auth` sets `progress.resume = True` and can break the wait loop immediately.
- In active MFA wait state, the authenticator is already waiting for the six-digit code, so another `/auth` does not restart Apple auth.

Recommendation: Implement a small Telegram command UX fix: accept both `auth` and `/auth`, and if status is already `NEED_MFA`, reply that the service is already waiting for the six-digit Apple code instead of saying auth will happen on the next synchronization.
