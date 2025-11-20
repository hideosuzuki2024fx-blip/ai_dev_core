from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import analyze_and_concat_v3 as v3

FFMPEG_CMD = "ffmpeg"


class SmartVideoConcatV3GUI(tk.Tk):
    """
    smart_video_concat v3 専用の簡易 GUI。

    - 複数 mp4 を選択（v3 のロジックで自動連結順を推定）
    - CRF / preset / width / height を指定
    - v3 と同等のフィルタ:
        scale=WIDTH:HEIGHT:force_original_aspect_ratio=decrease,
        pad=WIDTH:HEIGHT:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p
      で 1 本の mp4 を生成します。

    注意:
    - 連結順は v3 コア (analyze_and_concat_v3) の extract_features / build_order に従います。
      （ユーザーの追加順ではなく、推定順で連結します）
    - FFMPEG_CMD に ffmpeg がパス通っている前提です。
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("smart_video_concat v3 GUI")
        self.geometry("780x520")

        self.file_listbox: tk.Listbox
        self.files: list[Path] = []

        self.output_path_var = tk.StringVar()
        self.crf_var = tk.StringVar(value="20")
        self.width_var = tk.StringVar(value="1920")
        self.height_var = tk.StringVar(value="1080")
        self.preset_var = tk.StringVar(value="veryfast")

        self.log_text: tk.Text

        self._build_ui()

    # ---------------- UI 構築 ----------------

    def _build_ui(self) -> None:
        # 上段: ファイルリスト & 操作ボタン
        frame_top = ttk.LabelFrame(self, text="入力ファイル（v3 ロジックで自動並び替え）")
        frame_top.pack(fill="both", expand=True, padx=10, pady=8)

        left = ttk.Frame(frame_top)
        left.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=8)

        scrollbar = ttk.Scrollbar(left, orient="vertical")
        self.file_listbox = tk.Listbox(
            left,
            selectmode="extended",
            yscrollcommand=scrollbar.set,
            height=10,
        )
        scrollbar.config(command=self.file_listbox.yview)

        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        right = ttk.Frame(frame_top)
        right.pack(side="left", fill="y", padx=(4, 8), pady=8)

        btn_add = ttk.Button(right, text="追加...", command=self.on_add_files)
        btn_remove = ttk.Button(right, text="選択削除", command=self.on_remove_selected)
        btn_clear = ttk.Button(right, text="全クリア", command=self.on_clear_files)
        btn_up = ttk.Button(right, text="表示順 上へ", command=self.on_move_up)
        btn_down = ttk.Button(right, text="表示順 下へ", command=self.on_move_down)

        for w in (btn_add, btn_remove, btn_clear, btn_up, btn_down):
            w.pack(fill="x", pady=2)

        # 中段: エンコード設定
        frame_mid = ttk.LabelFrame(self, text="エンコード設定（v3 相当）")
        frame_mid.pack(fill="x", padx=10, pady=4, ipady=4)

        # CRF / preset / width / height
        grid = ttk.Frame(frame_mid)
        grid.pack(fill="x", padx=8, pady=4)

        # CRF
        ttk.Label(grid, text="CRF").grid(row=0, column=0, sticky="w", padx=2, pady=2)
        crf_entry = ttk.Entry(grid, textvariable=self.crf_var, width=8)
        crf_entry.grid(row=0, column=1, sticky="w", padx=2, pady=2)

        # preset
        ttk.Label(grid, text="preset").grid(row=0, column=2, sticky="w", padx=12, pady=2)
        preset_combo = ttk.Combobox(
            grid,
            textvariable=self.preset_var,
            values=[
                "ultrafast",
                "superfast",
                "veryfast",
                "faster",
                "fast",
                "medium",
            ],
            width=12,
            state="readonly",
        )
        preset_combo.grid(row=0, column=3, sticky="w", padx=2, pady=2)
        preset_combo.current(2)  # veryfast

        # width
        ttk.Label(grid, text="幅 (width)").grid(row=1, column=0, sticky="w", padx=2, pady=2)
        width_entry = ttk.Entry(grid, textvariable=self.width_var, width=8)
        width_entry.grid(row=1, column=1, sticky="w", padx=2, pady=2)

        # height
        ttk.Label(grid, text="高さ (height)").grid(row=1, column=2, sticky="w", padx=12, pady=2)
        height_entry = ttk.Entry(grid, textvariable=self.height_var, width=8)
        height_entry.grid(row=1, column=3, sticky="w", padx=2, pady=2)

        # 出力パス
        frame_out = ttk.Frame(frame_mid)
        frame_out.pack(fill="x", padx=8, pady=(2, 6))

        ttk.Label(frame_out, text="出力ファイル").pack(side="left")
        entry_out = ttk.Entry(frame_out, textvariable=self.output_path_var)
        entry_out.pack(side="left", fill="x", expand=True, padx=6)
        btn_out = ttk.Button(frame_out, text="参照...", command=self.on_browse_output)
        btn_out.pack(side="left")

        # 下段: 実行ボタン & ログ
        frame_bottom = ttk.Frame(self)
        frame_bottom.pack(fill="both", expand=False, padx=10, pady=(4, 10))

        btn_run = ttk.Button(
            frame_bottom,
            text="v3 ロジックで連結を実行",
            command=self.on_run_concat,
        )
        btn_run.pack(side="top", pady=(0, 6), anchor="e")

        self.log_text = tk.Text(
            frame_bottom,
            height=8,
            wrap="word",
        )
        self.log_text.pack(fill="both", expand=True)
        self._log("smart_video_concat v3 GUI を起動しました。")
        self._log("連結順は v3 コアのロジックで自動決定されます。")

    # ---------------- ファイルリスト操作 ----------------

    def _refresh_listbox(self) -> None:
        self.file_listbox.delete(0, tk.END)
        for p in self.files:
            self.file_listbox.insert(tk.END, str(p))

    def on_add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="連結候補の mp4 ファイルを選択",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
        )
        if not paths:
            return
        for p in paths:
            path_obj = Path(p)
            if path_obj.is_file():
                self.files.append(path_obj)
        self._refresh_listbox()
        self._log(f"{len(paths)} 個のファイルを追加しました。")

        # 出力ファイル未設定なら、最初のファイルのディレクトリに default 名で設定
        if self.files and not self.output_path_var.get():
            first_dir = self.files[0].parent
            default_out = first_dir / "smart_concat_v3_gui.mp4"
            self.output_path_var.set(str(default_out))

    def on_remove_selected(self) -> None:
        selection = list(self.file_listbox.curselection())
        if not selection:
            return
        # 後ろから消す
        for idx in reversed(selection):
            if 0 <= idx < len(self.files):
                self.files.pop(idx)
        self._refresh_listbox()
        self._log("選択中のファイルを削除しました。")

    def on_clear_files(self) -> None:
        if not self.files:
            return
        self.files.clear()
        self._refresh_listbox()
        self._log("ファイル一覧をクリアしました。")

    def on_move_up(self) -> None:
        selection = list(self.file_listbox.curselection())
        if not selection:
            return
        for idx in selection:
            if idx <= 0:
                continue
            self.files[idx - 1], self.files[idx] = self.files[idx], self.files[idx - 1]
        self._refresh_listbox()
        # 再選択
        self.file_listbox.selection_clear(0, tk.END)
        for idx in [max(i - 1, 0) for i in selection]:
            self.file_listbox.selection_set(idx)

    def on_move_down(self) -> None:
        selection = list(self.file_listbox.curselection())
        if not selection:
            return
        for idx in reversed(selection):
            if idx >= len(self.files) - 1:
                continue
            self.files[idx + 1], self.files[idx] = self.files[idx], self.files[idx + 1]
        self._refresh_listbox()
        # 再選択
        self.file_listbox.selection_clear(0, tk.END)
        for idx in [min(i + 1, len(self.files) - 1) for i in selection]:
            self.file_listbox.selection_set(idx)

    # ---------------- 出力パス選択 ----------------

    def on_browse_output(self) -> None:
        initialdir = None
        if self.files:
            initialdir = str(self.files[0].parent)

        path = filedialog.asksaveasfilename(
            title="出力 mp4 ファイルを指定",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            initialdir=initialdir,
            initialfile="smart_concat_v3_gui.mp4",
        )
        if path:
            self.output_path_var.set(path)

    # ---------------- 実行ロジック ----------------

    def on_run_concat(self) -> None:
        if not self.files:
            messagebox.showwarning("警告", "連結候補の mp4 ファイルを 1 つ以上追加してください。")
            return

        output_str = self.output_path_var.get().strip()
        if not output_str:
            messagebox.showwarning("警告", "出力ファイルを指定してください。")
            return

        try:
            crf = int(self.crf_var.get().strip())
        except ValueError:
            messagebox.showwarning("警告", "CRF には整数値を入力してください。")
            return

        try:
            width = int(self.width_var.get().strip())
            height = int(self.height_var.get().strip())
        except ValueError:
            messagebox.showwarning("警告", "幅・高さには整数値を入力してください。")
            return

        preset = self.preset_var.get().strip() or "veryfast"

        output_path = Path(output_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._log("連結処理を開始します...")
        self._log(f"- 入力ファイル数: {len(self.files)}")
        self._log(f"- 出力: {output_path}")
        self._log(f"- CRF: {crf}, preset: {preset}, size: {width}x{height}")
        self._log("v3 コアのロジックで連結順を自動推定します。")

        # v3 と同じロジックで自動連結順を決定
        ordered_files = self._auto_order_v3(self.files)

        self._run_ffmpeg_concat(ordered_files, output_path, crf, preset, width, height)

    def _auto_order_v3(self, input_paths: list[Path]) -> list[Path]:
        """
        analyze_and_concat_v3 の extract_features / build_order を使って
        連結順を推定します。
        """
        features: list[dict] = []
        self._log("特徴抽出と順序推定を開始します (v3)...")
        for p in input_paths:
            self._log(f"特徴抽出 (GUI v3): {p}")
            start_feat, end_feat = v3.extract_features(str(p))
            features.append({"path": p, "start": start_feat, "end": end_feat})

        order = v3.build_order(features)
        ordered = [features[i]["path"] for i in order]

        self._log("推定された連結順 (先頭 -> 末尾):")
        for idx, p in enumerate(ordered, start=1):
            self._log(f"{idx:2d}. {p}")

        return ordered

    def _run_ffmpeg_concat(
        self,
        input_paths: list[Path],
        output_path: Path,
        crf: int,
        preset: str,
        width: int,
        height: int,
    ) -> None:
        # 一時ディレクトリを作成
        tmp_dir = Path(tempfile.mkdtemp(prefix="svc_v3_gui_"))
        concat_path = tmp_dir / "concat_list_v3.txt"

        # concat list を作成
        with concat_path.open("w", encoding="utf-8") as f:
            for p in input_paths:
                # ffmpeg concat 用に POSIX パスで書き出し & ' をエスケープ
                posix = p.as_posix().replace("'", "''")
                f.write(f"file '{posix}'\n")

        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p"
        )

        cmd = [
            FFMPEG_CMD,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-c:a",
            "copy",
            str(output_path),
        ]

        self._log("ffmpeg コマンド:")
        self._log(" ".join(cmd))

        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError:
            self._log("エラー: ffmpeg コマンドが見つかりません。PATH 設定を確認してください。", error=True)
            messagebox.showerror("エラー", "ffmpeg が見つかりませんでした。PATH の設定を確認してください。")
            return

        if proc.returncode != 0:
            self._log("ffmpeg の実行に失敗しました。", error=True)
            self._log(proc.stdout)
            self._log(proc.stderr)
            messagebox.showerror(
                "エラー",
                "ffmpeg の実行に失敗しました。ログを確認してください。",
            )
            return

        self._log("ffmpeg の実行が正常に完了しました。")
        self._log(proc.stdout)
        self._log(proc.stderr)
        messagebox.showinfo("完了", f"連結が完了しました。\n\n出力: {output_path}")

    # ---------------- ログ出力 ----------------

    def _log(self, msg: str, error: bool = False) -> None:
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        if error:
            # とりあえずメッセージ内容で区別
            pass


def main() -> None:
    app = SmartVideoConcatV3GUI()
    app.mainloop()


if __name__ == "__main__":
    main()
