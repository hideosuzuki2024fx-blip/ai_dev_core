import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox


def run_tool():
    input_dir = input_dir_var.get().strip()
    pattern = pattern_var.get().strip() or "*.mp4"
    output_path = output_var.get().strip()

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
    analyzer = os.path.join(script_dir, "analyze_and_concat.py")

    if not os.path.isfile(analyzer):
        messagebox.showerror("エラー", f"analyze_and_concat.py が見つかりません:\\n{analyzer}")
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

    text_log.delete("1.0", tk.END)
    text_log.insert(tk.END, "コマンド実行中:\n" + " ".join(args) + "\n\n")
    root.update_idletasks()

    try:
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except Exception as e:
        messagebox.showerror("エラー", f"実行に失敗しました:\\n{e}")
        return

    text_log.insert(tk.END, proc.stdout)

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

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

# 入力ディレクトリ
tk.Label(frame, text="入力ディレクトリ:").grid(row=0, column=0, sticky="w")
tk.Entry(frame, textvariable=input_dir_var, width=50).grid(row=0, column=1, sticky="we")
tk.Button(frame, text="参照...", command=browse_input).grid(row=0, column=2, padx=(5, 0))

# パターン
tk.Label(frame, text="ファイルパターン:").grid(row=1, column=0, sticky="w")
tk.Entry(frame, textvariable=pattern_var, width=20).grid(row=1, column=1, sticky="w")

# 出力ファイル
tk.Label(frame, text="出力ファイル:").grid(row=2, column=0, sticky="w")
tk.Entry(frame, textvariable=output_var, width=50).grid(row=2, column=1, sticky="we")
tk.Button(frame, text="参照...", command=browse_output).grid(row=2, column=2, padx=(5, 0))

# オプション
opt_frame = tk.Frame(frame)
opt_frame.grid(row=3, column=0, columnspan=3, pady=(5, 5), sticky="w")
tk.Checkbutton(opt_frame, text="サブディレクトリも含める (recursive)", variable=recursive_var).pack(side=tk.LEFT)
tk.Checkbutton(opt_frame, text="Dry run (連結を実行しない)", variable=dryrun_var).pack(side=tk.LEFT, padx=(10, 0))

# 実行ボタン
tk.Button(frame, text="実行", command=run_tool).grid(row=4, column=0, columnspan=3, pady=(5, 5))

# ログ表示
text_log = tk.Text(frame, height=15, width=80)
text_log.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(5, 0))

frame.columnconfigure(1, weight=1)
frame.rowconfigure(5, weight=1)

root.mainloop()
