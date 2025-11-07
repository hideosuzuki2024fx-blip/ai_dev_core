from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import csv
from typing import Iterable
from weasyprint import HTML

# NOTE: パスの決定は実行環境に依存させず、リポジトリの実際の配置から解決する


def _iter_candidates(start: Path) -> Iterable[Path]:
    """親ディレクトリを含む候補パスを近い順に列挙する。"""

    yield start
    yield from start.parents


def _detect_project_root() -> Path:
    """リポジトリのルートディレクトリを動的に検出する。

    1. `AI_DEV_CORE_ROOT` or `PROJECT_ROOT` で明示指定されたパスを優先
    2. 指定がない場合は main.py から親ディレクトリを辿り、マーカーで特定
    3. マーカーが無ければ `src/backend` の親をフォールバックとして返す
    """

    env_candidates = [os.environ.get("AI_DEV_CORE_ROOT"), os.environ.get("PROJECT_ROOT")]
    for env in env_candidates:
        if not env:
            continue
        candidate = Path(env).expanduser().resolve()
        if candidate.is_dir():
            return candidate

    markers = ("START_HERE.md", "requirements.txt", ".git")
    # main.py が格納されているディレクトリから探索する
    current = Path(__file__).resolve().parent

    for candidate in _iter_candidates(current):
        if all((candidate / marker).exists() for marker in markers):
            return candidate

    # 何らかの理由でマーカーが見つからない場合は src/backend の親ディレクトリを返す
    return current


ROOT = _detect_project_root()
OUTPUTS = ROOT / "outputs"
STATIC = ROOT / "src" / "static"

OUTPUTS.mkdir(parents=True, exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
app.mount("/files", StaticFiles(directory=str(OUTPUTS)), name="files")

@app.post("/csv")
async def create_csv(title: str = Form(...), captions: str = Form("")):
    """
    captions 例:
      caption,text
      朝の光,海岸線の夜明け
      夕凪,オレンジの反射
    """
    filename = f"{title.replace(' ', '_')}.csv"
    csv_path = OUTPUTS / filename

    rows = []
    # 先頭行にヘッダが無い場合でも安全に生成できるようにする
    lines = [l for l in captions.splitlines() if l.strip()]
    if lines and "caption" in lines[0].lower() and "text" in lines[0].lower():
        body = lines[1:]
    else:
        # ヘッダを自動付与
        body = lines

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["caption", "text"])
        for line in body:
            if "," in line:
                k, v = line.split(",", 1)
                writer.writerow([k.strip(), v.strip()])
            else:
                # カンマが無ければ caption のみとして保存
                writer.writerow([line.strip(), ""])

    return {"ok": True, "filename": filename}

@app.get("/list_csv")
async def list_csv():
    items = [f.name for f in OUTPUTS.glob("*.csv")]
    return {"ok": True, "items": items}

@app.post("/pdf")
async def create_pdf(
    title: str = Form(...),
    csv_name: str = Form(...),
    files: list[UploadFile] = None
):
    csv_path = OUTPUTS / csv_name
    if not csv_path.exists():
        return JSONResponse({"ok": False, "error": "CSVが存在しません"}, status_code=400)
    if not files:
        return JSONResponse({"ok": False, "error": "画像がありません"}, status_code=400)

    # CSVは caption と text を結合して1つのキャプションに
    caps: list[str] = []
    with open(csv_path, encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            c = (row.get("caption") or "").strip()
            t = (row.get("text") or "").strip()
            merged = (f"{c} — {t}" if c and t else c or t).strip()
            caps.append(merged)

    # 画像を outputs に保存
    img_paths = []
    for img in files:
        out = OUTPUTS / img.filename
        out.write_bytes(await img.read())
        img_paths.append(out)

    # CSS: 画像+キャプションを同一ページに固定
    base_css = """
      <style>
        @page { margin: 24pt; }
        .page { page-break-after: always; break-inside: avoid; }
        figure { margin: 0; break-inside: avoid; }
        img.photo { width: 100%; height: auto; max-height: 85vh; }
        h1 { font-size: 42pt; text-align: center; margin-top: 200pt; }
        h2.caption { font-size: 16pt; text-align: center; margin-top: 10pt; }
      </style>
    """

    parts = []
    # 表紙
    parts.append(f'<div class="page"><h1>{title}</h1></div>')

    # 本文（必ず画像とキャプションを同じページに）
    for idx, p in enumerate(img_paths):
        cap = caps[idx] if idx < len(caps) else ""
        parts.append(f'''
        <div class="page">
          <figure>
            <img class="photo" src="{p.as_posix()}" />
            <figcaption><h2 class="caption">{cap}</h2></figcaption>
          </figure>
        </div>
        ''')

    html = f"<html><head>{base_css}</head><body>{''.join(parts)}</body></html>"
    pdf_name = f"{title.replace(' ', '_')}.pdf"
    pdf_path = OUTPUTS / pdf_name
    HTML(string=html).write_pdf(str(pdf_path))
    return RedirectResponse(url=f"/preview?file={pdf_name}", status_code=303)

@app.get("/preview")
async def preview(file: str):
    pdf_path = OUTPUTS / file
    return FileResponse(pdf_path, media_type="application/pdf")
