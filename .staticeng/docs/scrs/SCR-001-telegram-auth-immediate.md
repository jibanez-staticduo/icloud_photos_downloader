# SCR-001: Telegram /auth Immediate Authentication

## Status
Completed

## Completion
- Completed on 2026-05-30 through TASK-009 deployment.
- User confirmed the Telegram code prompt arrived, they entered the code, and authentication worked.

## Investigation Update
- Current deployed behavior already supports immediate `/auth` after the observed container start: logs show `/auth` breaking the 900-second wait loop and initiating fresh Apple authentication within seconds.
- Telegram command ingress is via webhook in practice; webhook takes precedence when `telegram_webhook_url` is configured, even if `telegram_polling=true` is also set.
- Remaining uncertainty is whether Telegram delivered the MFA prompt to the user after the service logged the code request, and whether Apple credentials/session state are valid.
- Reopen finding: the current response text is misleading during active MFA. Repeated `/auth` while already waiting for a Telegram MFA code says authentication will happen on the next synchronization, but it does not create a new Apple prompt because the service is already waiting for the six-digit code.
- User clarification: the user is sending `/auth` with the slash, and they send it precisely because they do not have the Apple code. The product behavior must treat `/auth` as a force-new-auth action, not as a reminder to enter a code they never received.
- Second user clarification: the user cannot use a manual iPhone `Obtener código de verificación` workaround. In the correct flow, icloudpd must actively trigger Apple so the trusted-device popup appears. Investigation found Telegram MFA was waiting for a code without priming the Apple HSA2 trusted-device challenge path that the console flow calls.

## Classification
- complexity: standard
- track: spec
- slice: core

## Problem
The deployed `icloudpd` service in `/volume2/docker/icloudpd` is not delivering the Apple MFA prompt to the user's mobile/Telegram flow. The user also requires the Telegram `/auth` command to trigger authentication immediately, not wait for the next scheduled synchronization/authentication cycle.

## Requested Behavior
- When the user sends `/auth` in Telegram, the service should attempt Apple authentication immediately.
- If Apple requires a six-digit MFA code, the user should receive the prompt immediately through Telegram.
- The flow should not depend on waiting until the next `synchronisation_interval` run.
- If `/auth` is sent because the user does not have a code, the service must not merely ask for an existing missing code; it should restart/force the authentication attempt enough to produce a fresh Apple device prompt when possible.
- Existing photo sync behavior and storage mappings must remain unchanged.

## Scope
- Inspect current Docker deployment under `/volume2/docker/icloudpd`.
- Identify whether the issue is deployment configuration, webhook/polling, Telegram command handling, container logs, or application behavior.
- Propose the smallest safe change that makes `/auth` immediate.

## Out of Scope
- Changing Apple ID, Telegram secrets, photo library path, or download policy unless required to restore authentication.
- Broad refactors unrelated to Telegram auth.
- Destructive cookie/keyring cleanup without explicit approval.

## Acceptance Criteria
- AC-1: Current Docker compose, effective environment, and container state are inspected without exposing secrets in reports.
- AC-2: Root cause is identified for why the mobile/Telegram MFA prompt is not arriving.
- AC-3: `/auth` behavior is mapped from Telegram command reception to Apple authentication attempt.
- AC-4: A minimal implementation or configuration change is recommended, with risk notes and required verification steps.
- AC-5: If implementation is performed later, evidence must show `/auth` triggers immediate authentication rather than waiting for the next scheduled sync.

## Discussion Record
- DISCUSSION-001: `.staticeng/tasks/discussions/DISCUSSION-001-icloudpd-telegram-authentication-immediate-auth.md`
