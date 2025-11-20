from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import analyze_and_concat_v3 as v3

FFMPEG_CMD = "ffmpeg"
TRANSITION_CLIP_NAME = "transition_black_1s.mp4"


class SmartVideoConcatV3GUI(tk.Tk):
    """
    smart_video_concat v3 専用の簡易 GUI。

    フロー:
      1. ファイルを追加（追加順で一覧表示）
      2. 「自動並び替え (v3 推奨順)」ボタンで、v3 ロジックに基づく推奨順に並び替え
      3. 必要に応じて「上へ」「下へ」で手動微調整
      4. 必要に応じて「選択の後に黒トランジション」を押して、黒 1 秒クリップを挿入したい境界を指定
      5. 「連結を実行」で、画面リストに表示されている順とトランジション指定に従って ffmpeg で連結

    ポイント:
      - 自動並び替えはユーザー操作時のみ実行されます。
      - 連結時には自動並び替えは行わず、「現在リストに見えている順 = 連結順」です。
      - トランジションは「選択したクリップの直後」に黒 1 秒クリップとして挿入されます。
      - トランジションクリップ自体は、必要になったときに ffmpeg で自動生成します。
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("smart_video_concat v3 GUI")
        self.geometry("820x600")

        self.file_listbox: tk.Listbox
        self.files: list[Path] = []

        # どのクリップの「直後」にトランジションを挿入するかを 0 始まりインデックスで保持
        # 例: {0, 2} なら 1 本目の後と 3 本目の後にトランジション
        self.transition_after_indices: set[int] = set()

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
        frame_top = ttk.LabelFrame(self, text="入力ファイル一覧（現在の表示順 = 連結順）")
        frame_top.pack(fill="both", expand=True, padx=10, pady=8)

        left = ttk.Frame(frame_top)
        left.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=8)

        scrollbar = ttk.Scrollbar(left, orient="vertical")
        self.file_listbox = tk.Listbox(
            left,
            selectmode="extended",
            yscrollcommand=scrollbar.set,
            height=12,
        )
        scrollbar.config(command=self.file_listbox.yview)

        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        right = ttk.Frame(frame_top)
        right.pack(side="left", fill="y", padx=(4, 8), pady=8)

        btn_add = ttk.Button(right, text="追加...", command=self.on_add_files)
        btn_remove = ttk.Button(right, text="選択削除", command=self.on_remove_selected)
        btn_clear = ttk.Button(right, text="全クリア", command=self.on_clear_files)
        btn_up = ttk.Button(right, text="上へ (表示順)", command=self.on_move_up)
        btn_down = ttk.Button(right, text="下へ (表示順)", command=self.on_move_down)

        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=4)

        btn_auto_tr = ttk.Button(
            right,
            text="選択の後に\n黒トランジション",
            command=self.on_add_transition_after_selected,
        )
        btn_clear_tr = ttk.Button(
            right,
            text="トランジション\n全クリア",
            command=self.on_clear_transitions,
        )

        for w in (btn_add, btn_remove, btn_clear, btn_up, btn_down, btn_auto_tr, btn_clear_tr):
            w.pack(fill="x", pady=2)

        # 中段: エンコード設定
        frame_mid = ttk.LabelFrame(self, text="エンコード設定（v3 相当）")
        frame_mid.pack(fill="x", padx=10, pady=4, ipady=4)

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

        # 下段: 自動並び替えボタン & 実行ボタン & ログ
        frame_bottom = ttk.Frame(self)
        frame_bottom.pack(fill="both", expand=False, padx=10, pady=(4, 10))

        btn_row = ttk.Frame(frame_bottom)
        btn_row.pack(fill="x", pady=(0, 6))

        btn_auto_order = ttk.Button(
            btn_row,
            text="自動並び替え (v3 推奨順)",
            command=self.on_auto_order_v3,
        )
        btn_auto_order.pack(side="left")

        btn_run = ttk.Button(
            btn_row,
            text="連結を実行（表示順のまま）",
            command=self.on_run_concat,
        )
        btn_run.pack(side="right")

        self.log_text = tk.Text(
            frame_bottom,
            height=10,
            wrap="word",
        )
        self.log_text.pack(fill="both", expand=True)
        self._log("smart_video_concat v3 GUI を起動しました。")
        self._log("現在リストに表示されている順番が、そのまま連結順になります。")
        self._log("必要に応じて「自動並び替え (v3 推奨順)」とトランジション指定を使ってください。")

    # ---------------- ファイルリスト操作 ----------------

    def _refresh_listbox(self) -> None:
        self.file_listbox.delete(0, tk.END)
        for p in self.files:
            self.file_listbox.insert(tk.END, str(p))

    def _invalidate_transitions_due_to_reorder(self) -> None:
        """
        順序が大きく変わる操作をしたときに、インデックスずれを避けるため
        トランジション指定をリセットする。
        """
        if self.transition_after_indices:
            self.transition_after_indices.clear()
            self._log("ファイル順が変更されたため、トランジション指定をリセットしました。")

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
        for idx in reversed(selection):
            if 0 <= idx < len(self.files):
                self.files.pop(idx)
        self._refresh_listbox()
        self._invalidate_transitions_due_to_reorder()
        self._log("選択中のファイルを削除しました。")

    def on_clear_files(self) -> None:
        if not self.files:
            return
        self.files.clear()
        self._refresh_listbox()
        self.transition_after_indices.clear()
        self._log("ファイル一覧およびトランジション指定をクリアしました。")

    def on_move_up(self) -> None:
        selection = list(self.file_listbox.curselection())
        if not selection:
            return
        for idx in selection:
            if idx <= 0:
                continue
            self.files[idx - 1], self.files[idx] = self.files[idx], self.files[idx - 1]
        self._refresh_listbox()
        self.file_listbox.selection_clear(0, tk.END)
        for idx in [max(i - 1, 0) for i in selection]:
            self.file_listbox.selection_set(idx)
        self._invalidate_transitions_due_to_reorder()

    def on_move_down(self) -> None:
        selection = list(self.file_listbox.curselection())
        if not selection:
            return
        for idx in reversed(selection):
            if idx >= len(self.files) - 1:
                continue
            self.files[idx + 1], self.files[idx] = self.files[idx], self.files[idx + 1]
        self._refresh_listbox()
        self.file_listbox.selection_clear(0, tk.END)
        for idx in [min(i + 1, len(self.files) - 1) for i in selection]:
            self.file_listbox.selection_set(idx)
        self._invalidate_transitions_due_to_reorder()

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

    # ---------------- 自動並び替え (v3 ロジック) ----------------

    def on_auto_order_v3(self) -> None:
        """
        v3 のロジック (analyze_and_concat_v3) を使って自動並び替えを行い、
        self.files を「推奨順」に更新します。
        """
        if not self.files:
            messagebox.showwarning("警告", "自動並び替えの対象となるファイルがありません。")
            return

        ordered_files = self._auto_order_v3(self.files)
        self.files = ordered_files
        self._refresh_listbox()
        self._invalidate_transitions_due_to_reorder()
        self._log("自動並び替え (v3 推奨順) を適用しました。")
        self._log("必要であれば「上へ」「下へ」で微調整してから、トランジションを指定して連結を実行してください。")

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

    # ---------------- トランジション指定 ----------------

    def on_add_transition_after_selected(self) -> None:
        """
        選択されている行の「直後」に黒 1 秒トランジションを挿入する指定を追加します。
        実際の挿入は _run_ffmpeg_concat 内で concat_list を書く際に行います。
        """
        if not self.files:
            messagebox.showwarning("警告", "トランジションを挿入する前にファイルを追加してください。")
            return

        selection = list(self.file_listbox.curselection())
        if not selection:
            messagebox.showwarning("警告", "トランジションを挿入する位置として、少なくとも 1 行選択してください。")
            return

        for idx in selection:
            if 0 <= idx < len(self.files):
                self.transition_after_indices.add(idx)

        self._log("以下の位置に黒トランジションを挿入します（クリップ番号は 1 始まり）:")
        for idx in sorted(self.transition_after_indices):
            if idx < len(self.files):
                self._log(f" - {idx + 1} 番目のクリップの直後")

    def on_clear_transitions(self) -> None:
        if not self.transition_after_indices:
            return
        self.transition_after_indices.clear()
        self._log("トランジション指定をすべてクリアしました。")

    # ---------------- 実行ロジック ----------------

    def on_run_concat(self) -> None:
        """
        現在リストに表示されている順番 (self.files) のまま連結します。
        自動並び替えはここでは行わず、必要なら事前に on_auto_order_v3 を使います。
        """
        if not self.files:
            messagebox.showwarning("警告", "連結する mp4 ファイルを 1 つ以上追加してください。")
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
        if self.transition_after_indices:
            indices_str = ", ".join(str(i + 1) for i in sorted(self.transition_after_indices) if i < len(self.files))
            self._log(f"- トランジション挿入位置 (クリップ番号基準): {indices_str}")
        else:
            self._log("- トランジション挿入位置: なし")

        ordered_files = list(self.files)
        self._run_ffmpeg_concat(ordered_files, output_path, crf, preset, width, height)

    def _ensure_transition_clip(self) -> Path | None:
        """
        黒 1 秒トランジションクリップを作成・または再利用します。
        - 解像度は 1920x1080 固定ですが、後段の scale/pad で出力解像度に揃えられます。
        """
        base_dir = Path(__file__).resolve().parent
        clip_path = base_dir / TRANSITION_CLIP_NAME

        if clip_path.exists():
            return clip_path

        self._log("トランジションクリップが存在しないため、新規作成します。")
        cmd = [
            FFMPEG_CMD,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=1920x1080:d=1",
            "-r",
            "30",
            "-pix_fmt",
            "yuv420p",
            str(clip_path),
        ]
        self._log("トランジションクリップ作成 ffmpeg コマンド:")
        self._log(" ".join(cmd))

        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError:
            self._log("エラー: ffmpeg が見つからないためトランジションクリップを生成できません。", error=True)
            messagebox.showerror("エラー", "ffmpeg が見つからないためトランジションクリップを生成できませんでした。")
            return None

        if proc.returncode != 0:
            self._log("トランジションクリップ生成に失敗しました。", error=True)
            self._log(proc.stdout)
            self._log(proc.stderr)
            messagebox.showerror("エラー", "トランジションクリップ生成に失敗しました。ログを確認してください。")
            return None

        self._log(f"トランジションクリップを作成しました: {clip_path}")
        return clip_path

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

        # トランジションクリップの準備（必要なときだけ）
        transition_clip_path: Path | None = None
        if self.transition_after_indices:
            transition_clip_path = self._ensure_transition_clip()
            if transition_clip_path is None:
                self._log("トランジションクリップの準備に失敗したため、トランジションなしで連結します。", error=True)
                self.transition_after_indices.clear()

        # concat list を作成
        with concat_path.open("w", encoding="utf-8") as f:
            for idx, p in enumerate(input_paths):
                posix = p.as_posix().replace("'", "''")
                f.write(f"file '{posix}'\n")

                # トランジション指定があれば、その直後に黒クリップを挿入
                if transition_clip_path is not None and idx in self.transition_after_indices:
                    t_posix = transition_clip_path.as_posix().replace("'", "''")
                    f.write(f"file '{t_posix}'\n")

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
            # 必要であればここでスタイル変更なども可能
            pass


def main() -> None:
    app = SmartVideoConcatV3GUI()
    app.mainloop()


if __name__ == "__main__":
    main()
