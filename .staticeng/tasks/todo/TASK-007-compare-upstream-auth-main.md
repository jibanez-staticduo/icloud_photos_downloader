---
id: TASK-007
title: Compare fork with upstream auth changes
complexity: standard
track: investigation
slice: core
status: todo
assigned_to: tech_lead
handoff_from: product_manager
scr: null
parent: TASK-006
discussion: DISCUSSION-001
---

# Task: Compare Fork With Upstream Auth Changes

## Context
The user suggested updating this fork from the original upstream project to see whether recent upstream changes fix the Apple 2FA/Telegram auth problem. The repository is a fork of `icloud-photos-downloader/icloud_photos_downloader` with remotes:
- `origin`: `git@github.com:jibanez-staticduo/icloud_photos_downloader.git`
- `upstream`: `git@github.com:icloud-photos-downloader/icloud_photos_downloader.git`

The current worktree is dirty with user-approved local changes and NomadWorks artifacts. Do not merge/rebase or modify the worktree in this investigation.

## Classification
- complexity: standard
- track: investigation
- slice: core

## Acceptance Criteria
- AC-1: Fetch upstream refs safely without changing the worktree.
- AC-2: Identify upstream default branch and compare current fork `master` to upstream main/master.
- AC-3: Summarize upstream changes relevant to Apple auth, 2FA/HSA2, pyicloud, MFA, trusted devices, SMS, Docker/runtime, or dependencies.
- AC-4: Identify merge/update risk given the fork's local changes, especially Telegram integration and repair/download changes.
- AC-5: Recommend a safe update strategy: merge, rebase, cherry-pick specific upstream auth changes, or avoid update and continue targeted fix.

## Constraints
- Investigation only: no merge, rebase, checkout, reset, stash, commit, push, or file edits.
- Do not expose secrets.
- Preserve dirty worktree.
- Avoid broad noisy diffs; focus on upstream auth-relevant changes first, then summarize overall divergence.

## Handoff
[Agent Message] From: product_manager To: tech_lead
Please compare this fork with current upstream and determine whether updating from upstream is likely to help the Apple 2FA popup/Telegram auth issue. Fetch refs is allowed; do not modify the worktree or merge anything. Return Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, and Recommended Next Step.
