# -*- coding: utf-8 -*-
'''
generate_i18n_visual.py
LP Heroセクションの英日対応・画像生成
'''

from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

# Windowsのバックスラッシュ誤認防止
root = Path.home() / 'Projects' / 'ai_dev_core'
img_dir = root / 'docs' / 'product' / 'img'
i18n_dir = root / 'docs' / 'product' / 'i18n'
adr_dir = root / 'docs' / 'ADR'
img_dir.mkdir(parents=True, exist_ok=True)
i18n_dir.mkdir(parents=True, exist_ok=True)

# === 英日対訳定義 ===
i18n = {
    'EmotionCut': {
        'ja': {'title': 'EmotionCut', 'subtitle': '感情トリガーで切り抜きが1分で完成'},
        'en': {'title': 'EmotionCut', 'subtitle': 'Cut your highlights in 1 minute with emotion triggers'}
    },
    'TrendHook': {
        'ja': {'title': 'TrendHook', 'subtitle': '今、刺さる投稿をAIが提案'},
        'en': {'title': 'TrendHook', 'subtitle': 'AI suggests posts that hit the trend right now'}
    }
}

def make_hero(title: str, subtitle: str, filename: str):
    w, h = 1200, 675
    img = Image.new('RGB', (w, h), (25, 27, 35))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype('arial.ttf', 70)
        font_sub = ImageFont.truetype('arial.ttf', 36)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    draw.text((80, 200), title, fill=(255, 255, 255), font=font_title)
    draw.text((80, 300), subtitle, fill=(180, 180, 200), font=font_sub)
    img.save(img_dir / filename, quality=95)
    print(f'✅ Hero image generated: {filename}')

# === Hero画像英日生成 ===
for app, langs in i18n.items():
    for lang, data in langs.items():
        fname = f'hero_{app.lower()}_{lang}.jpg'
        make_hero(data['title'], data['subtitle'], fname)

# === JSON保存 ===
json_path = i18n_dir / 'hero_i18n_map.json'
json_path.write_text(json.dumps(i18n, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'✅ JSON written: {json_path.name}')

# === ADR生成 ===
adr_text = (
    "# ADR-0003: LP多言語化とHero画像生成方針\n\n"
    "## 背景\n"
    "- LPの国際展開を見据え、Heroテキスト・画像の英日2言語展開を標準化。\n"
    "- 今後、image_genを活用し自動ビジュアル差分（A/Bテスト）を行う。\n\n"
    "## 決定\n"
    "- Hero構成要素（タイトル・サブタイトル）をJSONで管理。\n"
    "- Pythonスクリプト generate_i18n_visual.py によりHero画像を英日両方自動生成。\n"
    "- 出力先:\n"
    "  - /docs/product/img/hero_<app>_<lang>.jpg\n"
    "  - /docs/product/i18n/hero_i18n_map.json\n\n"
    "## 実行手順\n"
    "PowerShell:\n"
    "    cd $HOME/Projects/ai_dev_core\n"
    "    python ops/scripts/generate_i18n_visual.py\n\n"
    "## 今後の展開\n"
    "- image_genツールでビジュアル差分を自動生成し、A/Bテスト指標（CTR・CVR）を記録。\n"
    "- 翻訳は固定文型からLLM出力補助へ移行可能。\n"
)
adr_path = adr_dir / 'ADR-0003_i18n_visual.md'
adr_path.write_text(adr_text, encoding='utf-8')
print(f'✅ ADR document created: {adr_path.name}')

print('🎯 Hero多言語展開と画像生成が完了しました。')