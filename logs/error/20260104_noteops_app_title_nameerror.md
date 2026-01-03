# Error Log: NoteOps startup NameError (APP_TITLE not defined)

- Date: 2026-01-04
- Context: Token auth patch introduced NameError, server failed to start
- Affected Path(s): tools/noteops/app.py
- Severity: High

## 1. 症状（Symptom）
- NameError: name 'APP_TITLE' is not defined
- Server not listening -> connection refused on 127.0.0.1:8711

## 2. 再現手順（Repro Steps）
1. Apply patch
2. Start NoteOps
3. Observe NameError and server exit

## 3. 原因仮説（Root Cause Hypothesis）
- 置換パッチがファイル先頭の定義順/変数定義を破壊した可能性。

## 4. 回避策（Workaround）
- app.py を既知の完全版で上書きして復旧。

## 5. 恒久対策（Permanent Fix）
- app.py への変更は差分置換ではなく、関数単位の安全な編集（またはテンプレ生成）に統一する。
- 起動前に self-check（import時の必須定義確認）を追加検討。

## 6. 追跡（Follow-ups）
- TODO: /debug/repo に tokenEnabled を常に表示
- Owner: Ponta