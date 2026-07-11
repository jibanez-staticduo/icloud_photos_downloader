# TASK-008 Deployment Recommendation

## Recommendation

Do not deploy this integration yet.

## Rationale

- Upstream v1.32.3 is merged into the safe integration branch.
- Telegram MFA, `/auth` restart behavior, Apple 2FA push trigger, and trusted-phone parser fallback are present and verified by focused tests.
- Download, auth, Telegram, CLI, and compile checks now pass in the integration worktree.
- Production-safe download integrity behavior is preserved: truncated temp files remain `.part` for resume instead of being promoted as complete downloads.
- Reopen 3 focused verification passed after hardening Apple push-trigger response handling and confirming truncated downloads no longer report full success.

## Before Deploying

- Review the final integration diff and decide which NomadWorks/evidence artifacts belong in the code commit.
- Run normal full-suite/CI validation beyond the focused suites if required by maintainers.
- Build and smoke-test the Docker image locally or in CI without touching `/volume2/docker/icloudpd` runtime config.

## Explicit Non-Actions

- No live Docker deployment was performed.
- No `/volume2/docker/icloudpd` config, cookies, sessions, or keyrings were edited.
- No secrets were read or exposed.
