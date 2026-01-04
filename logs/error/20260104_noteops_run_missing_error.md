# Error Log: NoteOps run script missing (path resolved to System32)

- Date: 2026-01-04
- Context: Write-Utf8NoBomLf wrote to System32 due to non-repo working directory
- Affected Path(s): logs/error/20260104_noteops_run_missing_error.md
- Severity: Medium

## 1. 症状（Symptom）
- Could not find a part of the path 'C:\WINDOWS\System32\logs\error\# CODE_TRUNCATED'

## 2. 再現手順（Repro Steps）
1. PowerShell current dir is not repo top
2. Write-Utf8NoBomLf -Path logs/error/# CODE_TRUNCATED (relative)
3. Path resolves under System32 and fails

## 3. 原因仮説（Root Cause Hypothesis）
- 相対パスをカレント基準で書く関数設計。

## 4. 回避策（Workaround）
- Set-Location (git rev-parse --show-toplevel) を常に先に行う。

## 5. 恒久対策（Permanent Fix）
- repo top を真理源にして絶対パスへ解決する Write-Utf8NoBomLf_AtRepoTop を採用。

## 6. 追跡（Follow-ups）
- TODO: bootstrap系スクリプトは全て AtRepoTop 版に統一
- Owner: Ponta