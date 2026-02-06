# URL and PowerShell Rules (Summary)

This file summarizes URL and PowerShell handling constraints for repository operations.

- Prefer `raw.githubusercontent.com` URLs for GitHub file content references.
- Do not rely on GitHub connectors; use directly accessible sources.
- Keep PowerShell operations explicit and reproducible.
- Include related file operations in coherent execution units.
- Do not include `git push` in automation scripts unless explicitly required.

For full normative details, refer to `README.md`.
