# 🚀 MVP実装タスク分解書
**対象:** AI Photobook Creator（仮称）  
**作成日:** 2025-11-05 07:28 +09:00

> 本ドキュメントは app_spec.md の「MVPスコープ」「非機能要件」「パイプライン設計」に基づく実行タスク定義である。  
> 実装順序は依存関係に基づき決定。タスクIDは Cxx 形式で管理する。

---

## 🧱 C-01: 環境・依存整備
| ID | 内容 | 実行者 | 依存 | 成果物 |
|----|------|--------|------|--------|
| C01-1 | Python仮想環境構築 (venv / poetry) | 開発 | なし | .venv, requirements.txt |
| C01-2 | PDF出力モジュール依存固定 (pandoc/weasyprint) | 開発 | C01-1 | requirements.txt更新 |
| C01-3 | FastAPI起動テンプレ作成 (main.py) | GPT | C01-1 | src/backend/main.py |
| C01-4 | ReactまたはHTMLテンプレ初期化 | GPT | C01-1 | src/frontend/index.html |

---

## 🖼️ C-02: 生成パイプライン実装
| ID | 内容 | 実行者 | 依存 | 成果物 |
|----|------|--------|------|--------|
| C02-1 | ストーリーボード構造 (storyboard.json) 定義 | GPT | C01 | schemas/storyboard.json |
| C02-2 | 画像生成キックAPI (/generate) 実装 | GPT | C01-3 | main.py |
| C02-3 | 参照画像アップロード＋統一プリセット処理 | GPT | C02-1 | src/backend/presets.py |
| C02-4 | assets/保存構造と進捗ログ | 開発 | C02-2 | assets/\*, logs/\* |
| C02-5 | layoutテンプレ結合処理 | GPT | C02-3 | layout_engine.py |

---

## 📄 C-03: 出力テンプレート & 組版
| ID | 内容 | 実行者 | 依存 | 成果物 |
|----|------|--------|------|--------|
| C03-1 | HTMLテンプレ生成 (3種: Minimal/Editorial/Zine) | GPT | C02 | docs/templates/\* |
| C03-2 | pandoc連携でPDF出力実験 | 開発 | C03-1 | outputs/sample.pdf |
| C03-3 | メタデータヘッダ自動埋込 (title/author/date) | GPT | C03-2 | html→pdf統合済み出力 |

---

## 💰 C-04: 価格・A/Bテスト導線
| ID | 内容 | 実行者 | 依存 | 成果物 |
|----|------|--------|------|--------|
| C04-1 | 価格変数を config/plan.yml に定義 | GPT | C03 | config/plan.yml |
| C04-2 | 3価格帯 (¥780/¥980/¥1280) のA/B設定 | 開発 | C04-1 | data/ab_variants.yml |
| C04-3 | CIで自動切替 (deploy_lp.yml対応) | GPT | C04-2 | .github/workflows/deploy_lp.yml 更新 |

---

## 🔍 C-05: テスト & 計測
| ID | 内容 | 実行者 | 依存 | 成果物 |
|----|------|--------|------|--------|
| C05-1 | 単体テスト（生成API・出力モジュール） | 開発 | C02/C03 | tests/test_generate.py |
| C05-2 | e2eテスト (生成→レイアウト→出力) | 開発 | C05-1 | tests/test_end2end.py |
| C05-3 | KPIログスキーマ設計 (北極星指標) | GPT | C04 | analytics/kpi_schema.json |

---

## 📆 推奨スケジュール
| 週 | マイルストーン | 完了判定 |
|----|----------------|----------|
| W1 | 環境構築＋基礎API完了 | FastAPIサーバ起動確認 |
| W2 | 画像生成〜出力一連動作 | sample.pdf生成成功 |
| W3 | 価格A/B・テンプレA/B導入 | variant設定・反映OK |
| W4 | CI整合＆安定化 | GitHub Pages公開・404なし |

---

## ✅ 完了条件
- docs/specs/app_spec.md の全MVP要件に対応するタスクが定義されている  
- 生成・出力のフローがローカルで再現できる  
- KPI計測ロジックが導入され、分析に耐えうる構造になっている

---

## 📌 次フェーズ予定（Phase D: MVP構築）
完了後に ops/init_mvp_build.ps1 を自動生成し、環境構築→サンプル生成→PDF出力までを一括実行。

---