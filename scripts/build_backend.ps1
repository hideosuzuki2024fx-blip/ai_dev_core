# Rebuild main.py and index.html safely
$Root    = Join-Path $HOME "Projects/ai_dev_core"
$Backend = Join-Path $Root "src/backend"
$Static  = Join-Path $Root "src/static"
$Outputs = Join-Path $Root "outputs"

New-Item -ItemType Directory -Path $Backend -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType Directory -Path $Static  -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType Directory -Path $Outputs -ErrorAction SilentlyContinue | Out-Null

# --- main.py ---
$MainPy = Join-Path $Backend "main.py"
if (Test-Path $MainPy) { Copy-Item $MainPy "$MainPy.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Force }
$Main = @"
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import csv
from weasyprint import HTML

ROOT = Path.home() / "Projects" / "ai_dev_core"
OUTPUTS = ROOT / "outputs"
STATIC = ROOT / "src" / "static"
OUTPUTS.mkdir(parents=True, exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
app.mount("/files",  StaticFiles(directory=str(OUTPUTS)), name="files")

@app.post("/csv")
async def create_csv(title: str = Form(# CODE_TRUNCATED), captions: str = Form("")):
    filename = f"{title.replace(' ', '_')}.csv"
    csv_path = OUTPUTS / filename
    rows = []
    for line in captions.splitlines():
        if "," in line:
            k, v = line.split(",", 1)
            rows.append([k.strip(), v.strip()])
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["caption", "text"])
        w.writerows(rows)
    return {"ok": True, "filename": filename}

@app.get("/list_csv")
async def list_csv():
    items = [f.name for f in OUTPUTS.glob("*.csv")]
    return {"ok": True, "items": items}

@app.post("/pdf")
async def create_pdf(
    title: str = Form(# CODE_TRUNCATED),
    csv_name: str = Form(# CODE_TRUNCATED),
    files: list[UploadFile] = None
):
    csv_path = OUTPUTS / csv_name
    if not csv_path.exists():
        return JSONResponse({"ok": False, "error": "CSVが存在しません"}, status_code=400)
    if not files:
        return JSONResponse({"ok": False, "error": "画像がありません"}, status_code=400)

    # CSV読み込み（caption列がない/空のケースにも耐性）
    captions = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        # caption列インデックス推定
        cap_idx = None
        for i, h in enumerate(header):
            if str(h).strip().lower() == "caption":
                cap_idx = i; break
        if cap_idx is None:
            # ヘッダなしとみなし、先頭列をcaption扱い
            captions = [row[0].strip() for row in [header] + list(reader) if row]
        else:
            captions = [row[cap_idx].strip() for row in reader if row and len(row) > cap_idx]

    # 画像保存
    img_paths = []
    for img in files:
        out = OUTPUTS / img.filename
        out.write_bytes(await img.read())
        img_paths.append(out)

    # HTML構成：表紙1P + 画像+キャプション（同ページ内）×N
    html_parts = []
    html_parts.append(f"""
    <section style='page-break-after: always; text-align:center;'>
      <h1 style='font-size:48px; margin-top:200px;'>{title}</h1>
    </section>
    """)
    for idx, p in enumerate(img_paths):
        cap = captions[idx] if idx < len(captions) else ""
        img_uri = Path(p).as_uri()  # file:///C:/# CODE_TRUNCATED に変換
        html_parts.append(f"""
        <section style='page-break-after: always;'>
          <div style='text-align:center;'>
            <img src="{img_uri}" style="max-width:100%; height:auto; margin:0 auto 16px auto;" />
            <div style="font-size:20px; color:#222;">{cap}</div>
          </div>
        </section>
        """)

    html = f"<html><body>{''.join(html_parts)}</body></html>"
    pdf_name = f"{title.replace(' ', '_')}.pdf"
    pdf_path = OUTPUTS / pdf_name
    HTML(string=html).write_pdf(str(pdf_path))
    return RedirectResponse(url=f"/preview?file={pdf_name}", status_code=303)

@app.get("/preview")
async def preview(file: str):
    pdf_path = OUTPUTS / file
    return FileResponse(pdf_path, media_type="application/pdf")
"@

[IO.File]::WriteAllText($MainPy, $Main, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "✅ main.py 再生成: $MainPy" -ForegroundColor Green

# --- index.html ---
$Html = Join-Path $Static "index.html"
if (Test-Path $Html) { Copy-Item $Html "$Html.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Force }
$Page = @"
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <title>📘 CSV→PDF Photobook</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
  <div class="max-w-3xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-4">📷 Photobook CSV Generator</h1>

    <section class="bg-white p-4 rounded-xl shadow mb-6">
      <h2 class="font-semibold mb-2">A. CSV作成（保存先: outputs/）</h2>
      <form id="csvForm" class="space-y-2">
        <input name="title" type="text" placeholder="CSVのタイトル" class="w-full border rounded px-3 py-2" required />
        <textarea name="captions" rows="5" class="w-full border rounded px-3 py-2"
          placeholder="caption,text&#10;Morning Light,Sunrise over the coast.&#10;Evening Calm,Soft orange reflections on the sea."></textarea>
        <button class="w-full bg-emerald-600 text-white py-2 rounded hover:bg-emerald-700">CSV生成</button>
      </form>
      <div id="csvMsg" class="text-sm text-gray-600 mt-2"></div>
    </section>

    <section class="bg-white p-4 rounded-xl shadow">
      <h2 class="font-semibold mb-2">B. PDF生成（表紙 → 画像+キャプション × N）</h2>
      <form id="pdfForm" class="space-y-2" enctype="multipart/form-data">
        <input name="title" type="text" placeholder="フォトブックのタイトル" class="w-full border rounded px-3 py-2" required />
        <div class="flex gap-2 items-center">
          <label class="text-sm text-gray-700">保存済みCSV</label>
          <select id="csvSelect" name="csv_name" class="flex-1 border rounded px-3 py-2"></select>
          <button id="reloadCsv" type="button" class="border px-3 py-2 rounded">再読込</button>
        </div>
        <div>
          <label class="text-sm text-gray-700">画像（複数可・順番＝ページ順）</label>
          <input name="files" type="file" accept="image/*" multiple class="w-full border rounded p-2" required />
        </div>
        <button class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">PDF生成</button>
      </form>
      <div id="pdfMsg" class="text-sm text-gray-600 mt-2"></div>
    </section>
  </div>

<script>
async function loadCsvList() {
  const sel = document.getElementById('csvSelect');
  sel.innerHTML = "";
  try {
    const r = await fetch('/list_csv');
    const j = await r.json();
    if (!j.ok || !j.items || !j.items.length) {
      sel.innerHTML = "<option value=''>（CSVなし）</option>";
      return;
    }
    for (const name of j.items) {
      const o = document.createElement('option');
      o.value = name; o.textContent = name;
      sel.appendChild(o);
    }
  } catch(e) {
    sel.innerHTML = "<option value=''>（読み込み失敗）</option>";
  }
}
document.getElementById('reloadCsv').addEventListener('click', loadCsvList);
window.addEventListener('DOMContentLoaded', loadCsvList);

document.getElementById('csvForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const msg = document.getElementById('csvMsg');
  msg.textContent = "⏳ 生成中# CODE_TRUNCATED";
  const fd = new FormData(e.target);
  const r = await fetch('/csv', { method: 'POST', body: fd });
  const j = await r.json();
  if (r.ok && j.ok) {
    msg.textContent = "✅ 保存: " + j.filename;
    loadCsvList();
  } else {
    msg.textContent = "❌ 失敗";
  }
});

document.getElementById('pdfForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const msg = document.getElementById('pdfMsg');
  msg.textContent = "⏳ 生成中# CODE_TRUNCATED";
  const fd = new FormData(e.target);
  const r = await fetch('/pdf', { method: 'POST', body: fd, redirect: 'follow' });
  if (r.redirected) {
    msg.innerHTML = "✅ <a class='text-blue-600 underline' target='_blank' href='" + r.url + "'>PDFプレビューを開く</a>";
    window.open(r.url, '_blank');
  } else {
    try {
      const j = await r.json();
      msg.textContent = "❌ 失敗: " + (j.error || r.status);
    } catch {
      msg.textContent = "❌ 失敗: " + r.status;
    }
  }
});
</script>
</body>
</html>
"@
[IO.File]::WriteAllText($Html, $Page, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "✅ index.html 再生成: $Html" -ForegroundColor Green