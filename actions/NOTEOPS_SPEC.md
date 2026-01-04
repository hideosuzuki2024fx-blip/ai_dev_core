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
- NOTEOPS_TOKEN が空の場合はローカル開発モードとして認証を# CODE_TRUNCATED（運用では禁止推奨）。

## ガバナンス（commit）
- /git/commit は Amy+Ayase 合意（両方 true）+ decision_ref（logs/critique配下の既存ファイル）必須。
- message は Draft/Review/Final の接頭辞必須。


---

## 🧩 Integrity Allowlist Policy (2026-01-04)
明示的な省略マーカーをIntegrityチェック対象外として扱う。

| マーカー | 意図 | 備考 |
|-----------|------|------|
| `# CODE_TRUNCATED` | 手動・自動省略の明示タグ | Linter・CI除外対象 |
| `# SAMPLE_SNIPPET` | 教材・抜粋コード示唆 | NoteOps Ferment時に補完対象 |
| `# INTERNAL_OMIT` | 内部限定資料除外 | 外部配布時に自動削除 |

> 参照: `ops/scripts/check_integrity.ps1` の `$patterns` 定義から除外済。
