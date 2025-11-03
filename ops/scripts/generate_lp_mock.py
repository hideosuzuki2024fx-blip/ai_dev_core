# -*- coding: utf-8 -*-
"""
generate_lp_mock.py
EmotionCut / TrendHook の LP用 Hero画像とモック構成を生成
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path.home() / "Projects/ai_dev_core"
img_dir = root / "docs/product/img"
mock_dir = root / "docs/product/mock"
img_dir.mkdir(parents=True, exist_ok=True)
mock_dir.mkdir(parents=True, exist_ok=True)

def make_hero(title: str, subtitle: str, filename: str):
    w, h = 1200, 675
    img = Image.new("RGB", (w, h), (18, 22, 33))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 70)
        font_sub = ImageFont.truetype("arial.ttf", 36)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    draw.text((80, 200), title, fill=(255, 255, 255), font=font_title)
    draw.text((80, 300), subtitle, fill=(180, 180, 200), font=font_sub)
    img.save(img_dir / filename, quality=95)
    print(f"✅ Hero image saved: {filename}")

def make_mock_md(app: str, sections: list[str]):
    out_path = mock_dir / f"LP_{app}_mock.md"
    lines = [f"# LP構成モック ({app})", ""]
    for i, sec in enumerate(sections, 1):
        lines.append(f"## {i}. {sec}")
        lines.append(f"（ここに {sec} の要素配置予定）")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Mock markdown saved: {out_path.name}")

# EmotionCut
make_hero("EmotionCut", "感情トリガーで切り抜きが1分で完成", "hero_emotioncut.jpg")
make_mock_md("EmotionCut", ["Hero", "Problem", "Solution", "Demo", "Pricing", "FAQ"])

# TrendHook
make_hero("TrendHook", "今、刺さる投稿をAIが提案", "hero_trendhook.jpg")
make_mock_md("TrendHook", ["Hero", "Problem", "Solution", "Demo", "Pricing", "FAQ"])

print("🎯 すべてのLPモック生成が完了しました。")
