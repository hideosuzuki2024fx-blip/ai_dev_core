from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
import datetime, os

ROOT = os.path.expanduser("~/Projects/ai_dev_core/outputs")
os.makedirs(ROOT, exist_ok=True)

html_file = os.path.join(ROOT, "sample.html")
pdf_file = os.path.join(ROOT, "sample.pdf")

# HTML作成
with open(html_file, "w", encoding="utf-8") as f:
    f.write(f"""
    <html><head><meta charset='utf-8'><title>PDF Test</title></head>
    <body style='font-family:sans-serif;padding:40px;'>
      <h1>✅ WeasyPrint PDFテスト</h1>
      <p>生成日時: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}</p>
      <p>GTK・Pango・FontConfig統合確認。</p>
    </body></html>
    """)

# PDF生成
font_config = FontConfiguration()
HTML(html_file).write_pdf(pdf_file, font_config=font_config)

print(f"✅ PDF生成成功: {pdf_file}")