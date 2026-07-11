# TASK-005 Evidence Summary

## Scope
- Built and published the TASK-004 image through the documented registry flow.
- Pulled and recreated only the live `icloudpd` service from `/volume2/docker/icloudpd/docker-compose.yaml`.
- Did not edit secrets, compose mappings, cookies, keyrings, or storage mappings.
- Did not send Telegram `/auth`; runtime logs already showed the service requesting a Telegram authentication code after deployment.

## Deployment
- Source branch: `master`
- Source revision: `8ccf4a382bfaa31b139c986f77cb0e4de4930c3f`
- Published tags: `docker.staticduo.com/icloudpd:latest`, `docker.staticduo.com/icloudpd:sha-8ccf4a3`, `docker.staticduo.com/icloudpd:branch-master`
- Published digest: `docker.staticduo.com/icloudpd@sha256:10eb718c967a720116195c48c6c2ddeca2a86419853921ea5982f19a11ec20e4`

## Verification
- PASS: `docker compose -f /volume2/docker/icloudpd/docker-compose.yaml pull icloudpd`
- PASS: `docker compose -f /volume2/docker/icloudpd/docker-compose.yaml up -d icloudpd`
- PASS: `icloudpd` is running and healthy after recreation.
- PASS: Running image label `org.opencontainers.image.revision` is `8ccf4a382bfaa31b139c986f77cb0e4de4930c3f`.
- PARTIAL: Runtime logs after deployment show the Telegram authentication code request, but not a separate successful priming line; the deployed TASK-004 code performs `get_trusted_phone_numbers()` before `request_auth_code()` and only logs priming failures.

## Evidence Files
- `.staticeng/evidences/TASK-005-deploy-apple-2fa-priming/logs/build-publish.log`: image tags, digest, platform, and revision label.
- `.staticeng/evidences/TASK-005-deploy-apple-2fa-priming/logs/deploy-verify.log`: compose status, container health, image ID, digest, and revision label.
- `.staticeng/evidences/TASK-005-deploy-apple-2fa-priming/logs/runtime-sanitized.log`: sanitized post-deploy runtime logs.
- `.staticeng/evidences/TASK-005-deploy-apple-2fa-priming/logs/auth-flow-sanitized.log`: sanitized auth-related runtime lines.
- `.staticeng/evidences/TASK-005-deploy-apple-2fa-priming/logs/deployed-code-diff.patch`: deployed TASK-004 auth code diff showing the priming call order.
