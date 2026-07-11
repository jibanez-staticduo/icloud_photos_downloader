---
id: TASK-[ID]
complexity: standard
track: implementation
slice: logic
status: todo
scr: null
parent: null
assigned_to: product_manager
handoff_from: null
reopened_count: 0
---

# Task: [Task ID] - [Short Description]

## Objective
[Short description of the intended outcome and scope.]

## Acceptance Criteria
- [ ] AC-1: [Primary behavioral or task outcome]
- [ ] AC-2: Relevant verification is completed and evidence is recorded against each acceptance criterion.

## Expected Evidence

Create `.staticeng/evidences/<task_id>/` with:

- `SUMMARY.md` mapping each numbered acceptance criterion to verification results.
- `logs/` containing command outputs, test logs, build logs, and other non-secret verification artifacts.
- `screenshots/` for UI or visual work.

Never place task files under root `tasks/`; use `.staticeng/tasks/...`.
Never place implementation evidence under root `evidences/`; use `.staticeng/evidences/<task_id>/`.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** [unit test | integration test | e2e | manual check | doc review]
  - **Evidence:** `.staticeng/evidences/<task_id>/[file-or-folder]`
