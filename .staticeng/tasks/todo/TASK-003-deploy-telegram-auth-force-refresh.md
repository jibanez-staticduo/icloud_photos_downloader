---
id: TASK-003
title: Deploy Telegram /auth force refresh image
complexity: standard
track: implementation
slice: core
status: todo
assigned_to: tech_lead
handoff_from: product_manager
scr: SCR-001
parent: TASK-002
discussion: DISCUSSION-001
---

# Task: Deploy Telegram /auth Force Refresh Image

## Context
The user authorized deployment of TASK-002 changes to the live Docker service at `/volume2/docker/icloudpd`. The compose stack uses `docker.staticduo.com/icloudpd:latest` from `.env` and the repo includes `release-image.sh` using `Dockerfile.local`.

## Classification
- complexity: standard
- track: implementation
- slice: core

## Scope
- Build and publish the updated image using the repo's documented registry flow.
- Pull/recreate the `icloudpd` service in `/volume2/docker/icloudpd`.
- Verify the container is running/healthy and logs show the updated `/auth` behavior after the user triggers `/auth` or via safe observable startup/log evidence.

## Acceptance Criteria
- AC-1: Updated image is built and published or otherwise made available to the live compose stack.
- AC-2: Live `icloudpd` container is recreated from the updated image without changing secrets or compose storage mappings.
- AC-3: Container returns to running/healthy state.
- AC-4: Logs or runtime evidence confirm the updated Telegram `/auth` message/behavior is present.
- AC-5: Evidence packet exists at `.staticeng/evidences/TASK-003-deploy-telegram-auth-force-refresh/` with `SUMMARY.md` and sanitized logs.

## Constraints
- User has authorized Docker build/publish/restart for `icloudpd` only.
- Do not expose Telegram token, Apple credentials, cookies, or MFA codes.
- Do not edit `/volume2/docker/icloudpd/.env` unless a deployment blocker requires explicit PMA approval.
- Do not change storage volume mappings or delete cookies/keyrings.
- Preserve unrelated repo changes.

## Handoff
[Agent Message] From: product_manager To: tech_lead
Deploy the TASK-002 fix to the live `icloudpd` Docker service using the documented registry flow. Build/publish the image, pull/recreate the service, verify health, and collect sanitized evidence. Do not change secrets, compose mappings, cookies, or keyrings.

# Reopen History

## Reopen 1 - User still does not receive iPhone code
After deployment, the user reports that they still do not receive the Apple code/prompt. Need live read-only verification of the deployed `/auth` path and Apple/Telegram logs to determine whether `/auth` reaches the container, whether the fresh-auth message is sent, whether Apple requests 2FA, whether Telegram asks for the code, or whether Apple returns credential/session errors.

Additional acceptance criteria:
- AC-R1: Inspect sanitized live logs after the user's `/auth` attempt.
- AC-R2: Confirm whether the deployed code path is active by checking for the new `/auth` response/log behavior.
- AC-R3: Identify the next blocking layer: Telegram ingress, Apple auth credential/session, Apple device prompt generation, or user action needed on Apple trusted device.

## Reopen 2 - Apple popup is not being triggered
The user clarified that there is no usable manual `Obtener código de verificación` option for their device/account flow. In their known-good flow, icloudpd must correctly request Apple 2FA so the trusted-device popup appears and provides the code. Current logs show icloudpd reaches `Two-factor authentication is required (2fa)` and asks Telegram for the code, but this may only wait for an already-generated challenge rather than triggering the Apple trusted-device popup.

Additional acceptance criteria:
- AC-R4: Inspect the Apple 2FA implementation path to determine whether the trusted-device prompt is actively triggered or only detected.
- AC-R5: Identify whether icloudpd needs to call/send a trusted-device/SMS challenge endpoint before asking Telegram for the code.
- AC-R6: Recommend or implement the smallest safe fix so `/auth` causes Apple to send/show the code prompt before Telegram asks for it.
