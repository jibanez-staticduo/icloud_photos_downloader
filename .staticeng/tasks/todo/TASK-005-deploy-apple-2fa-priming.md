---
id: TASK-005
title: Deploy Apple 2FA priming fix
complexity: standard
track: implementation
slice: core
status: todo
assigned_to: tech_lead
handoff_from: product_manager
scr: SCR-001
parent: TASK-004
discussion: DISCUSSION-001
---

# Task: Deploy Apple 2FA Priming Fix

## Context
TASK-004 implemented the missing Apple HSA2 priming call in the Telegram MFA path. User intent is explicit: when they send `/auth`, icloudpd must force the Apple step that causes the trusted-device popup/code to appear.

The user already authorized deployment for the live `icloudpd` service during TASK-003, and this is the direct follow-up fix for the same auth incident.

## Classification
- complexity: standard
- track: implementation
- slice: core

## Acceptance Criteria
- AC-1: Updated TASK-004 image is built and published.
- AC-2: Live `icloudpd` service is recreated from the updated image without changing secrets, cookies, keyrings, or storage mappings.
- AC-3: Container is running/healthy after deployment.
- AC-4: Runtime logs after `/auth` show the new priming behavior before the Telegram code request, or otherwise show the relevant Apple priming failure warning.
- AC-5: Evidence packet exists at `.staticeng/evidences/TASK-005-deploy-apple-2fa-priming/` with sanitized logs.

## Constraints
- Docker build/publish/restart is authorized for `icloudpd` only.
- Do not expose secrets, tokens, chat IDs, Apple email, cookies, session data, or MFA codes.
- Do not edit `/volume2/docker/icloudpd/.env` or compose mappings.
- Do not delete cookies/keyrings.

## Handoff
[Agent Message] From: product_manager To: tech_lead
Deploy TASK-004 to live `icloudpd` using the same documented registry flow. Then verify container health and collect sanitized evidence. For live `/auth`, do not send Telegram commands as the agent; ask PMA/user unless logs already show a user-triggered attempt.

# Reopen History

## Reopen 1 - Priming did not produce iPhone popup
After TASK-004/TASK-005 deployment, the user sent `/auth` and reports that the Apple popup still does not arrive. Need read-only verification of live logs after the latest attempt and deeper inspection of pyicloud Apple HSA2 flow. The previous priming call may not be sufficient; next candidates are explicit challenge endpoint behavior, SMS challenge selection, or added instrumentation to confirm what Apple returns.

Additional acceptance criteria:
- AC-R1: Inspect sanitized logs after the latest `/auth` attempt to confirm whether priming errors are absent/present.
- AC-R2: Inspect `pyicloud_ipd` HSA2 APIs to identify an explicit trusted-device challenge endpoint if available.
- AC-R3: Recommend the next safe fix or operational path without asking the user to manually obtain an unavailable code.
