# Meta: Builder handoff (avoid losing chat thread)

- Date: 2026-01-04
- Concern:
  - Moving to GPT Builder/Actions UI may disrupt returning to this chat thread.
- Current state (repo):
  - NoteOps server running locally on 127.0.0.1:8711 with token auth enabled
  - Cloudflare quick tunnel URL:
    - https://correspondence-assignment-approaches-roles.trycloudflare.com
  - actions/openapi.yaml server url updated to trycloudflare (dev)
  - tools/noteops/run-tunnel-dev.ps1 exists for future URL refresh

## Next step (in GPT Builder)
1) Open GPT Builder -> Actions
2) Import OpenAPI from actions/openapi.yaml
3) Set header auth:
   - X-NoteOps-Token = <local secret token> (do not commit)
4) Test:
   - GET /debug/repo
   - POST /log/append

## If chat thread is lost
- Re-run:
  - .\tools\noteops\run-noteops.ps1 -Token <TOKEN>
  - .\tools\noteops\run-tunnel-dev.ps1 -Commit
- Then repeat Builder steps above.
