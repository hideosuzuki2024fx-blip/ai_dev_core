"""Bootstrap a demo photobook PDF using the FastAPI backend in-process.

This script exercises the CSV and PDF endpoints to produce a tangible output
without requiring the operator to run the web server manually. It generates
sample captions, synthesises placeholder images, and saves the resulting PDF
under the standard `outputs/` directory.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from fastapi.testclient import TestClient

from src.backend.main import app, OUTPUTS


def _ensure_demo_assets(target: Path) -> list[Path]:
    """Create a couple of illustrative SVGs and return their paths."""

    target.mkdir(parents=True, exist_ok=True)
    colors = ["#2563eb", "#f97316"]
    captions = ["Sunrise over Tokyo Bay", "Neon night in Shibuya"]
    created: list[Path] = []

    template = """<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='800'>\n"""
    template += "    <rect width='100%' height='100%' fill='{color}'/>\n"
    template += "    <text x='50%' y='50%' fill='#ffffff' font-size='64' font-family='sans-serif' text-anchor='middle' dominant-baseline='middle'>{caption}</text>\n"
    template += "  </svg>\n"

    for idx, (color, caption) in enumerate(zip(colors, captions), start=1):
        out_path = target / f"demo_image_{idx}.svg"
        out_path.write_text(template.format(color=color, caption=caption), encoding="utf-8")
        created.append(out_path)

    return created


def _captions_csv_lines() -> Iterable[str]:
    """Yield CSV-friendly caption rows."""

    yield "caption,text"
    yield "朝焼けの海辺,水平線から顔を出す光を感じて"
    yield "ネオン街,都会の夜が動き出す瞬間"


def run_demo() -> Path:
    client = TestClient(app)

    caption_blob = "\n".join(_captions_csv_lines())
    csv_title = "demo_captions"
    csv_response = client.post(
        "/csv",
        data={"title": csv_title, "captions": caption_blob},
    )
    csv_response.raise_for_status()
    csv_payload = csv_response.json()
    if not csv_payload.get("ok"):
        raise RuntimeError(f"CSV generation failed: {csv_payload}")

    csv_name = csv_payload["filename"]

    demo_assets_dir = OUTPUTS / "demo_assets"
    image_paths = _ensure_demo_assets(demo_assets_dir)

    files = [
        (
            "files",
            (
                path.name,
                path.read_bytes(),
                "image/svg+xml",
            ),
        )
        for path in image_paths
    ]

    pdf_title = "Demo Photobook"
    pdf_response = client.post(
        "/pdf",
        data={"title": pdf_title, "csv_name": csv_name},
        files=files,
        allow_redirects=False,
    )

    if pdf_response.status_code != 303:
        try:
            detail = pdf_response.json()
        except Exception:  # noqa: BLE001 - fallback to raw body
            detail = pdf_response.text
        raise RuntimeError(f"PDF generation failed: {detail}")

    preview_url = pdf_response.headers.get("location", "")
    if not preview_url:
        raise RuntimeError("PDF preview URL missing from response")

    pdf_filename = preview_url.split("file=")[-1]
    pdf_path = OUTPUTS / pdf_filename
    if not pdf_path.exists():
        raise FileNotFoundError(f"Expected PDF was not created: {pdf_path}")

    return pdf_path


def main() -> None:
    pdf_path = run_demo()
    rel_path = pdf_path.relative_to(Path.cwd()) if pdf_path.is_relative_to(Path.cwd()) else pdf_path
    print("✅ Demo photobook generated:", rel_path)


if __name__ == "__main__":
    main()
