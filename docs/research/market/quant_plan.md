# 定量マーケットリサーチ計画（AI Photobook Creator）

## 目的
ダウンロード規模、レビュー傾向、課金レンジ、ランキング推移を定量化し、
「売上が見込める仕様・価格」の初期仮説を導く。

## 対象
- プラットフォーム: Android / iOS / Web
- 分類: 写真編集、フォトアルバム、AI生成（画像・レイアウト）
- 主要KPI: 価格（月/年）、SKU数、レビュー数、評価、ランキング

## 収集スキーマ（CSV）
- competitors.csv
  - app_name,platform,publisher,installs_range,rating,reviews_count,monetization,price_monthly_jpy,price_annual_jpy,export_pdf,offline,notes
- pricing.csv
  - app_name,sku_name,price_jpy,billing_period,store,free_trial_days
- ranks.csv
  - date,store,country,category,rank_free,rank_grossing,rank_paid,notes

## タスク一覧
- T1: 競合リスト作成（上位10〜20）→ competitors.csv
- T2: 価格体系整理（サブスク、IAP）→ pricing.csv
- T3: ランキング取得（国/カテゴリ）→ ranks.csv
- T4: 初期所見のADR化 → docs/ADR/ADR-0006_market_findings.md

## 完了条件
- 3つのCSVが最小10行以上埋まっている
- ADR-0006がコミットされている