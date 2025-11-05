import os, csv, re, math
from collections import Counter, defaultdict
from datetime import datetime

ROOT = os.path.expanduser(os.path.join("~","Projects","ai_dev_core"))
IN_CSV = os.path.join(ROOT, "docs", "research", "market", "reviews_sample.csv")
OUT_MD = os.path.join(ROOT, "docs", "research", "market", "qualitative_summary.md")
OUT_PNG = os.path.join(ROOT, "docs", "research", "market", "positioning.png")

# カテゴリ用キーワード（日本語の素朴なルールベース）
CATEGORIES = {
    "usability": ["直感的","使いやすい","UX","UI","操作","反応","慣れる","迷わない","チュートリアル"],
    "quality": ["品質","綺麗","印刷","一貫性","顔認識","手が崩れる","崩れる","フィルタ","仕上がる"],
    "speed": ["速い","早い","書き出し","時間がかかる","反応が遅い"],
    "value": ["手頃","妥当","高め","割引","無料トライアル","お試し","サブスク","価格","年額","月額"],
    "features": ["テンプレ","コラージュ","プリセット","レイアウト","エクスポート","機能","ヘルプ"],
    "support": ["サポート","返金","返答","ヘルプ"],
}

POS_WORDS = ["良い","最適","便利","楽","綺麗","強い","丁寧","手頃","妥当","重宝","豊富","映え"]
NEG_WORDS = ["悪い","不快","遅い","遅かった","崩れる","難しい","できない","薄い","高い","高め","短い"]

def sentiment_score(text: str) -> float:
    t = text
    pos = sum(t.count(w) for w in POS_WORDS)
    neg = sum(t.count(w) for w in NEG_WORDS)
    # rating連動の緩和は別途（今回はレビューratingを併用）
    return pos - neg

def categorize(text: str):
    hit = set()
    for cat, words in CATEGORIES.items():
        for w in words:
            if w in text:
                hit.add(cat)
                break
    if not hit:
        hit.add("other")
    return list(hit)

def safe_mean(nums):
    arr = [x for x in nums if x is not None]
    return sum(arr)/len(arr) if arr else None

# 入力読み込み
rows = []
with open(IN_CSV, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        row["rating"] = float(row["rating"])
        row["sent"] = sentiment_score(row["text"])
        row["cats"] = categorize(row["text"])
        rows.append(row)

# app別集計
apps = sorted(set(r["app_name"] for r in rows))
app_stats = {}
for a in apps:
    sub = [r for r in rows if r["app_name"] == a]
    app_stats[a] = {
        "n": len(sub),
        "avg_rating": round(sum(r["rating"] for r in sub)/len(sub), 2),
        "avg_sent": round(sum(r["sent"] for r in sub)/len(sub), 2),
        "top_cats": Counter([c for r in sub for c in r["cats"]]).most_common(3)
    }

# カテゴリ別の感情傾向
cat_sent = defaultdict(list)
for r in rows:
    for c in r["cats"]:
        cat_sent[c].append(r["sent"])

cat_summary = {c: round(safe_mean(v) or 0.0, 2) for c, v in cat_sent.items()}

# 重要キーフレーズ（単純トークン頻度）
def tokenize(text):
    # 日本語簡易: 記号除去 → ひらがな/カタカナ/漢字/英数の連続を抽出
    return re.findall(r"[ぁ-んァ-ン一-龥a-zA-Z0-9]{2,}", text)

freq = Counter()
for r in rows:
    for t in tokenize(r["text"]):
        # ストップワードっぽい一般語を簡易除外
        if t in ["が","の","に","は","も","です","ます","する","できる","ある","ない","こと","と","ため","ために"]:
            continue
        freq[t] += 1

top_terms = freq.most_common(15)

# 図（avg_rating vs avg_sent）: matplotlibが無い場合はスキップ
plot_ok = False
try:
    import matplotlib.pyplot as plt
    xs = [app_stats[a]["avg_rating"] for a in apps]
    ys = [app_stats[a]["avg_sent"] for a in apps]
    plt.figure(figsize=(6,4.5))
    plt.scatter(xs, ys)
    for a, x, y in zip(apps, xs, ys):
        plt.text(x+0.02, y+0.02, a, fontsize=9)
    plt.xlabel("Average Rating")
    plt.ylabel("Average Sentiment (rule-based)")
    plt.title("Positioning: Rating vs Sentiment")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(OUT_PNG)
    plt.close()
    plot_ok = True
except Exception as e:
    plot_ok = False

# Markdown出力
lines = []
lines.append(f"# 🧠 定性マーケットリサーチ（A2）\n")
lines.append(f"- 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
lines.append("## 1. アプリ別サマリー\n")
lines.append("| App | Reviews | Avg Rating | Avg Sent | Top Categories |")
lines.append("|---|---:|---:|---:|---|")
for a in apps:
    cats = ", ".join([f"{k}({v})" for k,v in app_stats[a]["top_cats"]])
    lines.append(f"| {a} | {app_stats[a]['n']} | {app_stats[a]['avg_rating']} | {app_stats[a]['avg_sent']} | {cats} |")

lines.append("\n## 2. カテゴリ別 感情傾向（+正/−負）\n")
lines.append("| Category | Avg Sent |")
lines.append("|---|---:|")
for c, v in sorted(cat_summary.items(), key=lambda x: x[1], reverse=True):
    lines.append(f"| {c} | {v} |")

lines.append("\n## 3. キーフレーズ上位\n")
for term, cnt in top_terms:
    lines.append(f"- {term} ({cnt})")

if plot_ok:
    lines.append("\n## 4. ポジショニング図\n")
    lines.append(f"![positioning](./{os.path.basename(OUT_PNG)})\n")
else:
    lines.append("\n> 図の生成はスキップされました（matplotlib未導入）。`pip install matplotlib` 後に再実行で生成されます。\n")

os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"✅ qualitative_summary.md → {OUT_MD}")
if plot_ok:
    print(f"✅ positioning.png → {OUT_PNG}")