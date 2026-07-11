# TASK-008 Full Upstream Integration Evidence Summary

## Reopen 1 Update

- Fixed Telegram invalid-code retry path so Apple `trigger_push_notification()` is attempted again before Telegram re-prompts for a replacement code.
- Added retry coverage in `tests/test_telegram_auth.py` for both successful retry push and failure-tolerant retry push.
- Cleaned generated transient test artifact `tests/tmp-download-integrity/` from the integration worktree after test runs.
- Re-ran focused auth, Telegram, CLI, and download suites and refreshed evidence logs.

## Reopen 1 Verification

- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen1-pytest-telegram.log`: `14 passed`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen1-pytest-authentication.log`: `20 passed, 1 skipped`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen1-pytest-cli.log`: `11 passed`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen1-compileall.log`: compile check passed for `src` and `tests/test_telegram_auth.py`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen1-pytest-download.log`: `33 passed, 17 failed`; failures are isolated to legacy download fixture expectations under the fork's truncated-download integrity behavior.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen1-pytest-download-raw-representative.log`: representative failure keeps `.part` file because fixture payload is detected as truncated (`161 < 1884695`), so expected final file is absent.

## Reopen 1 Acceptance Notes

- Auth, Telegram, and CLI concerns from critic review are resolved in the integration worktree.
- Download suite is not rebaselined in this pass because failures are tied to fork-specific truncated-download protection and cassette fixture sizes; this should be accepted/rebaselined as a product/QA decision rather than silently weakening integrity behavior.
- See `CONFLICTS.md` for semantic conflict notes and artifact exclusions.
- See `DEPLOYMENT_RECOMMENDATION.md` for current deploy guidance.

## Reopen 2 Update

- User decision: keep production truncated-file protection and fix/adapt legacy tests instead of weakening integrity behavior.
- Classified the remaining download failures as test fixture issues: VCR media responses contain placeholder/truncated bodies while iCloud metadata advertises full asset sizes.
- Added helper-side fixture normalization in `tests/helpers/__init__.py` so non-truncation tests synthesize complete media payloads matching asset metadata.
- Kept explicit truncation behavior covered by `DownloadDownloadIntegrityTestCase.test_short_temp_file_is_not_promoted` and rebaselined `test_resume_download` to expect `.part` retention when the resumed fixture remains short.
- Rebaselined affected test assertions that previously depended on debug-only EXIF error logs or legacy dedupe suffix output.

## Reopen 2 Verification

- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen2-pytest-download-pass2.log`: `50 passed`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen2-pytest-telegram.log`: `14 passed`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen2-pytest-authentication.log`: `20 passed, 1 skipped`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen2-pytest-cli.log`: `11 passed`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen2-compileall.log`: compile check passed for `src`, `tests/test_download_photos.py`, and `tests/test_telegram_auth.py`.

## Reopen 2 Acceptance Notes

- Focused download, auth, Telegram, CLI, and compile checks now pass with known authentication skip only.
- Production integrity behavior remains intact: short temp files are not promoted; oversize temp files are moved aside.
- See `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen2-download-test-adaptation.diff` for the test/helper changes made to model complete fixture payloads without changing production code.

## Result

- Status: focused suites pass; review/build still required before deploy.
- Safe branch/worktree: `/tmp/opencode/icloudpd-task-008`, branch `task-008-upstream-integration`.
- Fork base: `8ccf4a382bfaa31b139c986f77cb0e4de4930c3f`.
- Upstream integrated: `upstream/master` at `9857dd88c4c7de49deb712b7d6b12193e23864b9` (`v1.32.3`).
- Integration merge commit: `3f114d6`.
- Original dirty worktree: preserved; no reset, clean, stash, live deploy, or `/volume2/docker/icloudpd` edits were performed.

## Reopen 3 Update

- Inspected the existing dirty integration worktree first; Reopen 2 already contained most truncated-download and Apple 2FA push changes.
- Hardened `PyiCloudService.trigger_push_notification()` further so response objects without `ok` are evaluated by status code when available and warnings only include status, not request data or secrets.
- Added/fixed auth tests for non-success trusted-device push responses and preserved `PyiCloudAPIResponseException` behavior.
- Reverified the truncated download path: incomplete resumed downloads leave `.part`, avoid the final success message, and return exit code `1` with an incomplete-download message.
- Removed generated `tests/tmp-download-integrity/` after verification.

## Reopen 3 Verification

- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen3-pytest-download.log`: `50 passed` for `TZ=UTC pytest tests/test_download_photos.py -q` using the local task venv.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen3-pytest-telegram.log`: `14 passed` for `pytest tests/test_telegram_auth.py -q`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen3-pytest-authentication.log`: `22 passed, 1 skipped` for `pytest tests/test_authentication.py -q`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen3-pytest-cli.log`: `11 passed` for `pytest tests/test_cli.py -q`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen3-compileall.log`: compile check passed for `src`, `tests/test_download_photos.py`, and `tests/test_telegram_auth.py`.

## Reopen 4 Main Workspace Copy

- User explicitly authorized bringing all integration worktree changes from `/tmp/opencode/icloudpd-task-008` back to `/home/staticduo/git/icloud_photos_downloader`.
- Copied the integration worktree into the main workspace with `rsync`, excluding `.git`, virtualenv/cache artifacts, Python bytecode, and generated `tests/tmp-download-integrity/`.
- Did not deploy and did not touch `/volume2/docker/icloudpd` config, cookies, or keyrings.
- Removed generated `tests/tmp-download-integrity/` after target validation.

## Reopen 4 Target Verification

- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen4-target-pytest-download.log`: `50 passed` for `TZ=UTC pytest tests/test_download_photos.py` in the main workspace.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen4-target-pytest-telegram.log`: `14 passed` for `pytest tests/test_telegram_auth.py` in the main workspace.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen4-target-pytest-authentication.log`: `22 passed, 1 skipped` for `pytest tests/test_authentication.py` in the main workspace.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen4-target-pytest-cli.log`: `11 passed` for `pytest tests/test_cli.py` in the main workspace.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/reopen4-target-compileall.log`: compile check passed for `src` and `tests` in the main workspace.

## Preserved Fork Features

- Telegram extension/control remains under `src/icloudpd/extensions/telegram/`.
- Telegram MFA handler remains wired through `src/icloudpd/extensions/telegram/mfa.py` and `src/icloudpd/authentication.py`.
- `/auth` force-refresh/restart semantics remain covered by `tests/test_telegram_auth.py`.
- Docker registry/deploy files remain present, including `DEPLOY_REGISTRY.md`, `release-image.sh`, and the entrypoint wrapper.
- Incremental sync/download/repair changes remain present in `src/icloudpd/base.py`, `src/icloudpd/download.py`, `src/icloudpd/file_cache.py`, and `src/pyicloud_ipd/services/photos.py`.

## Upstream Apple 2FA Fixes

- `src/pyicloud_ipd/base.py` includes `trigger_push_notification()` using `PUT /verify/trusteddevice/securitycode`.
- `src/pyicloud_ipd/sms.py` includes trusted-phone parser fallback for `bridgeInitiateData.phoneNumberVerification.trustedPhoneNumbers`.
- `src/icloudpd/authentication.py` calls `trigger_push_notification()` for console, WebUI, and Telegram MFA flows.
- `tests/test_telegram_auth.py` verifies Telegram MFA triggers Apple push before requesting a Telegram code and continues when push triggering fails.
- `tests/test_authentication.py` includes the trusted-phone fallback parser test.

## Fixes Applied During Fallback

- Restored `Authenticating...` as an info log so existing auth tests and user output expectations still hold.
- Restored user-visible info logs for lookup/download/existing/skip/EXIF/delete/resume flows that had been hidden at debug level.
- Fixed non-TTY password provider behavior so Docker still omits console while pytest remains deterministic.
- Removed a local import shadowing `create_filename_builder`, fixing delete-after-download crashes.
- Re-ran focused tests after these changes.

## Test Evidence

- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/pip-install-test-env.log`: isolated venv setup and package install.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/pytest-auth-telegram.log`: `32 passed, 1 skipped`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/pytest-cli-download.log`: `47 passed, 15 failed` under `TZ=UTC`.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/pytest-download-fixes-smoke.log`: intermediate smoke log showing delete-after-download fixed and timezone-only assertions before UTC rerun.

## Remaining Failures

- Remaining failures are in `tests/test_download_photos.py` legacy download fixture cases.
- Primary cause: current merged download integrity behavior refuses to promote truncated `.part` files when the downloaded byte count differs from iCloud metadata. Existing VCR fixtures often contain tiny/truncated payloads but tests expect final files to exist.
- Secondary cause: EXIF exception tests no longer hit their expected mocked error logs after the merged download path changes.

## Evidence Files

- `CONFLICTS.md`: strategy, conflict notes, semantic fixes, remaining risk.
- `DEPLOYMENT_RECOMMENDATION.md`: explicit deploy recommendation.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/integration-history.log`: recent branch history.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/upstream-delta-stat.log`: branch delta from upstream.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/dirty-delta-stat.log`: current dirty delta in integration worktree.
- `.staticeng/evidences/TASK-008-full-upstream-integration/logs/dirty-files-after-integration.txt`: changed files list.

## Recommendation

Do not deploy yet. The focused integration suites now pass, but the branch still needs normal review, final commit selection, and build/publish validation before any live rollout.
