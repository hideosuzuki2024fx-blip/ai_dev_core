# Error Log: /repo/status returns 500

- Date: 2026-01-04
- Context: Smoke test via Invoke-RestMethod from non-repo cwd
- Affected Path(s): tools/noteops/app.py, endpoint /repo/status
- Severity: Medium

## 1. 症状（Symptom）
- GET http://127.0.0.1:8711/repo/status -> Internal Server Error

## 2. 再現手順（Repro Steps）
1. Start NoteOps
2. Invoke-RestMethod http://127.0.0.1:8711/repo/status

## 3. 原因仮説（Root Cause Hypothesis）
- NoteOps が参照する REPO_TOP が git ルートと不一致で、git コマンドが失敗していた可能性。

## 4. 回避策（Workaround）
- /debug/repo で REPO_TOP を確認し、git ルートへ揃える。

## 5. 恒久対策（Permanent Fix）
- REPO_TOP を git rev-parse --show-toplevel で確定する実装へ変更（app.py v0.2.0）。

## 6. 追跡（Follow-ups）
- TODO: 起動時に REPO_TOP をログ出力
- Owner: Ponta