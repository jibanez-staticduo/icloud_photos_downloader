---
id: TASK-009
title: Deploy full upstream integration
complexity: standard
track: implementation
slice: core
status: todo
assigned_to: tech_lead
handoff_from: product_manager
scr: SCR-002
parent: TASK-008
discussion: DISCUSSION-001
---

# Task: Deploy Full Upstream Integration

## Context
TASK-008 full upstream integration has been brought back to the main workspace and focused validation passed:
- Download: 50 passed
- Telegram auth: 14 passed
- Authentication: 22 passed, 1 skipped
- CLI: 11 passed
- Compileall: passed

The user authorized build/deploy.

## Classification
- complexity: standard
- track: implementation
- slice: core

## Acceptance Criteria
- AC-1: Build/publish updated Docker image from the main workspace using the documented registry flow.
- AC-2: Pull/recreate only the live `icloudpd` service from `/volume2/docker/icloudpd/docker-compose.yaml` without editing secrets/config/cookies/keyrings/storage mappings.
- AC-3: Container returns to running/healthy state and image labels/digest match the build.
- AC-4: Runtime logs show Telegram webhook and auth flow initialized without secret exposure.
- AC-5: Evidence packet exists under `.staticeng/evidences/TASK-009-deploy-upstream-integration/` with sanitized logs and deployment summary.

## Constraints
- User authorized Docker build/publish/restart for `icloudpd` only.
- Do not edit `/volume2/docker/icloudpd/.env` or storage mappings.
- Do not delete cookies, sessions, keyrings, or photos.
- Do not expose tokens, chat IDs, Apple email, cookies, or MFA codes.
- Do not send Telegram `/auth` as the agent unless explicitly asked.

## Handoff
[Agent Message] From: product_manager To: tech_lead
Build, publish, and deploy the full upstream integration from the main workspace. Verify container health and collect sanitized evidence. Do not mutate live config/cookies/keyrings or send Telegram commands.

# Closure

## Product Manager Closure
- Deployment completed successfully.
- User confirmed that when the service requested the code, they entered it and authentication worked.
- Evidence packet: `.staticeng/evidences/TASK-009-deploy-upstream-integration/SUMMARY.md`.
- Live container reached running/healthy state and completed authenticated incremental sync.
