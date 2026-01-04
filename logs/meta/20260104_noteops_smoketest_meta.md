# Meta: NoteOps Smoke Test

- Date: 2026-01-04
- RepoTop (expected): E:\ai_dev_core
- Endpoints exercised:
  - GET /debug/repo  => OK (repoTop resolved to E:\ai_dev_core)
  - GET /repo/status => OK (after repoTop detection fix)
  - POST /note/write => OK (wrote to NoteMD/0_raw/# CODE_TRUNCATED)
  - POST /log/append => OK (wrote to logs/meta/# CODE_TRUNCATED)

- Notes:
  - Initial /repo/status returned 500 before repoTop detection fix.
  - .venv_noteops was created locally and is now ignored via .gitignore.
- Next TODO:
  - Add X-NoteOps-Token auth before exposing NoteOps beyond localhost.
