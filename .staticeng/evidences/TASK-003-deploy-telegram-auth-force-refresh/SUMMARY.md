# TASK-003 Evidence Summary

## Scope
- Deployed the TASK-002 Telegram `/auth` force-refresh changes to the live `icloudpd` Docker service.
- Used the documented registry flow from `DEPLOY_REGISTRY.md`.
- Did not edit secrets, compose volume mappings, cookies, or keyrings.

## Acceptance Criteria
- AC-1: PASS. Built and published `docker.staticduo.com/icloudpd:latest`, `docker.staticduo.com/icloudpd:sha-8ccf4a3`, and `docker.staticduo.com/icloudpd:branch-master` with `./release-image.sh`.
- AC-2: PASS. Pulled and recreated only the `icloudpd` service using `/volume2/docker/icloudpd/docker-compose.yaml`.
- AC-3: PASS. Container `icloudpd` is running and healthy after recreation.
- AC-4: PARTIAL PASS. Runtime image metadata confirms deployed image revision `8ccf4a382bfaa31b139c986f77cb0e4de4930c3f`, matching the checkout containing the TASK-002 `/auth` fresh-auth implementation. Startup logs show Telegram MFA request behavior and no plaintext six-digit code. Direct live `/auth` interaction was not triggered by this agent to avoid sending user-visible Telegram commands without an explicit instruction.
- AC-5: PASS. Evidence packet exists at `.staticeng/evidences/TASK-003-deploy-telegram-auth-force-refresh/` with sanitized logs under `.staticeng/evidences/TASK-003-deploy-telegram-auth-force-refresh/logs/`.

## Verification
- PASS: `./release-image.sh`; evidence in `.staticeng/evidences/TASK-003-deploy-telegram-auth-force-refresh/logs/build-publish.log`.
- PASS: `docker compose -f /volume2/docker/icloudpd/docker-compose.yaml pull icloudpd`; evidence in `.staticeng/evidences/TASK-003-deploy-telegram-auth-force-refresh/logs/deploy.log`.
- PASS: `docker compose -f /volume2/docker/icloudpd/docker-compose.yaml up -d icloudpd`; evidence in `.staticeng/evidences/TASK-003-deploy-telegram-auth-force-refresh/logs/deploy.log`.
- PASS: `docker inspect icloudpd` shows `status=running` and `health=healthy`; evidence in `.staticeng/evidences/TASK-003-deploy-telegram-auth-force-refresh/logs/verify.log`.
- PASS: `docker image inspect docker.staticduo.com/icloudpd:latest` shows revision `8ccf4a382bfaa31b139c986f77cb0e4de4930c3f` and image ID `sha256:1319d91977f7e11929590e3cb86c82b976a7a7c73bf20fe3e3dc723d56862a99`; evidence in `.staticeng/evidences/TASK-003-deploy-telegram-auth-force-refresh/logs/verify.log`.

## Sanitization
- Logs exclude Telegram token, Telegram chat ID, credentials, cookies, session data, six-digit codes, and account email addresses.
- Full raw Docker output was not stored because it may contain account-identifying runtime lines.

## Notes
- The container entered MFA-required flow after restart and requested the authentication code via Telegram.
- No compose config, `.env`, storage volume mapping, cookie, or keyring file was changed.
