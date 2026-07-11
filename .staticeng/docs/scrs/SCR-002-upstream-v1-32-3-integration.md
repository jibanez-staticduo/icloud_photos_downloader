# SCR-002: Full Upstream v1.32.3 Integration

## Status
Completed

## Completion
- Completed on 2026-05-30 through TASK-008 and TASK-009.
- Upstream v1.32.3 was integrated, focused tests passed, image was published/deployed, and live auth succeeded.

## Classification
- complexity: complex
- track: spec
- slice: foundation

## Problem
The fork is behind upstream `icloud-photos-downloader/icloud_photos_downloader` and the user wants a full merge/update from upstream, accepting that fork-specific breakage should be fixed afterward. Upstream contains Apple 2FA fixes likely relevant to the current Telegram `/auth` trusted-device popup issue.

## Requested Behavior
- Bring the fork up to date with upstream `master` at or beyond `9857dd88c4c7de49deb712b7d6b12193e23864b9` (`v1.32.3`).
- Preserve fork-specific capabilities: Telegram webhook/MFA/control flow, registry deployment files, Docker entrypoint wrapper, incremental sync/download/repair behavior, and current TASK-002/TASK-004 auth fixes where still applicable.
- Incorporate upstream Apple 2FA fixes including `trigger_push_notification()` and trusted-phone parser fallback.
- Restore passing focused tests or clearly isolate unrelated pre-existing failures.

## Scope
- Full upstream merge/integration.
- Conflict resolution across auth, pyicloud, Docker/build, CLI/config, Telegram extension, sync/download, and tests.
- Evidence-first validation and deploy readiness assessment.

## Out of Scope
- Deploying to live Docker until integration is reviewed and explicitly authorized.
- Deleting secrets, cookies, keyrings, or live config.
- Dropping fork features without explicit user approval.

## Acceptance Criteria
- AC-1: Upstream `master` changes are integrated into a safe working branch or isolated worktree without losing current dirty work.
- AC-2: Fork-specific Telegram auth/control behavior remains present and builds/tests import successfully.
- AC-3: Upstream Apple 2FA push trigger and parser fallback are present and wired into Telegram MFA flow.
- AC-4: Relevant tests for Telegram auth, Apple 2FA, CLI/config, and touched download behavior pass, or failures are documented as pre-existing/unrelated with evidence.
- AC-5: Evidence packet documents merge strategy, conflicts resolved, tests run, remaining risks, and deployment recommendation.

## Risks
- High semantic conflict risk in `src/icloudpd/authentication.py`, `src/pyicloud_ipd/base.py`, CLI/config, Docker files, and tests.
- Current worktree is dirty with user-approved local changes and workflow artifacts.
- Full merge can regress Telegram flow if upstream code removes/overwrites fork extension hooks.

## Decision
Approved by user: perform full upstream merge and fix what breaks in the fork.
