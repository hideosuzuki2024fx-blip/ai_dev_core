# ADR-0003: ユーザーとAIの分担方針

## 🎯 目的
AI（GPT）と人間ユーザーが共同でアプリを開発する際、
**工数削減・再現性・確実性** を最優先する。

---

## 📘 基本原則

### GPT（AI）が行うこと
- すべてのコード・構成・スクリプトは「**コピペで即実行可能な完全形**」で提示。
- 途中省略（例: “ここに貼る”）は禁止。
- 動作確認可能な最小実行単位で出力。
- 自身の生成物は .md / .ps1 / .py に保存できる形にする。

### ユーザー（人間）が行うこと
- 外部操作（GitHub、OS、APIキー設定など）を担当。
- GPTの提示したコードを PowerShell / Python に貼り付けて実行。
- 実行ログをGPTに返し、差分と修正を確認。

### 記録と自動化
- 各工程（#0001〜）を /docs/ADR/ または /docs/product/ に保存。
- 各ステップ終了時、「完了」報告とログ共有を行う。
- 最終的な成果物は完全な再現性を保証する。

### 禁止事項
- 擬似コードや不完全テンプレート。
- 曖昧な省略表現。
- GPTによる省略的な出力。

---

## ⚙️ コード提示方針（サンプル）
GPTが提示するコードは、以下のように**直接実行できる完全形**とする。

\\\python
# 完全コピペ実行可能サンプル
import os
from pathlib import Path

repo_root = Path.home() / "Projects/ai_dev_core"
docs_path = repo_root / "docs" / "ADR"
docs_path.mkdir(parents=True, exist_ok=True)

content = '''# ADR-0003: ユーザーとAIの分担方針
など、必要な情報をすべて含める。（本文省略）など、必要な情報をすべて含める。
'''
(docs_path / "ADR-0003_user_protocol.md").write_text(content, encoding="utf-8")
\\\

---

## ✅ 運用
- GPTは「差分のある変更（Semantic Diff）」のみ行う。
- ユーザーはリポジトリを母艦（Single Source of Truth）として維持。
- すべての変更は /docs/ADR/ に残す。

---

## 🧾 履歴
- 作成者: GPT（AIエンジニア/PM補佐）
- 監修: hideosuzuki2024fx-blip
- 日付: 2025-11-03
