---
id: TASK-008
title: Full upstream v1.32.3 integration
complexity: complex
track: implementation
slice: foundation
status: todo
assigned_to: workflow_runner
handoff_from: product_manager
scr: SCR-002
parent: TASK-007
discussion: DISCUSSION-001
---

# Task: Full Upstream v1.32.3 Integration

## Context
The user explicitly wants a full merge/update from upstream and accepts fixing whatever breaks in the fork afterward. Upstream `master` has Apple 2FA fixes likely needed for `/auth` to trigger trusted-device popup codes.

Current repository state:
- Fork branch: `master` at `8ccf4a382bfaa31b139c986f77cb0e4de4930c3f`.
- Upstream `master`: `9857dd88c4c7de49deb712b7d6b12193e23864b9` (`v1.32.3`).
- Merge-base: `3a97872f9f44ac49bda54b66b5170575bd22ff18`.
- Dirty worktree includes user-approved source edits and NomadWorks artifacts. Preserve them.

## Classification
- complexity: complex
- track: implementation
- slice: foundation

## Acceptance Criteria
- AC-1: Integrate upstream `master` fully in a safe branch/worktree strategy that preserves current dirty changes.
- AC-2: Preserve fork-specific functionality: Telegram extension/MFA/control, registry deploy flow, Docker wrapper, incremental sync/download/repair changes, and current `/auth` force-refresh semantics.
- AC-3: Include upstream auth fixes: `trigger_push_notification()` and trusted-phone parser fallback, wired into Telegram MFA.
- AC-4: Resolve conflicts and run relevant tests; provide evidence for pass/fail status.
- AC-5: Produce evidence packet under `.staticeng/evidences/TASK-008-full-upstream-integration/` with `SUMMARY.md`, conflict notes, logs, and deployment recommendation.

## Expected Evidence
- Merge strategy and exact refs.
- Conflict list and resolution notes.
- Test/build logs.
- Code references for auth integration and preserved fork features.

## Constraints
- Do not deploy to live Docker in this task.
- Do not delete live cookies/keyrings or edit `/volume2/docker/icloudpd` config.
- Do not expose secrets.
- If current dirty worktree cannot be safely preserved, stop and escalate before destructive actions.

## Handoff
[Agent Message] From: product_manager To: workflow_runner
Run a full upstream integration from `upstream/master` into the fork, preserving current local/fork changes and fixing breakage. This is complex work; use safe branch/worktree strategy, perform pre-sync, resolve conflicts, run relevant tests, and return full evidence. Do not deploy.

# Execution History

## Workflow Runner Attempt 1 - Tool failure
NomadFlow failed before completion with: `undefined is not an object (evaluating 'runResult.data.parts')`. Treat as tooling failure, not implementation result. Reassigning execution path while preserving original scope and constraints.
