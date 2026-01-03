# Meta: NoteOps Token Auth

- Date: 2026-01-04
- Change: Add optional token auth via NOTEOPS_TOKEN + X-NoteOps-Token header
- Scope: write endpoints (/note/write, /log/append, /normalize/run, /git/commit)
- Behavior:
  - NOTEOPS_TOKEN set => require matching header, else 401
  - NOTEOPS_TOKEN empty => allow (local-dev mode)
- Next TODO:
  - For production, make token mandatory (no local-dev bypass) via config flag
