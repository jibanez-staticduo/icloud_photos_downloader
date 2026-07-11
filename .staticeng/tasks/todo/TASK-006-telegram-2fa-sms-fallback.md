---
id: TASK-006
title: Add Telegram 2FA instrumentation and SMS fallback
complexity: standard
track: implementation
slice: core
status: todo
assigned_to: developer
handoff_from: product_manager
scr: SCR-001
parent: TASK-005
discussion: DISCUSSION-001
---

# Task: Add Telegram 2FA Instrumentation and SMS Fallback

## Context
The user still does not receive the Apple trusted-device popup after `/auth`, even after TASK-004 primed Apple HSA2 with `get_trusted_phone_numbers()`. Live logs confirm `/auth` reaches the container and reaches HSA2. The codebase does not expose a known explicit trusted-device popup endpoint; it only has implicit HSA2 flow plus existing SMS challenge APIs.

Read-only inspection found a possible parser gap: Apple may return trusted phone numbers at `direct.twoSV.bridgeInitiateData.phoneNumberVerification.trustedPhoneNumbers`, while current parser only reads `direct.twoSV.phoneNumberVerification.trustedPhoneNumbers`.

## Classification
- complexity: standard
- track: implementation
- slice: core

## Scope
- Add sanitized instrumentation around Telegram 2FA priming so logs show whether trusted phone options were found, without exposing numbers or identifiers.
- Update trusted phone parsing to support the alternate Apple response shape if applicable.
- Add an explicit Telegram SMS fallback path requiring user choice before sending SMS; do not auto-send SMS.
- Preserve `/auth` fresh-auth and restart behavior.

## Acceptance Criteria
- AC-1: Logs indicate whether Apple HSA2 priming found trusted phone options, without exposing phone numbers or account data.
- AC-2: Trusted phone parser supports current and alternate Apple response shapes with tests.
- AC-3: Telegram flow can present an explicit SMS fallback option when no trusted-device popup arrives and only sends SMS after user selects a trusted phone option.
- AC-4: SMS code validation path works through Telegram without breaking existing trusted-device code validation.
- AC-5: Focused tests and evidence packet exist at `.staticeng/evidences/TASK-006-telegram-2fa-sms-fallback/`.

## Constraints
- Repository implementation only; no deployment in this task.
- Do not auto-send SMS.
- Do not expose phone numbers, Apple email, tokens, cookies, session data, or MFA codes in logs/tests/evidence.
- Do not keep retrying live `/auth` during Apple temporary refusal.

## Handoff
[Agent Message] From: product_manager To: developer
Implement the next safe recovery path for the missing Apple popup: sanitized HSA2 priming instrumentation, parser support for alternate trusted-phone response shape, and explicit Telegram SMS fallback by user choice. Do not deploy and do not auto-send SMS.
