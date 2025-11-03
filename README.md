# 🧠 ai_dev_core — AI開発母艦モノレポ

あなた（オーナー）とAI（PM/エンジニア/マーケター）が共同で、
**「本当に売れるAIアプリ」**を設計・実装・収益化するための母艦です。

---

## ⚠️ AI (GPT) 開発者への最重要指示
このリポジトリで**コード生成・修正・提案**を行うすべてのAIは、
実行前に必ず以下のポリシーファイルを読み、その内容を厳守すること。

📄 [ops/ai_policy.md](./ops/ai_policy.md)

> 本ポリシーに違反した出力は破棄対象とし、信頼スコアをリセットする。

---

## 📂 構成概要
ai_dev_core/
├─ apps/              # 各アプリ（EmotionCut, TrendHook等）
├─ packages/          # 共通モジュール（ai-core, ui-kit等）
├─ docs/              # 設計・ADR・仕様ドキュメント
├─ ops/               # スクリプト・CI・AIポリシー
└─ README.md          # 本ファイル（エントリーポイント）

---

## 🧪 整合性チェック
- ローカル検査: pwsh ops/scripts/check_integrity.ps1
- CI検査: .github/workflows/integrity.yml
- 検出語句: 中略, 省略, 略, ..., …

---

## 🧭 ブランチ運用
- main：安定版
- dev：統合検証
- feat/*：新機能
- docs/*：ドキュメント更新
コミット形式：feat(scope): summary (#phase)

---

## 🪶 GPT後継者への引継ぎ方針
- /docs/ADR/ADR-0005_project_manifest.md を基点に全情報を継承
- 「記憶」「方針」「制約」「手順」を逐次読み込み、誤出力を防止

---

## 🧩 ライセンス
MIT（予定）

---

最終更新: 2025-11-03 14:15 JST