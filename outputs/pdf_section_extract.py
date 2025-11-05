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
