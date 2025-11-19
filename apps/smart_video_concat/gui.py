import os
import sys
import subprocess
import locale
import tkinter as tk
from tkinter import filedialog, messagebox


def run_tool():
    input_dir = input_dir_var.get().strip()
    pattern = pattern_var.get().strip() or "*.mp4"
    output_path = output_var.get().strip()
    mode = mode_var.get()

    if not input_dir:
        messagebox.showerror("エラー", "入力ディレクトリを指定してください。")
        return
    if not os.path.isdir(input_dir):
        messagebox.showerror("エラー", f"入力ディレクトリが存在しません:\\n{input_dir}")
        return
    if not output_path:
        output_path = os.path.join(input_dir, "smart_concat_gui.mp4")
        output_var.set(output_path)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    if mode == "v2":
        analyzer_name = "analyze_and_concat_v2.py"
    elif mode == "v3":
        analyzer_name = "analyze_and_concat_v3.py"
    else:
        analyzer_name = "analyze_and_concat.py"

    analyzer = os.path.join(script_dir, analyzer_name)

    if not os.path.isfile(analyzer):
        messagebox.showerror("エラー", f"{analyzer_name} が見つかりません:\\n{analyzer}")
        return

    args = [
        sys.executable,
        analyzer,
        "--input-dir", input_dir,
        "--pattern", pattern,
        "--output", output_path,
    ]
    if recursive_var.get():
        args.append("--recursive")
    if dryrun_var.get():
        args.append("--dry-run")

    # v2 / v3 の場合だけ CRF / preset を渡す
    if mode in ("v2", "v3"):
        crf_str = crf_var.get().strip()
        preset_str = preset_var.get().strip()
        if crf_str:
            args.extend(["--crf", crf_str])
        if preset_str:
            args.extend(["--preset", preset_str])

    text_log.delete("1.0", tk.END)

    if mode == "v1":
        mode_label = "v1 (copy)"
    elif mode == "v2":
        mode_label = "v2 (reencode)"
    elif mode == "v3":
        mode_label = "v3 (reencode + 16:9)"
    else:
        mode_label = mode

    text_log.insert(tk.END, f"モード: {mode_label}\\n")
    text_log.insert(tk.END, "コマンド実行中:\\n" + " ".join(args) + "\\n\\n")
    root.update_idletasks()

    try:
        # バイト列として取得して、後で安全にデコードする
        proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
    except Exception as e:
        messagebox.showerror("エラー", f"実行に失敗しました:\\n{e}")
        return

    # ロケールのエンコーディングでデコードし、失敗する部分は置き換え
    encoding = locale.getpreferredencoding(False) or "utf-8"
    try:
        output_text = proc.stdout.decode(encoding, errors="replace")
    except Exception as e:
        output_text = f"ログのデコード中にエラーが発生しました: {e}\\n"

    text_log.insert(tk.END, output_text)

    if proc.returncode == 0:
        messagebox.showinfo("完了", "処理が完了しました。")
    else:
        messagebox.showerror("エラー", f"処理がエラー終了しました (exit code={proc.returncode})。")


def browse_input():
    initial = input_dir_var.get().strip() or os.getcwd()
    d = filedialog.askdirectory(initialdir=initial)
    if d:
        input_dir_var.set(d)


def browse_output():
    initialdir = input_dir_var.get().strip() or os.getcwd()
    path = filedialog.asksaveasfilename(
        initialdir=initialdir,
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if path:
        output_var.set(path)


root = tk.Tk()
root.title("Smart Video Concat")

input_dir_var = tk.StringVar()
pattern_var = tk.StringVar(value="*.mp4")
output_var = tk.StringVar()
recursive_var = tk.BooleanVar(value=False)
dryrun_var = tk.BooleanVar(value=False)
mode_var = tk.StringVar(value="v1")  # "v1" / "v2" / "v3"
crf_var = tk.StringVar(value="20")
preset_var = tk.StringVar(value="veryfast")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

row = 0

# モード選択 (v1 / v2 / v3)
tk.Label(frame, text="モード:").grid(row=row, column=0, sticky="w")
mode_frame = tk.Frame(frame)
mode_frame.grid(row=row, column=1, columnspan=2, sticky="w")
tk.Radiobutton(mode_frame, text="v1 (高速 / 非再エンコード)", variable=mode_var, value="v1").pack(side=tk.LEFT)
tk.Radiobutton(mode_frame, text="v2 (再エンコード / 互換性重視)", variable=mode_var, value="v2").pack(side=tk.LEFT, padx=(10, 0))
tk.Radiobutton(mode_frame, text="v3 (再エンコード + 16:9 正規化)", variable=mode_var, value="v3").pack(side=tk.LEFT, padx=(10, 0))

row += 1

# 入力ディレクトリ
tk.Label(frame, text="入力ディレクトリ:").grid(row=row, column=0, sticky="w")
tk.Entry(frame, textvariable=input_dir_var, width=50).grid(row=row, column=1, sticky="we")
tk.Button(frame, text="参照.", command=browse_input).grid(row=row, column=2, padx=(5, 0))

row += 1

# パターン
tk.Label(frame, text="ファイルパターン:").grid(row=row, column=0, sticky="w")
tk.Entry(frame, textvariable=pattern_var, width=20).grid(row=row, column=1, sticky="w")

row += 1

# 出力ファイル
tk.Label(frame, text="出力ファイル:").grid(row=row, column=0, sticky="w")
tk.Entry(frame, textvariable=output_var, width=50).grid(row=row, column=1, sticky="we")
tk.Button(frame, text="参照.", command=browse_output).grid(row=row, column=2, padx=(5, 0))

row += 1

# オプション
opt_frame = tk.Frame(frame)
opt_frame.grid(row=row, column=0, columnspan=3, pady=(5, 5), sticky="w")
tk.Checkbutton(opt_frame, text="サブディレクトリも含める (recursive)", variable=recursive_var).pack(side=tk.LEFT)
tk.Checkbutton(opt_frame, text="Dry run (連結を実行しない)", variable=dryrun_var).pack(side=tk.LEFT, padx=(10, 0))

row += 1

# v2 / v3 用 CRF / preset
crf_frame = tk.Frame(frame)
crf_frame.grid(row=row, column=0, columnspan=3, pady=(5, 5), sticky="w")
tk.Label(crf_frame, text="v2/v3 用 CRF:").pack(side=tk.LEFT)
tk.Entry(crf_frame, textvariable=crf_var, width=6).pack(side=tk.LEFT, padx=(2, 10))
tk.Label(crf_frame, text="preset:").pack(side=tk.LEFT)
tk.Entry(crf_frame, textvariable=preset_var, width=10).pack(side=tk.LEFT, padx=(2, 10))
tk.Label(crf_frame, text="(v1 モードでは無視されます)").pack(side=tk.LEFT)

row += 1

# 実行ボタン
tk.Button(frame, text="実行", command=run_tool).grid(row=row, column=0, columnspan=3, pady=(5, 5))

row += 1

# ログ表示
text_log = tk.Text(frame, height=15, width=80)
text_log.grid(row=row, column=0, columnspan=3, sticky="nsew", pady=(5, 0))

frame.columnconfigure(1, weight=1)
frame.rowconfigure(row, weight=1)

root.mainloop()
