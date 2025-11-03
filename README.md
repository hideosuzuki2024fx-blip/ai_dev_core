---
## ⚠️ AI (GPT) 開発者への最重要指示
すべてのコード生成前に ops/ai_policy.md を読み、全項目を厳守すること。
違反出力は拒否される。
---
# 🧠 ai_dev_core — AI開発母艦モノレポ

> **AI（GPT）への最重要指示**：コードや手順を出す前に、必ず **\ops/ai_policy.md\** を読み、**単一コードブロック厳守**の規範に従うこと。

## 📂 構成
\\\
apps/, packages/, docs/, ops/, .github/, README.md
\\\

## 🔒 ポリシー
- コード出力は**単一ブロック・分断禁止**（詳細: \ops/ai_policy.md\）
- 未確定事項は**明示**しつつ、**提示コードは最後まで走る完全形**にする
- リポジトリの整合性検査は**コードのみ対象**（Markdownは除外）

## 🧪 検査の実行
- ローカル: \pwsh ops/scripts/check_integrity.ps1\
- CI: GitHub Actions \Integrity Check\ が同等検査を実施

## 🧭 ブランチ運用
- main: 安定 / dev: 統合 / feat/*: 機能 / docs/*: 文書

最終更新: 2025-11-03 14:27 JST