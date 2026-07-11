---
id: TASK-[PARENT].[SUBTASK]
complexity: complex
track: implementation
slice: logic
status: todo
scr: SCR-[ID]
parent: TASK-[PARENT]
---

# Sub-Task: [Parent ID] - [Sub-Task ID] - [Short Description]

## Parent Task
Use `.staticeng/tasks/...` for parent and subtask files. Never create root `tasks/` files.

## Acceptance Criteria
- [ ] AC-1: [Local criterion]

## Expected Evidence

For implementation subtasks, create or append evidence under `.staticeng/evidences/<task_id>/` with:

- `SUMMARY.md` mapping local acceptance criteria to verification results.
- `logs/` for command output and non-secret verification artifacts.
- `screenshots/` for UI or visual work.

Never place implementation evidence under root `evidences/`.
