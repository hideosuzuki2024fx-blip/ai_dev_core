# Meta: Actions connectivity (localhost issue)

- Date: 2026-01-04
- Fact:
  - GPTs Actions cannot reliably reach localhost (127.0.0.1) on the developer machine.
- Options:
  - Tunnel for development (ngrok/Cloudflare Tunnel)
  - LAN/VM host for production (recommended)
- Security:
  - NOTEOPS_TOKEN + X-NoteOps-Token required for write endpoints
  - Do NOT commit token values
- Next TODO:
  - Choose connectivity method and record decision in logs/critique
