# ADR-0003: LP多言語化とHero画像生成方針

## 背景
- LPの国際展開を見据え、Heroテキスト・画像の英日2言語展開を標準化。
- 今後、image_genを活用し自動ビジュアル差分（A/Bテスト）を行う。

## 決定
- Hero構成要素（タイトル・サブタイトル）をJSONで管理。
- Pythonスクリプト generate_i18n_visual.py によりHero画像を英日両方自動生成。
- 出力先:
  - /docs/product/img/hero_<app>_<lang>.jpg
  - /docs/product/i18n/hero_i18n_map.json

## 実行手順
PowerShell:
    cd $HOME/Projects/ai_dev_core
    python ops/scripts/generate_i18n_visual.py

## 今後の展開
- image_genツールでビジュアル差分を自動生成し、A/Bテスト指標（CTR・CVR）を記録。
- 翻訳は固定文型からLLM出力補助へ移行可能。
