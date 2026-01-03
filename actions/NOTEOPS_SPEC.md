# NOTEOPS_SPEC (GPTs Actions Boundary)

## 目的
- 再現性・ログ必須・三者合議（Amy/Ayase/Ponta）を **API境界で強制**する。

## Allowlist（書き込み許可）
- NoteMD/0_raw/**, 1_mash/**, 2_ferment/**, 3_article/**
- logs/critique/**, logs/error/**, logs/meta/**
- persona/**, tools/**, actions/**
- .gitattributes, README.md, README_NEW.md

## Token認証（推奨）
- 環境変数 NOTEOPS_TOKEN を設定した場合、書き込み系APIは
  X-NoteOps-Token: <NOTEOPS_TOKEN> が一致しないと **401**。
- NOTEOPS_TOKEN が空の場合はローカル開発モードとして認証を省略（運用では禁止推奨）。

## ガバナンス（commit）
- /git/commit は Amy+Ayase 合意（両方 true）+ decision_ref（logs/critique配下の既存ファイル）必須。
- message は Draft/Review/Final の接頭辞必須。

