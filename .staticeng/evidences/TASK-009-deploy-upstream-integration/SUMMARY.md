# TASK-009 Evidence Summary

## Scope
- Built and published the full upstream integration image from `/home/staticduo/git/icloud_photos_downloader` using `./release-image.sh`.
- Pulled and recreated only the live `icloudpd` service from `/volume2/docker/icloudpd/docker-compose.yaml`.
- Did not edit `/volume2/docker/icloudpd/.env`, compose storage mappings, cookies, sessions, keyrings, or photos.
- Did not send Telegram `/auth` as the agent.

## Deployment
- Source branch: `master`
- Source revision: `8ccf4a382bfaa31b139c986f77cb0e4de4930c3f`
- Published tags: `docker.staticduo.com/icloudpd:latest`, `docker.staticduo.com/icloudpd:sha-8ccf4a3`, `docker.staticduo.com/icloudpd:branch-master`
- Published digest: `docker.staticduo.com/icloudpd@sha256:ecd56507a1f90276fa58eb6ed88eeb4c6dbfe532c181ad6a7652fccb381367f0`
- Image ID: `sha256:26e78995edb860b1bd65ce11d3af9d5d2e8a04ef50e102c680df626fd5d0df59`

## Verification
- PASS: `./release-image.sh` completed and pushed all documented tags.
- PASS: `docker compose -f /volume2/docker/icloudpd/docker-compose.yaml pull icloudpd` completed for service `icloudpd`.
- PASS: `docker compose -f /volume2/docker/icloudpd/docker-compose.yaml up -d icloudpd` recreated and started only service `icloudpd`.
- PASS: Container `icloudpd` is `running` and Docker health is `healthy` after recreation.
- PASS: Running image label `org.opencontainers.image.revision` is `8ccf4a382bfaa31b139c986f77cb0e4de4930c3f`.
- PASS: Runtime logs show Telegram webhook initialization, Telegram auth-code request/receipt, successful authentication, and incremental sync startup with identifiers redacted.

## Evidence Files
- `.staticeng/evidences/TASK-009-deploy-upstream-integration/logs/compose-ps.txt`: compose service status after deployment.
- `.staticeng/evidences/TASK-009-deploy-upstream-integration/logs/container-state.txt`: container running/health/image state.
- `.staticeng/evidences/TASK-009-deploy-upstream-integration/logs/image-inspect.txt`: local image ID, repo digest, OCI revision/version/source labels.
- `.staticeng/evidences/TASK-009-deploy-upstream-integration/logs/startup-sanitized.log`: sanitized post-deploy startup and auth-flow logs.
