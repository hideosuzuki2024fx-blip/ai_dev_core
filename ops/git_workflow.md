# AI_DEV_CORE — GPT Git Workflow (Official)

GPT が AI_DEV_CORE でコード生成・修正を行う場合は、
必ず **単一の PowerShell スクリプト** の中で以下の 3 つを実行する。

---

## 1. ファイル操作（作成・置換・追記）

- Set-Content（新規/全置換）
- Add-Content（追記）
- ディレクトリが未作成なら New-Item -ItemType Directory

例：

```powershell
Set-Content -Path "src/core.js" -Value @"
export function login(u,p){
  return u === "admin" && p === "1234";
}
"@
```

---

## 2. Git add（触ったファイルのみ）
GPT は **変更したファイルのみ** を add する。

```powershell
git add "src/core.js"
```

---

## 3. Git commit（Conventional Commits）

- feat: 新機能
- fix: 不具合修正
- docs: 文書
- chore: 雑務
- refactor: 構造変更（非機能）

```powershell
git commit -m "feat: add login function to core.js"
```

---

## ❌ GPT の禁止事項

- push を含めない
- 他のファイルを同時に add しない
- コード省略禁止（…や省略）
- コメントだけ出すの禁止
- ファイル操作と Git を分離するの禁止
- 不明点の推測・捏造禁止

---

## 🎯 このワークフローの目的

- 履歴の安全性最大化
- クリーンな GitLog
- ロールバック容易
- 作業単位が明確
